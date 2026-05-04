"""
Product Detection + OCR + LLM Normalisation
===========================================
Step 1 → YOLO (e.g. v8/v11 via Ultralytics) detects product bounding boxes.
Step 2 → EasyOCR runs on each crop to extract the product text/name.
Step 3 → (optional) Groq + Llama 3 cleans the text: fix OCR mistakes and keep only brand + product name.
"""

import argparse
import os
import re
from pathlib import Path

import cv2
import numpy as np
import requests
from ultralytics import YOLO

# Metric sizes: 200ml, 40mle, 100 ml, 50g, 250mg, 1.5kg, 30cl, and handles standard 'e200mL' or 'e 50ml'
_METRIC_SIZE_RE = re.compile(
    r'(?:^|[^\w])e?\s*(\d+(?:[.,]\d+)?\s*(?:mle?|ml|mg|mcg|\xb5g|kg|g(?=\s|$|\|)|cl))\b',
    re.IGNORECASE,
)

# Imperial sizes: 3.4fl.oz., 6.8 fl oz … (fallback only)
_IMPERIAL_SIZE_RE = re.compile(
    r'\b(\d+(?:[.,]\d+)?\s*fl\.?\s*oz\.?)',
    re.IGNORECASE,
)

# Pattern to strip imperial tokens from anywhere in a string
_STRIP_IMPERIAL_RE = re.compile(
    r'\s*\d+(?:[.,]\d+)?\s*fl\.?\s*oz\.?',
    re.IGNORECASE,
)


def _extract_size(raw_text: str) -> str:
    """Prefer metric size (100ml) over imperial (3.4fl.oz). Normalises 'mle' → 'ml'."""
    text = raw_text or ""
    m = _METRIC_SIZE_RE.search(text)
    if m:
        size = m.group(1).strip()
        # Fix PaddleOCR artefact '100mle' → '100ml'
        size = re.sub(r'mle$', 'ml', size, flags=re.IGNORECASE)
        return size
    # Fallback to imperial only when no metric found
    m = _IMPERIAL_SIZE_RE.search(text)
    return m.group(1).strip() if m else ""


def _ensure_size_in_name(clean_name: str, raw_text: str) -> str:
    """Strip imperial from LLM name; append metric size if LLM forgot it."""
    # Remove any fl.oz token the LLM may have included
    clean_name = _STRIP_IMPERIAL_RE.sub("", clean_name).strip().rstrip(" -,.")

    size = _extract_size(raw_text)
    if not size:
        return clean_name

    # Skip if metric size is already present (case-insensitive, ignore spaces)
    norm = lambda s: re.sub(r'\s+', '', s).lower()
    if norm(size) in norm(clean_name):
        return clean_name
    return f"{clean_name} {size}"

# Compatibility: NumPy 2.x removed np.sctypes which is still used by imgaug (Paddle dependency)
import numpy as np
if not hasattr(np, 'sctypes'):
    # Restore minimal sctypes so 'imgaug' and other old libs don't crash on import
    np.sctypes = {
        'float': [np.float16, np.float32, np.float64],
        'int': [np.int8, np.int16, np.int32, np.int64],
        'uint': [np.uint8, np.uint16, np.uint32, np.uint64],
        'complex': [np.complex64, np.complex128]
    }

# PaddleOCR 3.4.0 — Disable OneDNN via env var to bypass PIR crash on Windows/3.13
os.environ["FLAGS_use_mkldnn"] = "0"

try:
    import paddle
    # Use CPU by default for stability
    paddle.device.set_device('cpu') 
except Exception:
    pass
try:
    from paddleocr import PaddleOCR
    _OCR_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] PaddleOCR import failed: {e}")
    _OCR_AVAILABLE = False

try:
    # Optional: load GROQ_API_KEY from a local .env file during development
    from dotenv import load_dotenv  # type: ignore[import-not-found]
    _DOTENV_LOADED = load_dotenv()
except Exception:
    _DOTENV_LOADED = False

# Optional: fuzzy-match against your Excel database
try:
    from match_products import load_database, find_similar_products  # type: ignore
    _MATCHING_AVAILABLE = True
except Exception:
    _MATCHING_AVAILABLE = False

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
# YOLO weights used by this script (place `best_yolov11.pt` next to this file)
YOLO_WEIGHTS = Path(__file__).parent / "best_yolov11.pt"
CONF_THRESHOLD = 0.35
IOU_THRESHOLD  = 0.45
PADDING        = 10

# Groq / Llama 3 config
GROQ_API_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "llama-3.3-70b-versatile"


def load_models(yolo_weights: Path):
    """Load YOLO and PaddleOCR 3.x models."""
    if not _OCR_AVAILABLE:
        raise RuntimeError("PaddleOCR is not available.")

    w = Path(yolo_weights).expanduser().resolve()
    if not w.is_file():
        raise FileNotFoundError(f"YOLO weights not found: {w}")
    print(f"[INFO] Loading YOLO model \u2192 {w}")
    yolo = YOLO(str(w))

    print("[INFO] Loading PaddleOCR (CPU, mkldnn=False) \u2026")
    try:
        # Crucial fix for 'ConvertPirAttribute2RuntimeAttribute' on Windows:
        # 1. enable_mkldnn=False prevents oneDNN PIR incompatibility
        # 2. use_gpu=False for initial safety, can be changed later
        ocr = PaddleOCR(
            lang="en",
            device="cpu",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
        )
        print("[INFO] PaddleOCR initialized successfully")
    except Exception as e:
        print(f"[WARNING] PaddleOCR initialization failed: {e}")
        raise RuntimeError(f"Failed to initialize PaddleOCR: {e}")

    print("[INFO] Models loaded successfully.\n")
    return yolo, ocr


_models_cache = None  # type: tuple | None


def get_cached_models():
    """Reuse YOLO + PaddleOCR across API requests (same process)."""
    global _models_cache
    if _models_cache is None:
        _models_cache = load_models(YOLO_WEIGHTS.resolve())
    return _models_cache


def clean_product_text_with_groq(raw_text: str, enable: bool = False) -> tuple[str, str]:
    """ 
    Use Groq + Llama 3 to:
      - correct OCR mistakes
      - keep brand + commercial product name, and product-defining size/concentration when present
        (e.g. 30ml, 50ml, SPF50+)
      - drop usage text, marketing blurbs, and non-essential extras (not the size line).
      - ALSO extract a short description.

    If `enable` is False or no API key is set, returns the original text and an empty string.
    """
    raw_text = (raw_text or "").strip()
    if not raw_text or raw_text == "N/A" or len(raw_text) < 3:
        return raw_text, ""

    if not enable:
        return raw_text, ""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Fail gracefully if the key is not configured
        return raw_text, ""

    prompt = f"""
You are an expert in product catalogue normalisation.
Input is noisy OCR text from a single product packshot (often French cosmetics or pharma).
Your job is to extract a clean short title AND a brief description.

Rules for the title:
1. Correct obvious OCR mistakes (e.g. 'Ejel' -> 'Gel', 'Sallate-Savon' -> 'Sans savon').
2. Keep ONLY:
   - Brand name (e.g. 'SVR', 'Eucerin', 'Cytolnat').
   - Full commercial product name including its cosmetic form words
     such as 'Crème', 'Gel Nettoyant Purifiant', 'Soin Contour des Yeux'.
3. KEEP concentration/size when present and product-defining (e.g. 30ml, 50ml, 40g, SPF50+).
4. REMOVE everything else: instructions, usage, broad marketing claims or ingredients
   (e.g. remove 'PEAUX GRASSES A IMPERFECTIONS', 'NETTOIE PURIFIE ASSAINIT', 'OILY SKIN', etc.).

Output format MUST be a valid JSON object with exactly two keys: "name" (the cleaned title) and "description" (a rich 3-4 sentence paragraph: describe the product type/category, its key active ingredients or technology, benefits for the target skin/hair type, and any notable features like SPF, size, concentration or special formula). Do not output markdown.

Examples:
OCR: 'SVR | AR | SENSIFINE | CREME | SOIN ANTI-ROUGEURS HYDRATANT APAISANT INTENSIF'
OUT: {{"name": "SVR - Sensifine AR Crème", "description": "Crème hydratante et apaisante spécialement formulée pour les peaux sensibles sujettes aux rougeurs et à la couperose. Sa formule anti-rougeurs intensif cible les irritations cutanées et renforce la barrière protectrice de la peau. Enrichie en actifs apaisants, elle procure une hydratation longue durée tout au long de la journée. Idéale en soin quotidien pour atténuer visiblement les rougeurs réactionnelles et améliorer le confort de la peau."}}

OCR: 'EUCERIN | HYALURON-FILLER | SOIN CONTOUR DES YEUX SPF15 | 15ML | 3x EFFECT | TROUSSE OFFERT'
OUT: {{"name": "Eucerin - Hyaluron-Filler Soin Contour des Yeux SPF15 15ml", "description": "Soin anti-âge haute performance pour le contour des yeux à triple action : il lisse, repulpe et protège grâce à l'acide hyaluronique à bas et haut poids moléculaire. Sa formule légère intègre un filtre solaire SPF15 pour protéger la zone délicate du périoculaire contre le photovieillissement. Conçu pour réduire l'apparence des rides, des poches et des cernes en quatre semaines d'utilisation. Sa texture rafraîchissante convient à tous les types de peau et s'applique matin et soir."}}

OCR: 'CYTOL | NAT | CYTOLCLEAN | Ejel | GEL NETTOYANT PURIFIANT | PEAUX GRASSES A IMPERFECTIONS | NETTOIE PURIFIE ASSAINIT'
OUT: {{"name": "Cytolnat - Cytolclean Gel Nettoyant Purifiant", "description": "Gel nettoyant purifiant formulé spécifiquement pour les peaux grasses et à tendance acnéique, offrant un nettoyage en profondeur des pores. Sa texture gel légère élimine efficacement les impuretés, l'excès de sébum et les résidus de maquillage, tout en respectant l'équilibre naturel de la peau. Enrichi en actifs purifiants et assainissants, il aide à prévenir l'apparition des boutons et des points noirs avec une utilisation régulière. Après chaque utilisation, la peau est nette, fraîche et matifiée sans effet desséchant."}}

Now process this OCR text and reply with ONLY the JSON object:
OCR: {raw_text}
OUT: 
"""

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "temperature": 0.1,
                "max_tokens": 400,
                "messages": [
                    {
                        "role": "system",
                        "content": "You specialise in cleaning noisy OCR product titles and MUST output pure JSON.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        cleaned = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        import json
        try:
            parsed = json.loads(cleaned)
            return parsed.get("name", raw_text), parsed.get("description", "")
        except Exception:
            return cleaned or raw_text, ""
    except Exception as e:
        # In production you might want to log this; here we silently fall back.
        print(f"[GROQ] Warning: normalisation failed, using raw OCR text. Error: {e}")
        return raw_text, ""


def padded_crop(img, box, pad=PADDING):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = box
    return img[max(0, y1-pad): min(h, y2+pad), max(0, x1-pad): min(w, x2+pad)]


def extract_text_from_crop(ocr, crop):
    """Run PaddleOCR on the crop, return the merged text."""
    try:
        result = ocr.ocr(crop)
    except Exception as e:
        print(f"[WARNING] PaddleOCR inference failed: {e}")
        return "N/A", []

    if not result or not result[0]:
        return "N/A", []

    res0 = result[0]
    texts: list[str] = []
    lines_info: list[tuple[str, float]] = []

    # PaddleOCR 3.x returns an OCRResult object with rec_texts/rec_scores
    if hasattr(res0, "get"):
        rec_texts = res0.get("rec_texts", []) or []
        rec_scores = res0.get("rec_scores", []) or []
        for text, conf in zip(rec_texts, rec_scores):
            try:
                conf_f = float(conf)
            except Exception:
                continue
            if isinstance(text, str) and text.strip() and conf_f > 0.4:
                t = text.strip()
                texts.append(t)
                lines_info.append((t, conf_f))
    else:
        # PaddleOCR 2.x list format
        for line in res0:
            box_points, (text, conf) = line
            if text.strip() and conf > 0.4:
                texts.append(text.strip())
                lines_info.append((text.strip(), float(conf)))

    return " | ".join(texts) if texts else "N/A", lines_info


def draw_results(image, detections):
    vis        = image.copy()
    font       = cv2.FONT_HERSHEY_SIMPLEX
    BOX_COLOR  = (0, 210, 60)
    LABEL_BG   = (0, 170, 50)
    LABEL_FG   = (255, 255, 255)
    OCR_BG     = (30, 30, 30)
    OCR_FG     = (0, 255, 200)

    for det in detections:
        x1, y1, x2, y2 = det["box"]

        # Product Bounding Box
        cv2.rectangle(vis, (x1, y1), (x2, y2), BOX_COLOR, 2)

        # Confidence title
        tag = f"product {det['det_conf']:.2f}"
        (tw, th), _ = cv2.getTextSize(tag, font, 0.55, 1)
        cv2.rectangle(vis, (x1, y1 - th - 8), (x1 + tw + 6, y1), LABEL_BG, -1)
        cv2.putText(vis, tag, (x1 + 3, y1 - 4), font, 0.55, LABEL_FG, 1, cv2.LINE_AA)

        # Display text lines
        y_cur = y2 + 18
        for txt, conf in det["text_lines"][:4]:
            text_str = f"{txt} [{conf:.2f}]"
            (lw, lh), _ = cv2.getTextSize(text_str, font, 0.45, 1)
            cv2.rectangle(vis, (x1, y_cur - lh - 4), (x1 + lw + 6, y_cur + 2), OCR_BG, -1)
            cv2.putText(vis, text_str, (x1 + 3, y_cur), font, 0.45, OCR_FG, 1, cv2.LINE_AA)
            y_cur += lh + 7

    return vis


def run_pipeline_on_image(
    image,
    conf=CONF_THRESHOLD,
    iou=IOU_THRESHOLD,
    use_groq: bool = False,
    match_db: str | None = None,
    match_limit: int = 10,
    match_threshold: int = 55,
    use_model_cache: bool = True,
    verbose: bool = True,
):
    """
    Run YOLO → OCR → optional Groq → optional fuzzy match on an in-memory BGR image.

    Returns list of detection dicts with keys: box, det_conf, product_text_raw,
    product_text_clean, text_lines, matches.
    """
    if image is None or getattr(image, "size", 0) == 0:
        raise ValueError("Invalid or empty image array")

    if use_model_cache:
        yolo, ocr = get_cached_models()
    else:
        yolo, ocr = load_models(YOLO_WEIGHTS.resolve())

    if verbose:
        print(f"[YOLO] Detecting products  conf={conf}  iou={iou} …")
    boxes = yolo.predict(source=image, conf=conf, iou=iou, verbose=False)[0].boxes

    db = None
    if match_db:
        if not _MATCHING_AVAILABLE:
            raise RuntimeError(
                "Matching requested but match_products.py (or its dependencies) could not be imported."
            )
        if verbose:
            print(f"[MATCH] Loading database → {match_db}")
        db = load_database(match_db)
        if verbose:
            print(f"[MATCH] Database loaded (rows={len(db)})\n")

    dets = []
    if boxes and len(boxes) > 0:
        if verbose:
            print(f"[YOLO] {len(boxes)} product(s) found. Running OCR …\n")

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            det_conf = round(float(box.conf[0]), 3)

            crop = padded_crop(image, [x1, y1, x2, y2])
            if crop.size == 0:
                continue

            raw_text, lines = extract_text_from_crop(ocr, crop)
            cleaned_res = clean_product_text_with_groq(raw_text, enable=use_groq)
            if isinstance(cleaned_res, tuple):
                cleaned_text, description_text = cleaned_res
            else:
                cleaned_text, description_text = cleaned_res, ""

            # Safety net: always include size/volume (e.g. 200ml) even if LLM dropped it
            cleaned_text = _ensure_size_in_name(cleaned_text, raw_text)

            if verbose:
                print(f"  [{i+1}/{len(boxes)}] Box ({x1},{y1})→({x2},{y2}) YOLO_conf={det_conf}")
                print(f"         OCR text:    \"{raw_text}\"")
                if use_groq:
                    print(f"         Cleaned:     \"{cleaned_text}\"")
                    print(f"         Description: \"{description_text}\"\n")
                else:
                    print()

            matches = []
            if db is not None:
                matches = find_similar_products(
                    clean_name=cleaned_text,
                    db=db,
                    limit=match_limit,
                    threshold=match_threshold,
                )
                if verbose:
                    print(f"         Matches (top {match_limit}, threshold={match_threshold}):")
                    if not matches:
                        print("           [no matches]")
                    else:
                        for m in matches:
                            print(f"           - {m['score']:3d}  {m['name']}")
                    print()

            dets.append({
                "box": [x1, y1, x2, y2],
                "det_conf": det_conf,
                "product_text_raw": raw_text,
                "product_text_clean": cleaned_text,
                "description": description_text,
                "text_lines": lines,
                "matches": matches,
            })

    return dets


def pipeline(
    image_path,
    conf=CONF_THRESHOLD,
    iou=IOU_THRESHOLD,
    save=False,
    show=False,
    out_dir="output",
    use_groq: bool = False,
    match_db: str | None = None,
    match_limit: int = 10,
    match_threshold: int = 55,
):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")

    dets = run_pipeline_on_image(
        image,
        conf=conf,
        iou=iou,
        use_groq=use_groq,
        match_db=match_db,
        match_limit=match_limit,
        match_threshold=match_threshold,
        use_model_cache=True,
        verbose=True,
    )

    vis = draw_results(image, dets)

    if show:
        cv2.imshow("Detection + PaddleOCR", vis)
        print("[INFO] Press any key to close the window …")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if save:
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, Path(image_path).stem + "_result.jpg")
        cv2.imwrite(out, vis)
        print(f"[INFO] Saved result → {out}")

    return dets


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--conf", type=float, default=CONF_THRESHOLD)
    p.add_argument("--iou", type=float, default=IOU_THRESHOLD)
    p.add_argument("--save", action="store_true")
    p.add_argument("--show", action="store_true")
    p.add_argument("--output", default="output")
    p.add_argument(
        "--use_groq",
        action="store_true",
        help="Use Groq + Llama 3 to clean OCR text into 'BRAND - PRODUCT NAME'. "
             "Requires GROQ_API_KEY to be set in your environment.",
    )
    p.add_argument(
        "--match_db",
        default=None,
        help="Path to merged.xlsx (or another Excel file with a 'name' column) to fuzzy-match against.",
    )
    p.add_argument("--match_limit", type=int, default=10)
    p.add_argument("--match_threshold", type=int, default=55)
    args = p.parse_args()

    pipeline(
        args.image,
        args.conf,
        args.iou,
        args.save,
        args.show,
        args.output,
        use_groq=args.use_groq,
        match_db=args.match_db,
        match_limit=args.match_limit,
        match_threshold=args.match_threshold,
    )
