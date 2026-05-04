"""
search_product_es.py
====================
Hybrid Elasticsearch search for parapharmacie product matching.

Architecture (in order):
  1. RRF fusion of BM25 + kNN (or single hybrid query as fallback)
  2. Size hard-filter  — different volume = different product
  3. Brand hard-filter — extracted from text, no hardcoded lists
  4. Universal token-overlap filter — language-agnostic
  5. Cross-encoder rerank (optional, CPU-friendly)
  6. Dedup + price sort

Design principles:
  - Zero hardcoded brand / product-line names
  - Every filter is derived from the query itself at runtime
  - Prefer high recall (missing a listing is worse than including a near-match)
  - Deterministic: identical input → identical output
"""

from __future__ import annotations

import os
import re
import unicodedata
from typing import Optional

from elasticsearch import Elasticsearch

try:
    from rerank_cross_encoder import rerank_listings_with_cross_encoder
    _RERANK_AVAILABLE = True
except Exception:
    rerank_listings_with_cross_encoder = None
    _RERANK_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────
ES_URL       = "http://localhost:9200"
INDEX_NAME   = "parapharmacie"
# The fine-tuned e5 model is best for this index
EMBED_MODEL_NAME = "intfloat/multilingual-e5-large-instruct"

BM25_BOOST   = 2.0
VECTOR_BOOST = 1.0
RRF_K        = 60          # RRF rank constant (standard = 60)

# ── Lazy globals ──────────────────────────────────────────────────────────────
_es_client   = None
_embed_model = None


def _load_es():
    global _es_client
    if _es_client is not None:
        return
    _es_client = Elasticsearch(ES_URL)
    try:
        _es_client.info()
        print("[ES] Elasticsearch connected.")
    except Exception as e:
        print(f"[ES] Connection failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  TEXT UTILITIES  (no hardcoded domain knowledge)
# ══════════════════════════════════════════════════════════════════════════════

# Universal stopwords — function words only, no product descriptors
_SIZE_RE = re.compile(
    r"(?:^|(?<=[\s\-(\[,]))"
    r"e?\s*(\d+(?:[.,]\d+)?\s*"
    r"(?:mle?|ml|mg|mcg|g|gr|grs|kg|cl|l|oz|fl\.?oz\.?))\b"
    r"(?=[\s\-)\],]|$)",
    re.IGNORECASE,
)

def _get_size(text: str) -> Optional[str]:
    """Extract the first size/volume token (e.g. '200ml', '50g')."""
    if not text:
        return None
    m = _SIZE_RE.search(text)
    if not m:
        return None
    s = m.group(1).lower().replace(" ", "")
    if s.endswith("mle"):
        s = s[:-1]
    if s.endswith("gr"):
        s = s[:-1]
    return s


# ══════════════════════════════════════════════════════════════════════════════
#  ELASTICSEARCH HELPERS
# ══════════════════════════════════════════════════════════════════════════════

_ES_SOURCE = ["name", "source", "price", "link", "ean"]


def _parse_hits(resp: dict, q_size: Optional[str]) -> list[dict]:
    """Convert ES hits to row dicts. Pre-filter obvious size mismatches."""
    max_score = resp.get("hits", {}).get("max_score", 1.0) or 1.0
    rows = []
    for hit in resp.get("hits", {}).get("hits", []):
        src = hit.get("_source") or {}
        es_score = hit.get("_score") or 0.0
        # Fast size pre-filter before the more expensive token filter
        if q_size:
            r_size = _get_size(src.get("name", ""))
            if r_size and r_size != q_size:
                continue
        rows.append({
            "_id":         hit["_id"],
            "name":        src.get("name", ""),
            "source":      src.get("source", ""),
            "price":       src.get("price", ""),
            "link":        src.get("link", ""),
            "ean":         src.get("ean"),
            "match_score": round(float(es_score) / max_score, 4),
        })
    return rows


def _rrf_merge(rank_a: list[dict], rank_b: list[dict], k: int = RRF_K) -> list[dict]:
    """
    Standard Reciprocal Rank Fusion.
    score(d) = Σ  1 / (k + rank_i)
    """
    scores: dict[str, float] = {}
    best:   dict[str, dict]  = {}
    for ranked_list in (rank_a, rank_b):
        for rank, row in enumerate(ranked_list, start=1):
            did = str(row.get("_id") or row.get("link") or "")
            if not did:
                continue
            scores[did] = scores.get(did, 0.0) + 1.0 / (k + rank)
            if did not in best:
                best[did] = dict(row)
    if not scores:
        return []
    mx = max(scores.values())
    out = []
    for did in sorted(scores, key=scores.__getitem__, reverse=True):
        r = dict(best[did])
        r["match_score"] = round(scores[did] / mx, 4)
        out.append(r)
    return out


def _normalize_price_string(s: str) -> str:
    s = re.sub(r'[\u0600-\u06FF]+', '', s)
    s = re.sub(r'\b(DT|TND|dinar|dinars)\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^\d.,\s]', '', s).strip()
    if not s: return ''
    has_dot, has_comma = '.' in s, ',' in s
    if has_dot and has_comma:
        if s.rfind('.') > s.rfind(','):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '').replace(',', '.')
    elif has_comma and not has_dot:
        s = s.replace(',', '.')
    m = re.search(r'\d+(?:\.\d+)?', s)
    return m.group(0) if m else ''

def _parse_price(x: dict) -> float:
    """Helper to safely parse price string into float for sorting. Unknowns map to inf."""
    raw = str(x.get("price", ""))
    norm = _normalize_price_string(raw)
    if not norm:
        return float("inf")
    try:
        val = float(norm)
        return val if val > 0 else float("inf")
    except ValueError:
        return float("inf")


# Stopwords to ignore when computing key token overlap
_STOPWORDS = {
    "de", "du", "la", "le", "les", "un", "une", "des", "et", "ou", "en",
    "au", "aux", "sur", "par", "pour", "avec", "sans", "the", "and", "or",
    "eau", "thermale", "soin", "peaux", "peau", "sensibles", "sensible",
}

def _norm_token(t: str) -> str:
    """Lowercase + strip accents for comparison."""
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()

def _key_tokens(text: str) -> set[str]:
    """Extract meaningful tokens from text, removing stopwords."""
    raw = re.findall(r"[a-zA-ZÀ-ÖØ-öø-ÿ0-9]+", text)
    return {
        _norm_token(t) for t in raw
        if len(t) >= 3 and _norm_token(t) not in _STOPWORDS
    }

# Domains whose scraped data is known to be wrong — block entirely
_BANNED_DOMAINS: set[str] = {"cosmedic.tn"}

# Product bundle keywords — reject any candidate whose name contains these
_BUNDLE_KEYWORDS: set[str] = {"coffret", "pack", "kit", "bundle", "box"}

# Regex to detect size-like tokens (30ml, 200 ml, 50g, etc.)
_SIZE_TOKEN_RE = re.compile(
    r"^(\d+(?:[.,]\d+)?)(mle?|ml|mg|mcg|g|gr|grs|kg|cl|l|oz)$",
    re.IGNORECASE,
)

def _normalize_size_text(text: str) -> str:
    """
    Collapse '30 ML', '30 ml', '30mle' → '30ml' everywhere in text
    so the tokenizer sees a single consistent token.
    """
    return re.sub(
        r"(\d+(?:[.,]\d+)?)\s*(mle?|ml|mg|mcg|g|gr|grs|kg|cl|l|oz)\b",
        lambda m: m.group(1).replace(",", ".") + "ml"
        if m.group(2).lower().startswith("ml") or m.group(2).lower().startswith("mle")
        else m.group(1).replace(",", ".") + m.group(2).lower(),
        text,
        flags=re.IGNORECASE,
    )

def _is_size_token(t: str) -> bool:
    return bool(_SIZE_TOKEN_RE.match(t))

def _prefilter_by_tokens(query: str, results: list[dict]) -> list[dict]:
    """
    Smart pre-filter after BM25:
    1. Block results from banned domains (cosmedic.tn etc.)
    2. If BOTH query AND candidate have a size AND they differ → REJECT
    3. If candidate is missing the size entirely → OK (website sometimes omits it)
    4. Require ALL non-size key tokens from the query to be present in candidate.
    """
    q_norm  = _normalize_size_text(query)
    q_all   = _key_tokens(q_norm)
    q_size_tokens  = {t for t in q_all if _is_size_token(t)}   # e.g. {'30ml'}
    q_content_tokens = q_all - q_size_tokens                    # e.g. {'avene','cleanance','serum','exfoliant'}

    if not q_content_tokens:
        return results

    kept = []
    for r in results:
        # ── Banned domain check ──────────────────────────────────────────────
        link   = str(r.get("link") or "")
        domain = _get_domain(link)
        if domain in _BANNED_DOMAINS:
            print(f"[PREFILTER] DROP (banned: {domain}): {r.get('name','')[:65]}")
            continue

        name   = r.get("name", "")
        # ── Bundle keyword check ─────────────────────────────────────────────
        name_lower = name.lower()
        if any(kw in name_lower for kw in _BUNDLE_KEYWORDS):
            print(f"[PREFILTER] DROP (bundle/pack): {name[:65]}")
            continue

        c_norm = _normalize_size_text(name)
        c_all  = _key_tokens(c_norm)
        c_size_tokens    = {t for t in c_all if _is_size_token(t)}
        c_content_tokens = c_all - c_size_tokens

        # ── Size rule ────────────────────────────────────────────────────────
        # Only reject if BOTH have a size AND they differ
        if q_size_tokens and c_size_tokens and q_size_tokens != c_size_tokens:
            print(f"[PREFILTER] DROP (size {q_size_tokens}≠{c_size_tokens}): {name[:65]}")
            continue

        # ── Content token rule ───────────────────────────────────────────────
        # All non-size query tokens must appear in the candidate (ignoring size)
        missing = q_content_tokens - c_content_tokens
        if missing:
            print(f"[PREFILTER] DROP (missing {missing}): {name[:65]}")
            continue

        kept.append(r)

    print(f"[PREFILTER] {len(results)} -> {len(kept)} after smart filter")
    return kept

def _get_domain(url: str) -> str:
    """Extract registrable domain from a URL for website-level dedup."""
    try:
        # strip scheme
        host = re.sub(r"^https?://", "", url.strip()).split("/")[0].lower()
        # strip www.
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return url

def _dedup_by_domain(listings: list[dict]) -> list[dict]:
    """
    Keep only the CHEAPEST listing per website domain.
    Also silently skips entries from _BANNED_DOMAINS (safety net).
    """
    best_by_domain: dict[str, dict] = {}
    no_link = []
    for lst in listings:
        link = str(lst.get("link") or "").strip()
        if not link:
            no_link.append(lst)
            continue
        domain = _get_domain(link)
        if domain in _BANNED_DOMAINS:
            continue
        if domain not in best_by_domain:
            best_by_domain[domain] = lst
        else:
            # keep the cheaper one
            current_price = _parse_price(best_by_domain[domain])
            new_price = _parse_price(lst)
            if new_price < current_price:
                best_by_domain[domain] = lst
    return list(best_by_domain.values()) + no_link


def _dedup_by_link(listings: list[dict]) -> list[dict]:
    """Keep one row per unique URL. Preserve all distinct retailer links."""
    seen_links: set[str] = set()
    seen_no_link: set[tuple] = set()
    out = []
    for lst in listings:
        link = str(lst.get("link") or "").strip()
        if link:
            if link in seen_links:
                continue
            seen_links.add(link)
        else:
            key = (str(lst.get("name", "")), str(lst.get("source", "")), str(lst.get("price", "")))
            if key in seen_no_link:
                continue
            seen_no_link.add(key)
        out.append(lst)
    return out


def _strip_internal(rows: list[dict]) -> list[dict]:
    for r in rows:
        r.pop("_id", None)
    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def search_product_es(
    ocr_cleaned_name: str,
    top_k: int = 100,
    use_filter: bool = True,
    use_cross_encoder_rerank: bool = True,
    rerank_max_candidates: int = 100,
) -> list[dict]:
    """
    Search for a product by its cleaned OCR name.

    Pipeline:
      1. Run strict BM25 search (no kNN vector search to avoid brand drift)
      2. Size pre-filter during ES result parsing (free, early)
      3. Cross-encoder rerank (LLM)
      4. Dedup by URL → sort by price → return

    Parameters
    ----------
    ocr_cleaned_name : str
        Groq-cleaned product name from OCR.
    top_k : int
        Maximum candidates to retrieve from ES before filtering.
    use_filter : bool
        Legacy parameter, kept for compatibility.
    use_cross_encoder_rerank : bool
        Re-score with a cross-encoder model after filtering.
    rerank_max_candidates : int
        Cap on how many candidates the cross-encoder processes.
    """
    _load_es()

    if not _es_client:
        print("[ES] Not connected.")
        return []

    # Hard cap — ignore any larger value passed by callers
    top_k = min(top_k, 100)

    q_size = _get_size(ocr_cleaned_name)
    results: list[dict] = []

    # Strip stopwords so BM25 75% minimum_match focuses on core terms
    query_tokens = _key_tokens(ocr_cleaned_name)
    bm25_query_str = " ".join(query_tokens) if query_tokens else ocr_cleaned_name

    # ── Step 1: Retrieve candidates strictly by keywords ──────────────────────
    body_bm25 = {
        "size": top_k,
        "_source": _ES_SOURCE,
        "query": {
            "bool": {
                "must": [{
                    "match": {
                        "name": {
                            "query": bm25_query_str,
                            "boost": BM25_BOOST,
                            "minimum_should_match": "75%",
                        }
                    }
                }]
            }
        },
    }
    
    try:
        resp_lex = _es_client.search(index=INDEX_NAME, body=body_bm25)
        results = _parse_hits(resp_lex, q_size)
        results = results[:top_k]
        print(f"[ES] Strict BM25 Query: {len(results)} candidates (capped to {top_k})")
    except Exception as e:
        print(f"[ES] Query failed: {e}")
        return []

    # ── Step 1b: Token pre-filter (free, before LLM) ────────────────────────────
    results = _prefilter_by_tokens(ocr_cleaned_name, results)
    if not results:
        return []

    # ── Step 2: Cross-encoder (LLM) rerank ────────────────────────────────────
    _do_rerank = (
        use_cross_encoder_rerank
        and _RERANK_AVAILABLE
        and rerank_listings_with_cross_encoder is not None
        and os.environ.get("DISABLE_CROSS_ENCODER", "").lower() not in {"1", "true"}
        and results
    )
    if _do_rerank:
        try:
            before = len(results)
            results = rerank_listings_with_cross_encoder(
                ocr_cleaned_name,
                results,
                max_candidates=min(rerank_max_candidates, before),
                relative_threshold=0.2,   # Drop everything with score < max - 0.2
            )
            print(f"[ES] Cross-encoder rerank: {before} -> {len(results)}")
        except Exception as e:
            print(f"[ES] Cross-encoder skipped: {e}")

    # ── Step 3: Dedup by domain (one result per website) + sort ─────────────────
    deduped = _dedup_by_domain(results)
    deduped.sort(key=_parse_price)
    _strip_internal(deduped)
    print(f"[ES] Returning {len(deduped)} unique listings by domain (sorted by price)")
    return deduped
