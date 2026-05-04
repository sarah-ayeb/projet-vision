"""
HTTP-friendly entry for the YOLO + PaddleOCR + Groq + FAISS semantic-match pipeline.
Used by FastAPI: decode upload bytes → run_pipeline_on_image → FAISS search → flat rows sorted by price.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
    load_dotenv(Path(__file__).parent / ".env")
except Exception:
    pass

from detect_and_ocr import run_pipeline_on_image  # noqa: E402

# ── Elasticsearch search (loaded lazily on first request) ─────────────────────
try:
    from elasticsearch_search import search_product_es
    _ES_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] elasticsearch_search could not be imported: {e}")
    _ES_AVAILABLE = False


def _normalize_price_string(s: str) -> str:
    """
    Normalize a raw price string to a float-parseable string.
    Handles:
      - Arabic-block currency chars (ديناردت and all U+0600-U+06FF)
      - Latin labels: DT, TND, dinar, etc.
      - Tunisian comma-decimal: '77,130 DT' → '77.130'
      - Dot-thousands + comma-decimal: '1.500,000' → '1500.0'
    """
    # Strip all Arabic-block characters (U+0600–U+06FF)
    s = re.sub(r'[\u0600-\u06FF]+', '', s)
    # Strip Latin currency labels
    s = re.sub(r'\b(DT|TND|dinar|dinars)\b', '', s, flags=re.IGNORECASE)
    # Strip all remaining non-numeric chars except . , and whitespace
    s = re.sub(r'[^\d.,\s]', '', s).strip()
    if not s:
        return ''

    has_dot   = '.' in s
    has_comma = ',' in s

    if has_dot and has_comma:
        # Whichever comes last is the decimal separator
        if s.rfind('.') > s.rfind(','):
            s = s.replace(',', '')           # comma = thousands, remove it
        else:
            s = s.replace('.', '').replace(',', '.')  # dot = thousands, comma = decimal
    elif has_comma and not has_dot:
        # Tunisian: 77,130 → 77.130 (comma is decimal)
        s = s.replace(',', '.')

    m = re.search(r'\d+(?:\.\d+)?', s)
    return m.group(0) if m else ''


def _parse_price_numeric(price) -> float:
    """Return a float for sorting; NaN if unknown (sorts last)."""
    if price is None:
        return float("nan")
    try:
        import pandas as pd
        if pd.isna(price):
            return float("nan")
    except Exception:
        pass
    if isinstance(price, (int, float)):
        if isinstance(price, float) and math.isnan(price):
            return float("nan")
        return float(price) if float(price) > 0 else float("nan")

    norm = _normalize_price_string(str(price))
    if not norm:
        return float("nan")
    try:
        val = float(norm)
        return val if val > 0 else float("nan")
    except ValueError:
        return float("nan")


def _format_prix_for_client(price) -> str | None:
    """Format price to '75.463 DT', or None if unknown (frontend shows 'Prix N/A')."""
    val = _parse_price_numeric(price)
    if math.isnan(val) or val <= 0:
        return None
    return f"{val:.3f} DT"

_LIVE_SCRAPE_SELECTORS = {
    'anais.tn': "span.current-price-value, span.price",
    'parahealth.tn': "div.glozin-product-price > p > ins > span > bdi, div.glozin-product-price > p > span > bdi",
    'lifepara.tn': "p.price ins .woocommerce-Price-amount bdi, p.price > .woocommerce-Price-amount bdi",
    'med-coast.tn': "p.price ins .woocommerce-Price-amount bdi, p.price > .woocommerce-Price-amount bdi",
    'paylesspara.com': "div.summary.entry-summary p.price > span, p.price > span",
}

def _scrape_live_price(url: str, domain: str) -> float:
    """Dynamically grab the real price from the website if DB data is flawed."""
    selector = _LIVE_SCRAPE_SELECTORS.get(domain)
    if not selector:
        return float("nan")
    try:
        print(f"[LIVE SCRAPE] Fetching live price for {domain}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Try each CSS selector variant (comma separated fallback)
            for sel in selector.split(','):
                el = soup.select_one(sel.strip())
                if el:
                    val = _parse_price_numeric(el.get_text(strip=True))
                    if not math.isnan(val):
                        print(f"[LIVE SCRAPE] Success -> {val}")
                        return val
    except Exception as e:
        print(f"[LIVE SCRAPE] Failed for {domain}: {e}")
    return float("nan")


def run_pipeline_bytes(
    image_bytes: bytes,
    *,
    merged_xlsx: str | Path | None = None,
    use_groq: bool = True,
    min_faiss_score: float = 0.88,
    top_k: int = 100,
    use_cross_encoder_rerank: bool = True,
    rerank_max_candidates: int = 100,
    ean_expand: bool = False,
) -> dict:
    """
    Run pipeline on raw image bytes (JPEG/PNG/etc.).

    Steps:
      1. Decode image
      2. YOLO → detect product regions
      3. PaddleOCR → extract text from each region
      4. Groq (optional) → clean product name
      5. Elasticsearch → find all matching listings
      6. Deduplicate by source website → sort by price

    Returns JSON-serialisable dict: success, message, detections, results, total_found.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        return {
            "success": False,
            "message": "Could not decode image. Use JPEG or PNG.",
            "detections": [],
            "results": [],
            "total_found": 0,
        }

    # Apply Paddle flags inside this worker thread (paddle.set_flags is per-thread,
    # not global — asyncio.to_thread spawns a new thread where main-thread flags don't apply)
    try:
        import os
        os.environ["FLAGS_use_mkldnn"] = "0"
        import paddle
        paddle.device.set_device('cpu')
    except Exception:
        pass

    # Run YOLO + EasyOCR + optional Groq
    # We do NOT pass match_db — matching is now handled by FAISS below
    detections = run_pipeline_on_image(
        image,
        use_groq=use_groq,
        match_db=None,
        use_model_cache=True,
        verbose=True,    # DEBUG: print OCR text to server console
    )

    print(f"[DEBUG] YOLO found {len(detections)} detection(s)")
    if len(detections) > 1:
        best_det = max(detections, key=lambda d: float(d.get("det_conf", 0.0)))
        detections = [best_det]
        print(f"[DEBUG] Filtered to top detection with conf={best_det.get('det_conf', 0.0):.3f}")
        
    for i, d in enumerate(detections):
        print(f"[DEBUG] Det {i+1}: raw='{d.get('product_text_raw')}' clean='{d.get('product_text_clean')}'")

    # ── Elasticsearch search for each detected product ────────────────────────
    slim_dets = []
    all_results: list[dict] = []

    for d in detections:
        clean_text = (d.get("product_text_clean") or d.get("product_text_raw") or "").strip()

        es_listings: list[dict] = []
        if _ES_AVAILABLE and clean_text and clean_text != "N/A":
            try:
                # We do not use min_faiss_score here because ES scores can scale differently
                es_listings = search_product_es(
                    clean_text,
                    top_k=top_k,
                    use_filter=True,
                    use_cross_encoder_rerank=use_cross_encoder_rerank,
                    rerank_max_candidates=rerank_max_candidates,
                )
                print(f"[DEBUG] ES Search '{clean_text[:50]}': {len(es_listings)} results")
            except Exception as e:
                print(f"[ES] Search failed for '{clean_text}': {e}")

        slim_dets.append({
            "box"               : d.get("box"),
            "det_conf"          : d.get("det_conf"),
            "product_text_raw"  : d.get("product_text_raw"),
            "product_text_clean": clean_text,
            "description"       : d.get("description", ""),
            "faiss_listings"    : len(es_listings), # keep key name for backwards compatibility
        })

        # Build client-facing rows for this detection
        for lst in es_listings:
            link      = str(lst.get("link") or "")
            source    = str(lst.get("source") or "")
            
            # --- Live Pricing Override ---
            if source in _LIVE_SCRAPE_SELECTORS and link:
                live_price = _scrape_live_price(link, source)
                if not math.isnan(live_price):
                    lst["price"] = live_price  # override the DB value
                    
            if "hdparashop.tn/products/" in link:
                link = link.replace("/products/", "/product/")
                
            price_str = _format_prix_for_client(lst.get("price"))
            all_results.append({
                "nom"             : str(lst.get("name") or ""),
                "prix"            : price_str,
                "lien"            : link,
                "link"            : link,
                "url"             : link,
                "site"            : source,
                "site_name"       : source,
                "similarity_score": round(lst.get("match_score", 0.0), 4),
                "match_score"     : round(lst.get("match_score", 0.0) * 100),
            })

    # ── Global dedup across all detections (by link, then name+price) ────
    seen_links: set[str] = set()
    seen_fallback: set[tuple] = set()
    unique_results: list[dict] = []

    for row in all_results:
        link = row.get("link") or ""
        if link:
            if link in seen_links:
                continue
            seen_links.add(link)
        else:
            key = (row.get("nom", ""), str(row.get("prix", "")))
            if key in seen_fallback:
                continue
            seen_fallback.add(key)
        unique_results.append(row)

    # Sort by price ascending (unknown prices go last)
    def sort_key(r: dict) -> float:
        p = _parse_price_numeric(r.get("prix"))
        return float("inf") if math.isnan(p) else p

    unique_results.sort(key=sort_key)

    msg = "OK"
    if not detections:
        msg = "No product detected in the image. Try a clearer packshot."
    elif not unique_results:
        msg = "Product detected but no matches found in the database."

    return {
        "success"    : True,
        "message"    : msg,
        "detections" : slim_dets,
        "results"    : unique_results,
        "total_found": len(unique_results),
    }
