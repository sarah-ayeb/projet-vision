# AI-Powered Pharmaceutical Product Recognition & Price Comparison Platform

> A final-year engineering project (PFA) — an intelligent, end-to-end platform that enables users to identify parapharmacy products through AI-driven image recognition and instantly compare real-time prices across Tunisian e-commerce websites.

---

## 🧠 What It Does

This platform solves a real problem faced by pharmacists and consumers in Tunisia: quickly identifying unlabeled or unfamiliar parapharmacy products and finding the best price without manually browsing multiple websites.

It combines **computer vision**, **OCR**, **large language models**, and **semantic search** into a seamless pipeline:

### 🔍 Image Search — *Identify a product from a photo*
1. User uploads a photo of a product (box, bottle, tube, etc.)
2. **YOLOv11** (custom-trained) detects the product region in the image
3. **PaddleOCR** extracts all visible text from the label
4. **Groq / LLaMA-3** normalizes the raw OCR output into a clean product name
5. **Elasticsearch** (hybrid BM25 + semantic) retrieves the best matching products from the catalog
6. **Groq LLM reranker** filters and ranks final results for maximum relevance

### 📦 Barcode Search — *Scan a barcode, compare prices instantly*
1. User scans an EAN barcode via webcam or types it manually
2. The backend scrapes **real-time prices** from multiple Tunisian parapharmacy websites
3. Results are displayed side-by-side with prices, links, and availability

### 📊 Reporting & Administration
- Every search session is saved as a **persistent report** (product name, results, timestamp)
- Admin dashboard for managing users, viewing analytics, and monitoring search activity
- Role-based access: standard users vs. administrators

---

## 🏗️ Project Structure

```
pfa_github/
├── Back_End/                   # FastAPI REST API
│   ├── main.py                 # All API endpoints (auth, search, reports)
│   ├── enhanced_search.py      # Real-time barcode price scraper
│   ├── barcode_search.py       # Barcode search (legacy fallback)
│   ├── database.py             # SQLite / SQLAlchemy setup
│   ├── models.py               # DB models: User, Report, Site
│   ├── config.py               # Configuration & API keys
│   └── requirements.txt
├── image_search/               # AI recognition pipeline
│   ├── detect_and_ocr.py       # YOLOv11 + PaddleOCR + Groq normalization
│   ├── pipeline_api.py         # FastAPI integration entry point
│   ├── elasticsearch_search.py # Hybrid BM25 + cross-encoder search
│   ├── rerank_cross_encoder.py # Groq LLM reranker (LLaMA-3)
│   ├── best_yolov11.pt         # Custom-trained YOLO model weights
│   └── requirements.txt
├── Front_End/                  # Vue.js 3 + Vuetify frontend
│   └── src/
│       ├── components/
│       │   ├── ImageSearch.vue       # AI image search interface
│       │   ├── BarcodeSearch.vue     # Barcode scan & price comparison
│       │   ├── BarcodeScanner.vue    # Webcam barcode scanner
│       │   ├── Reports.vue           # Search history & reports
│       │   ├── AdminPanel.vue        # Admin dashboard
│       │   ├── Statistics.vue        # Analytics & charts
│       │   ├── LoginAuth.vue         # Authentication
│       │   └── Navigation.vue        # App navigation
│       ├── locales/                  # i18n (French / English)
│       ├── router/index.js
│       └── main.js
└── alembic/                    # Database migration scripts
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Elasticsearch** running on `http://localhost:9200`
- **Tesseract OCR** installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`
- A **Groq API Key** from [console.groq.com](https://console.groq.com) — set it in `image_search/.env`:
  ```
  GROQ_API_KEY=your_key_here
  ```

### 1. Backend (FastAPI)
```bash
cd Back_End
pip install -r requirements.txt
pip install -r ../image_search/requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend (Vue.js)
```bash
cd Front_End
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Vue.js 3, Vuetify 3, Vue Router, Axios, @zxing/library |
| **Backend** | FastAPI, SQLAlchemy, SQLite, Alembic, aiohttp |
| **AI / Vision** | YOLOv11 (Ultralytics), PaddleOCR, Groq API (LLaMA-3.1) |
| **Search Engine** | Elasticsearch (BM25 + semantic hybrid search) |
| **Scraping** | BeautifulSoup4, aiohttp (async multi-site scraping) |

---

## 📌 Notes

- The `.env` file containing your `GROQ_API_KEY` is **gitignored** and should never be committed.
- The YOLO model (`best_yolov11.pt`) was trained on a custom dataset of Tunisian parapharmacy product images.
- The Elasticsearch index must be pre-populated with the product catalog before running image searches.

---

*Developed as a Final Year Project (PFA) — 2025/2026*
