import json
import re
import os
from groq import Groq

# Initialize groq client with user's key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    groq_client = None
    print(f"[RERANK] Could not initialize Groq client: {e}")
PROMPT_TEMPLATE = """Task: Identify which candidates are the SAME physical product as the Target Product.

You are a Tunisian parapharmacy expert. Your job is to find ALL listings of the same product 
across different websites, even when websites write the product name differently.

CORE PRINCIPLE: Websites often omit words, add words, or describe the same product differently.
Focus on whether a customer buying the candidate would receive the SAME physical item.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALWAYS KEEP — these differences are FINE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Missing brand name in candidate (e.g. target has "Uriage" but candidate just says "Crème Lavante 200ml")
✓ Missing product line words (e.g. target has "Eau Thermale" but candidate omits it)
✓ Extra skin type words added (e.g. candidate adds "Peaux Sensibles", "Peau Mixte", "Peau Sèche")
✓ Extra marketing words (e.g. "Nos Promotions", "Nouveau", "Offre", "Pack", "Kit")
✓ Minor spelling differences (e.g. "Sensibles" vs "Sensible", "Crème" vs "Creme")
✓ Different word order (e.g. "Crème Lavante Uriage" vs "Uriage Crème Lavante")
✓ Abbreviations (e.g. "SPF50" vs "SPF50+", "200ML" vs "200ml")
✓ Missing SPF value in candidate when target has it (assume match)
✓ Missing size in candidate when target has it (assume match)
✓ OCR artifacts or partial brand names (e.g. "Uriag" or "URIAGE" or "uriage")
✓ One has brand + product line, other has only product line (same product)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICTLY REJECT — these differences mean different product:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Clearly different brand (e.g. target=SVR, candidate=Bioderma — both brands present and different)
✗ Clearly different size/volume (e.g. target=200ml, candidate=400ml — both sizes present and different)
✗ Clearly different product type (e.g. target=Crème, candidate=Shampooing or Gel Douche)
✗ Clearly different product line (e.g. target=Effaclar, candidate=Toleriane — both lines present and different)
✗ Different SPF level (e.g. target=SPF30, candidate=SPF50 — both present and different)
✗ Clearly different concentration (e.g. target=1%, candidate=2%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REAL EXAMPLES from Tunisian parapharmacie websites:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Target: "Eau Thermale Avène - Cleanance Sérum Exfoliant 30ml"
  KEEP → "AVENE CLEANANCE SERUM EXFOLIANT AHA 30ML"           (AHA is part of the product name, same product — SAME)
  KEEP → "AVENE CLEANANCE SERUM EXFOLIANT AHA – 30ML"         (dash formatting difference — SAME product)
  KEEP → "AVENE Cleanance AHA Sérum Exfoliant ,30 ml"         (punctuation + "AHA" inside name — SAME product)
  KEEP → "AVENE CLENANCE SERUM EXFOLIANT AHA 30 ML"           (typo "clenance" + "AHA" — SAME product)
  KEEP → "Avène Cleanance - Sérum Exfoliant AHA - 30ml"       (formatting with dashes — SAME product)
  REJECT → "AVENE CLEANANCE COMEDOMED CONCENTRE ANTI IMPERFECTION 30ML" (different product: Comedomed, not Sérum Exfoliant)
  REJECT → "AVENE Cleanance Women Soin Nuit Lissant 30ml"      (different product: Women Soin Nuit, not Sérum Exfoliant)
Target: "Uriage - Eau Thermale Crème Lavante 200ml"
  KEEP → "uriage creme lavante peaux sensibles 200ml"        (added skin type, missing "Eau Thermale" — SAME product)
  KEEP → "Uriage Crème Lavante Peaux Sensible 200ml"         (minor spelling, missing line — SAME product)
  KEEP → "URIAGE CREME LAVANTE 200ML"                        (simplified name — SAME product)
  KEEP → "Uriage crème lavante peaux sensibles 200ml"        (lowercase, extra words — SAME product)
  REJECT → "Uriage Gel Lavant 200ml"                         (different product type: Crème vs Gel)
  REJECT → "Uriage Eau Thermale Crème Lavante 400ml"         (different size: 200ml vs 400ml)

Target: "SVR SENSIFINE AR CREME SPF50+ 40ML"
  KEEP → "SVR SENSIFINE AR Crème Apaisante Anti-Rougeurs SPF50+ 40ml"  (extra descriptor words — SAME product)
  KEEP → "svr sensifine ar creme 40ml"                       (missing SPF — SAME product)
  KEEP → "SENSIFINE AR CREME SPF50+"                         (missing brand and size — SAME product)
  REJECT → "SVR SENSIFINE AR CREME SPF50+ 50ML"              (different size: 40ml vs 50ml)
  REJECT → "SVR SEBIACLEAR CREME SPF50+ 40ML"                (different product line: SENSIFINE vs SEBIACLEAR)

Target: "Bioderma Sensibio Gel Moussant 200ml"
  KEEP → "BIODERMA SENSIBIO GEL MOUSSANT PURIFIANT 200ML"    (extra word — SAME product)
  KEEP → "Sensibio Gel Moussant 200ml"                       (missing brand — SAME product)
  REJECT → "Bioderma Sensibio Gel Moussant 500ml"            (different size)
  REJECT → "Bioderma Atoderm Gel Moussant 200ml"             (different line: Sensibio vs Atoderm)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT RULES (follow strictly in order):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SIZE RULE: If both target AND candidate explicitly state a size/volume AND they differ (e.g. 30ml vs 200ml) → REJECT. If the candidate has NO size in its name → do NOT reject for size alone.
2. BRAND RULE: If a different brand is clearly stated in the candidate (e.g. target=Avène, candidate=Bioderma) → REJECT.
3. PRODUCT TYPE RULE (applies when size and brand match or size is missing): Check if the core product type matches. The product type is words like "Sérum Exfoliant", "Gel Nettoyant", "Crème Hydratante", "Soin Nuit", etc. If the product type clearly differs → REJECT. Ignore extra qualification words (e.g. "AHA", "Peaux Sensibles", "Peau Grasse") — these are NOT reasons to reject.
4. BRAND PREFIX RULE: Missing generic brand prefixes (e.g. "Eau Thermale", "Laboratoire", "Laboratoire Dermatologique", "Paris") in the candidate is NOT a reason to reject.
5. PRECISION OVER RECALL: When in doubt → REJECT. Only keep if confident it is the same product.
6. Skin type descriptors (Peaux Sensibles, Peau Grasse, Peau Sèche, Peau Mixte) are NOT a reason to reject.
7. Promotional words (Offre Spéciale, BOX, Pack, Nouveau) are NOT a reason to reject — but verify the core product inside the pack still matches.

Return ONLY a valid JSON array of matching integer indices.
No explanation. No markdown. No extra text.
Example: [0, 1, 3, 5, 7, 8, 11, 14, 17, 19, 22]

Target Product: "{target}"
Candidates:
{candidates}
"""

def rerank_listings_with_cross_encoder(target_name: str, candidates: list[dict], max_candidates=200, relative_threshold=0.0) -> list[dict]:
    # Despite the function name (kept for compatibility), we are now using LLM
    if not candidates:
        return []
    
    candidates_to_process = candidates[:max_candidates]
    CHUNK_SIZE = 50
    final_filtered = []
    
    # Process in chunks to avoid LLM context limits and timeouts
    for chunk_start in range(0, len(candidates_to_process), CHUNK_SIZE):
        chunk = candidates_to_process[chunk_start:chunk_start + CHUNK_SIZE]
        
        c_text = ""
        for idx, c in enumerate(chunk):
            name = c.get('name', 'Unknown')[:100]
            c_text += f"[{idx}] {name}\n"
        
        prompt = PROMPT_TEMPLATE.format(target=target_name, candidates=c_text)
        
        print(f"[RERANK] Asking LLaMA 3 (via Groq API) to filter chunk {chunk_start}-{chunk_start+len(chunk)-1} ...")
        if not groq_client:
            print("[RERANK] Groq client not initialized, keeping all.")
            final_filtered.extend(chunk)
            continue
            
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a data-matching JSON-only assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1024,
            )
            result_text = response.choices[0].message.content
            
            match = re.search(r"\[[\d\s,]*\]", result_text)
            if match:
                kept_indices = json.loads(match.group(0))
                kept_indices = set(kept_indices)
                for i, c in enumerate(chunk):
                    if i in kept_indices:
                        final_filtered.append(c)
                    else:
                        print(f"[RERANK] DROP (LLM decision): {c.get('name', '')[:65]}")
            else:
                print(f"[RERANK] JSON array not found in LLM output! Output was: {result_text}")
                # Fallback: keep all in this chunk if it failed to parse
                final_filtered.extend(chunk)
                
        except Exception as e:
            print(f"[RERANK] LLM exception via Groq: {e}")
            final_filtered.extend(chunk)
    
    print(f"[RERANK] LLM kept {len(final_filtered)} out of {len(candidates_to_process)}")
    # CRITICAL: We return only the filtered items! Do not append unprocessed candidates.
    return final_filtered
