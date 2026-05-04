# import sys
# import asyncio
#
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
#
# # Add this at the very top of the file
# print("Backend module is loading...")
#
# from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# import bcrypt
# import jwt
# import datetime
# from Back_End.database import get_db, Base, engine
# from Back_End.models import User as UserModel
# from Back_End.models import Product as ProductModel
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import Request
# from fastapi.responses import Response, JSONResponse
# import requests
# from bs4 import BeautifulSoup
# import urllib.parse
# import re
# import time
# from config import GOOGLE_API_KEY, CSE_ID
# import httpx
# from barcode_search import search_barcode_on_sites
#
# SECRET_KEY = "ourKey"  # Changez cette clé
#
# SEARCH_TIMEOUT = 3  # Very fast timeout for search requests
# PRODUCT_TIMEOUT = 2  # Very fast timeout for product page requests
# DNS_FAILURE_TOLERANCE = 0.3  # Allow 30% of sites to fail before stopping
# MAX_DNS_FAILURES = 15
# MAX_PRODUCTS_PER_SITE = 5  # Limit products checked per site for speed
# MAX_RESULTS_TARGET = 5  # Lower target for faster results
#
# TUNISIAN_SITES_CONFIG = {
#     "parapharmacie.tn": {
#         "search_urls": [
#             "https://parapharmacie.tn/recherche?controller=search&s={barcode}",
#             "https://parapharmacie.tn/catalogsearch/result/?q={barcode}"
#         ],
#         "direct_urls": [
#             "https://parapharmacie.tn/nuxe-white-ultimate-glow-creme-gel-eclaircissante-hydratante-50ml-{barcode}.html",
#             "https://parapharmacie.tn/produit-{barcode}.html"
#         ],
#         "product_selectors": [
#             "a.product-item-link", 
#             "a.product-thumbnail",
#             ".product-item a",
#             "a[href*='.html']",
#             "a[href*='/product']",
#             "a[href*='/produit']"
#         ],
#         "barcode_selectors": [".sku", ".product-sku", "[data-sku]", ".reference"],
#         "priority": 1
#     },
#     "parashop.tn": {
#         "search_urls": [
#             "https://parashop.tn/recherche?controller=search&s={barcode}",
#             "https://www.parashop.tn/recherche?controller=search&s={barcode}"
#         ],
#         "direct_urls": [
#             "https://parashop.tn/nuxe-white-{barcode}.html",
#             "https://www.parashop.tn/nuxe-white-{barcode}.html"
#         ],
#         "product_selectors": [
#             "a.product-thumbnail", 
#             "a.product-item-link", 
#             ".product a",
#             "a[href*='.html']"
#         ],
#         "barcode_selectors": [".sku", ".reference", "[data-reference]", ".product-sku"],
#         "priority": 1
#     },
#     "pharma-shop.tn": {
#         "search_urls": [
#             "https://pharma-shop.tn/recherche?controller=search&s={barcode}"
#         ],
#         "direct_urls": [
#             "https://pharma-shop.tn/soins-anti-taches-et-depigmentants/1807-nuxe-white-creme-nuit-eclaircissante-renovatrice-50ml-{barcode}.html"
#         ],
#         "product_selectors": ["a.product-thumbnail", ".product-name a", "a[href*='.html']"],
#         "barcode_selectors": [".sku", ".product-reference", ".reference"],
#         "priority": 1
#     }
# }
#
# def get_prioritized_sites_for_barcode(barcode: str) -> list:
#     site_configs = []
#     for site_name, config in TUNISIAN_SITES_CONFIG.items():
#         site_config = {
#             'name': site_name,
#             'search_urls': config.get('search_urls', []),
#             'direct_urls': config.get('direct_urls', []),
#             'product_selectors': config.get('product_selectors', []),
#             'barcode_selectors': config.get('barcode_selectors', []),
#             'priority': config.get('priority', 1)
#         }
#         site_configs.append(site_config)
#     return sorted(site_configs, key=lambda x: x['priority'])

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import sys
import os

# Add the current directory to Python path to handle imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# image_search pipeline (YOLO + PaddleOCR + Groq + merged.xlsx fuzzy match)
_project_root = os.path.dirname(current_dir)
_image_search_dir = os.path.join(_project_root, "image_search")
if os.path.isdir(_image_search_dir) and _image_search_dir not in sys.path:
    sys.path.insert(0, _image_search_dir)

try:
    from barcode_search import search_barcode_on_sites
except ImportError:
    # Try relative import if running from project root
    from Back_End.barcode_search import search_barcode_on_sites

# IMPORTANT: Load paddle/YOLO in the MAIN thread at startup to avoid pybind11 generic_type errors in asyncio.to_thread
try:
    from pipeline_api import run_pipeline_bytes
    import detect_and_ocr
    # Warm up models synchronously on startup so it doesn't crash when imported concurrently inside endpoint
    detect_and_ocr.get_cached_models()
except Exception as e:
    print(f"Warning: Could not preload pipeline models during startup. {e}")

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image
import io
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
# Import OpenCV for advanced image preprocessing
import cv2
import numpy as np
OPENCV_AVAILABLE = True

try:
    from config import GOOGLE_API_KEY, CSE_ID
except ImportError:
    # Try relative import if running from project root
    from Back_End.config import GOOGLE_API_KEY, CSE_ID

from database import get_db
from models import Report as ReportModel
from sqlalchemy.orm import Session
from fastapi import Depends

# Additional imports for enhanced website scraping
import asyncio
import functools
import aiohttp
from urllib.parse import urljoin
from typing import List, Dict, Set, Optional
import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
from aiohttp import ClientTimeout, TCPConnector
import logging
from dataclasses import dataclass
from collections import defaultdict
import re
from bs4 import BeautifulSoup, Tag
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration for advanced scraping - Optimized for maximum speed"""
    max_concurrent_requests: int = 25  # Increased for faster parallel processing
    request_timeout: int = 10  # Reduced timeout for faster failure detection
    max_retries: int = 2  # Reduced retries for speed
    retry_delay: float = 0.2  # Faster retry delay
    cache_ttl: int = 3600  # 1 hour
    rate_limit_delay: float = 0.1  # Minimal delay between requests
    user_agents: List[str] = None
    verify_ssl: bool = False  # Disabled SSL verification for speed
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]



class AdvancedProductScraper:
    """High-performance product scraper with concurrent processing and smart caching"""
    
    def __init__(self, base_url: str, selectors: dict, config: ScrapingConfig = None):
        self.base_url = base_url
        self.selectors = selectors
        self.config = config or ScrapingConfig()
        self.session = None
        self.cache = {}
        self.visited_urls = set()
        self.semaphore = None
        self.results = []
        self.stats = {
            'pages_scraped': 0,
            'products_found': 0,
            'errors': 0,
            'cache_hits': 0,
            'start_time': time.time()
        }
    
    async def __aenter__(self):
        # Create connection pool for better performance
        connector = TCPConnector(
            limit=self.config.max_concurrent_requests * 2,
            limit_per_host=self.config.max_concurrent_requests,
            ttl_dns_cache=300,
            use_dns_cache=True,
            verify_ssl=self.config.verify_ssl
        )
        
        timeout = ClientTimeout(total=self.config.request_timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': random.choice(self.config.user_agents)}
        )
        
        # Create semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return time.time() - cache_time < self.config.cache_ttl
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch page with caching and retry logic"""
        cache_key = self._get_cache_key(url)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]['content']
        
        async with self.semaphore:
            for attempt in range(self.config.max_retries):
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Cache the result
                            self.cache[cache_key] = {
                                'content': content,
                                'timestamp': time.time()
                            }
                            
                            # Rate limiting
                            await asyncio.sleep(self.config.rate_limit_delay)
                            return content
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            
                except Exception as e:
                    logger.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    else:
                        self.stats['errors'] += 1
        
        return ""
    
    def _extract_products_fast(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """Fast product extraction with intelligent fallback"""
        products = []
        
        # Use provided selectors only
        container_selector = self.selectors.get('productContainer')
        
        if not container_selector:
            logger.warning(f"No container selector found for {page_url}")
            return products
        
        containers = soup.select(container_selector)
        logger.info(f"Found {len(containers)} containers with selector: {container_selector}")
        
        # Use provided selectors only
        name_selector = self.selectors.get('name')
        price_selector = self.selectors.get('price')
        image_selector = self.selectors.get('image')
        link_selector = self.selectors.get('link')
        
        # Extract products efficiently with minimal logging for maximum speed
        for i, container in enumerate(containers):
            try:
                product = {'source_url': page_url}
                
                # Extract name with cleaning (optimized)
                if name_selector:
                    name_elem = container.select_one(name_selector)
                    if name_elem:
                        raw_name = name_elem.get_text(strip=True)
                        product['name'] = clean_product_name(raw_name)
                    else:
                        # Quick fallback for name extraction
                        for alt_selector in ['.product_desc h3', '.product_desc h2', '.product-title', '.name']:
                            alt_elem = container.select_one(alt_selector)
                            if alt_elem:
                                raw_name = alt_elem.get_text(strip=True)
                                product['name'] = clean_product_name(raw_name)
                                break
                
                # Extract price - get only the main price, not all price elements
                if price_selector:
                    # Try to get the main price (not the base price)
                    price_elem = container.select_one(price_selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        # Clean up the price text - extract just the price number
                        import re
                        price_match = re.search(r'(\d+[,\d]*)\s*TND', price_text)
                        if price_match:
                            product['price'] = f"{price_match.group(1)} TND"
                        else:
                            product['price'] = price_text
                    else:
                        # Quick fallback for price extraction
                        for alt_selector in ['.price', '.product-price .price', '.current-price']:
                            alt_elem = container.select_one(alt_selector)
                            if alt_elem:
                                price_text = alt_elem.get_text(strip=True)
                                price_match = re.search(r'(\d+[,\d]*)\s*TND', price_text)
                                if price_match:
                                    product['price'] = f"{price_match.group(1)} TND"
                                else:
                                    product['price'] = price_text
                                break
                        
                        # If still no price found, try to extract from structured data (JSON-LD)
                        if not product.get('price'):
                            try:
                                # Look for JSON-LD structured data
                                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                                for script in json_ld_scripts:
                                    try:
                                        import json
                                        data = json.loads(script.string)
                                        
                                        # Handle different JSON-LD structures
                                        if isinstance(data, dict):
                                            # Direct product object
                                            if data.get('@type') == 'Product' and data.get('offers'):
                                                offers = data['offers']
                                                if isinstance(offers, dict) and offers.get('price'):
                                                    price = offers.get('price')
                                                    currency = offers.get('priceCurrency', 'TND')
                                                    product['price'] = f"{price} {currency}"
                                                    logger.info(f"Product {i+1} price (JSON-LD): {product['price']}")
                                                    break
                                                elif isinstance(offers, list) and len(offers) > 0:
                                                    # Multiple offers, take the first one
                                                    first_offer = offers[0]
                                                    if first_offer.get('price'):
                                                        price = first_offer.get('price')
                                                        currency = first_offer.get('priceCurrency', 'TND')
                                                        product['price'] = f"{price} {currency}"
                                                        logger.info(f"Product {i+1} price (JSON-LD): {product['price']}")
                                                        break
                                        
                                        elif isinstance(data, list):
                                            # Array of structured data
                                            for item in data:
                                                if isinstance(item, dict) and item.get('@type') == 'Product' and item.get('offers'):
                                                    offers = item['offers']
                                                    if isinstance(offers, dict) and offers.get('price'):
                                                        price = offers.get('price')
                                                        currency = offers.get('priceCurrency', 'TND')
                                                        product['price'] = f"{price} {currency}"
                                                        logger.info(f"Product {i+1} price (JSON-LD): {product['price']}")
                                                        break
                                                    elif isinstance(offers, list) and len(offers) > 0:
                                                        first_offer = offers[0]
                                                        if first_offer.get('price'):
                                                            price = first_offer.get('price')
                                                            currency = first_offer.get('priceCurrency', 'TND')
                                                            product['price'] = f"{price} {currency}"
                                                            logger.info(f"Product {i+1} price (JSON-LD): {product['price']}")
                                                            break
                                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                                        logger.debug(f"Error parsing JSON-LD: {e}")
                                        continue
                            except Exception as e:
                                logger.debug(f"Error extracting JSON-LD price: {e}")
                
                # Extract image
                if image_selector:
                    img_elem = container.select_one(image_selector)
                    if img_elem:
                        # Try multiple image source attributes for lazy loading
                        img_src = (img_elem.get('data-src') or 
                                  img_elem.get('data-lazy-src') or
                                  img_elem.get('data-original') or
                                  img_elem.get('data-lazy') or
                                  img_elem.get('src'))
                        if img_src:
                            product['image'] = self._normalize_url(img_src)
                            logger.info(f"Product {i+1} image: {product['image'][:50]}...")
                        else:
                            logger.warning(f"Product {i+1}: No image src found with {image_selector}")
                    else:
                        logger.warning(f"Product {i+1}: No image element found with {image_selector}")
                        # Try alternative image selectors
                        alt_image_selectors = [
                            '.product-thumbnail img[data-src]',
                            '.product-thumbnail img',
                            '.product-image img',
                            '.image img',
                            'img[data-src]',
                            'img[src*="product"]',
                            'img'
                        ]
                        for alt_selector in alt_image_selectors:
                            alt_elem = container.select_one(alt_selector)
                            if alt_elem:
                                img_src = (alt_elem.get('data-src') or 
                                          alt_elem.get('data-lazy-src') or
                                          alt_elem.get('data-original') or
                                          alt_elem.get('data-lazy') or
                                          alt_elem.get('src'))
                                if img_src:
                                    product['image'] = self._normalize_url(img_src)
                                    logger.info(f"Product {i+1} image (alt): {product['image'][:50]}... with {alt_selector}")
                                    break
                
                # Extract link
                if link_selector:
                    link_elem = container.select_one(link_selector)
                    if link_elem:
                        link_href = link_elem.get('href')
                        if link_href:
                            product['link'] = self._normalize_url(link_href)
                
                # Only add if we have essential data
                if product.get('name') and product.get('price'):
                    products.append(product)
                    logger.debug(f"Product {i+1} added successfully")
                else:
                    logger.debug(f"Product {i+1} skipped - missing name or price. Name: {bool(product.get('name'))}, Price: {bool(product.get('price'))}")
                    
            except Exception as e:
                logger.error(f"Error extracting product {i+1}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(products)} products from {len(containers)} containers")
        return products
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to absolute format"""
        if not url:
            return ""
        if url.startswith('//'):
            return f"https:{url}"
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        if not url.startswith(('http://', 'https://')):
            return urljoin(self.base_url, url)
        return url
    
    def _find_pagination_links_fast(self, soup: BeautifulSoup) -> List[str]:
        """Fast pagination link detection"""
        pagination_urls = []
        
        # Common pagination patterns
        pagination_patterns = [
            'a[href*="page="]', 'a[href*="p="]', 'a[href*="pg="]',
            '.pagination a', '.pager a', 'a[rel="next"]', 'a.next',
            'a[class*="next"]', 'a[class*="page"]'
        ]
        
        for pattern in pagination_patterns:
            links = soup.select(pattern)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = self._normalize_url(href)
                    if full_url and full_url not in self.visited_urls:
                        pagination_urls.append(full_url)
        
        return list(set(pagination_urls))[:5]  # Limit to 5 pagination links
    
    async def scrape_page_concurrent(self, url: str) -> tuple[List[Dict], List[str]]:
        """Scrape a single page concurrently"""
        if url in self.visited_urls:
            return [], []
        
        self.visited_urls.add(url)
        self.stats['pages_scraped'] += 1
        
        content = await self._fetch_page(url)
        if not content:
            return [], []
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract products
        products = self._extract_products_fast(soup, url)
        self.stats['products_found'] += len(products)
        
        # Find pagination links
        pagination_links = self._find_pagination_links_fast(soup)
        
        return products, pagination_links
    
    async def scrape_all_products_fast(self, max_pages: int = 10, max_products: int = 100) -> List[Dict]:
        """Fast concurrent scraping of all products"""
        urls_to_visit = [self.base_url]
        all_products = []
        
        while urls_to_visit and len(self.visited_urls) < max_pages and len(all_products) < max_products:
            # Take up to 5 URLs to process concurrently
            current_batch = urls_to_visit[:5]
            urls_to_visit = urls_to_visit[5:]
            
            # Process batch concurrently
            tasks = [self.scrape_page_concurrent(url) for url in current_batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed: {result}")
                    continue
                
                products, pagination_links = result
                all_products.extend(products)
                
                # Add new pagination URLs
                for pag_url in pagination_links:
                    if pag_url not in self.visited_urls and pag_url not in urls_to_visit:
                        urls_to_visit.append(pag_url)
            
            # Stop if we have enough products
            if len(all_products) >= max_products:
                break
        
        # Remove duplicates efficiently
        seen_products = set()
        unique_products = []
        
        for product in all_products:
            product_key = f"{product.get('name', '')}_{product.get('price', '')}"
            if product_key not in seen_products:
                seen_products.add(product_key)
                unique_products.append(product)
        
        return unique_products[:max_products]
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        elapsed_time = time.time() - self.stats['start_time']
        return {
            **self.stats,
            'elapsed_time': elapsed_time,
            'products_per_second': self.stats['products_found'] / elapsed_time if elapsed_time > 0 else 0,
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['pages_scraped'], 1),
            'error_rate': self.stats['errors'] / max(self.stats['pages_scraped'], 1)
        }

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": f"Validation error: {str(exc)}"}
    )

class BarcodeRequest(BaseModel):
    barcode: str

class TextSearchRequest(BaseModel):
    searchText: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ReportRequest(BaseModel):
    barcode: str
    product_name: str | None = None
    search_date: str
    total_results: int
    results: str  # JSON string

def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy using advanced techniques
    """
    if not OPENCV_AVAILABLE:
        # Fallback: return original image with basic PIL preprocessing
        processed_images = []
        
        # Convert to grayscale if it's a color image
        if image.mode != 'L':
            gray = image.convert('L')
        else:
            gray = image
        
        # Basic PIL preprocessing
        from PIL import ImageEnhance, ImageFilter
        
        # 1. Original grayscale
        processed_images.append(("original", gray))
        
        # 2. Enhanced contrast
        enhancer = ImageEnhance.Contrast(gray)
        contrast_img = enhancer.enhance(2.0)
        processed_images.append(("enhanced", contrast_img))
        
        # 3. Sharpened
        sharpened = gray.filter(ImageFilter.SHARPEN)
        processed_images.append(("sharpened", sharpened))
        
        # 4. Smoothed
        smoothed = gray.filter(ImageFilter.SMOOTH)
        processed_images.append(("smoothed", smoothed))
        
        return processed_images
    
    # OpenCV preprocessing (if available)
    # Convert PIL image to OpenCV format
    if isinstance(image, Image.Image):
        # Convert PIL to numpy array
        img_array = np.array(image)
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_array = image
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    
    # Apply different preprocessing techniques
    processed_images = []
    
    # 1. Enhanced contrast and brightness (most effective)
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    processed_images.append(("enhanced", enhanced))
    
    # 2. Denoised image
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    processed_images.append(("denoised", denoised))
    
    # 3. Adaptive threshold (good for varying lighting)
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    processed_images.append(("adaptive", adaptive_thresh))
    
    # 4. Enhanced + Gaussian blur (reduce noise)
    blurred_enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    processed_images.append(("enhanced_blur", blurred_enhanced))
    
    # 5. Denoised + Enhanced
    denoised_enhanced = clahe.apply(denoised)
    processed_images.append(("denoised_enhanced", denoised_enhanced))
    
    return processed_images

def extract_text_with_multiple_attempts(image):
    """
    Try multiple OCR configurations to get the best result
    """
    all_results = []
    
    # Try simple text extraction first (often works best for product names)
    try:
        simple_text = pytesseract.image_to_string(image, lang='eng')
        simple_text = re.sub(r'\s+', ' ', simple_text).strip()
        if simple_text and len(simple_text) > 2:
            print(f"[OCR DEBUG] Simple extraction: '{simple_text}'")
            all_results.append({
                'text': simple_text,
                'confidence': 50.0,
                'method': 'simple'
            })
    except Exception as e:
        print(f"[OCR DEBUG] Simple extraction failed: {str(e)}")
    
    # Try with different PSM modes for simple extraction
    psm_modes = [6, 3, 8, 13]
    for psm in psm_modes:
        try:
            config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(image, lang='eng', config=config)
            text = re.sub(r'\s+', ' ', text).strip()
            if text and len(text) > 2:
                print(f"[OCR DEBUG] PSM {psm}: '{text}'")
                all_results.append({
                    'text': text,
                    'confidence': 45.0,
                    'method': f'psm_{psm}'
                })
        except Exception as e:
            print(f"[OCR DEBUG] PSM {psm} failed: {str(e)}")
    
    # Try with different languages (fallback to eng if others fail)
    languages = ['eng', 'eng+fra']
    for lang in languages:
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            text = re.sub(r'\s+', ' ', text).strip()
            if text and len(text) > 2:
                print(f"[OCR DEBUG] Language {lang}: '{text}'")
                all_results.append({
                    'text': text,
                    'confidence': 45.0,
                    'method': f'lang_{lang}'
                })
        except Exception as e:
            print(f"[OCR DEBUG] Language {lang} failed: {str(e)}")
    
    # Try with preprocessing - focus on the most promising methods
    processed_images = preprocess_image_for_ocr(image)
    
    # Only try the most effective preprocessing methods based on results
    priority_methods = ['enhanced', 'adaptive', 'denoised']
    
    for img_name, processed_img in processed_images:
        # Skip methods that aren't working well
        if img_name not in priority_methods:
            continue
        try:
            # Convert back to PIL for pytesseract
            if OPENCV_AVAILABLE and hasattr(processed_img, 'shape'):
                # OpenCV array
                if len(processed_img.shape) == 3:
                    pil_img = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                else:
                    pil_img = Image.fromarray(processed_img)
            else:
                # Already a PIL image
                pil_img = processed_img
            
            # Try different PSM modes with preprocessed image
            for psm in [6, 3]:  # Focus on the most effective PSM modes
                try:
                    config = f'--oem 3 --psm {psm}'
                    text = pytesseract.image_to_string(pil_img, lang='eng', config=config)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 2:
                        print(f"[OCR DEBUG] {img_name} + PSM {psm}: '{text}'")
                        all_results.append({
                            'text': text,
                            'confidence': 40.0,
                            'method': f'{img_name}_psm_{psm}'
                        })
                except Exception as e:
                    print(f"[OCR DEBUG] {img_name} + PSM {psm} failed: {str(e)}")
                    
        except Exception as e:
            print(f"[OCR DEBUG] Failed to process {img_name}: {str(e)}")
            continue
    
    # Select the best result
    if not all_results:
        return ""
    
    # Select the best result using natural criteria
    if not all_results:
        return ""
    
    # Sort by confidence first, then by length
    all_results.sort(key=lambda x: (x['confidence'], len(x['text'])), reverse=True)
    
    best_result = all_results[0]['text']
    print(f"[OCR DEBUG] Best result: '{best_result}' (method: {all_results[0]['method']}, confidence: {all_results[0]['confidence']:.1f})")
    
    # Show top 3 results for debugging
    print(f"[OCR DEBUG] Top 3 results:")
    for i, result in enumerate(all_results[:3]):
        print(f"  {i+1}. '{result['text']}' (method: {result['method']}, confidence: {result['confidence']:.1f}, length: {len(result['text'])})")
    
    return best_result

def clean_extracted_text(text):
    """
    Clean and improve extracted text for better search results
    """
    if not text:
        return ""
    
    # Remove obvious OCR artifacts and noise
    text = re.sub(r'[^\w\s\-\.\(\)]', ' ', text)  # Keep alphanumeric, spaces, hyphens, dots, parentheses
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    # Remove very short words (likely OCR errors)
    words = text.split()
    cleaned_words = []
    for word in words:
        # Keep words that are meaningful or longer than 1 character
        if len(word) > 1 or word.lower() in ['s', 'a', 'i']:  # Keep single letters that might be meaningful
            cleaned_words.append(word)
    
    cleaned_text = ' '.join(cleaned_words)
    
    # Remove very obvious prefixes/suffixes
    if len(cleaned_words) > 2:
        # Remove only the most common prefixes
        common_prefixes = ['the', 'a', 'an']
        if cleaned_words and cleaned_words[0].lower() in common_prefixes:
            cleaned_words.pop(0)
        
        cleaned_text = ' '.join(cleaned_words)
    
    return cleaned_text

def clean_product_name(name_text):
    """Clean product name by removing price information and other contaminants"""
    if not name_text:
        return ""
    
    # Remove price patterns (TND, €, $, etc.)
    name_text = re.sub(r'\d+[,\d]*\s*(TND|€|\$|DT|dinars?)', '', name_text, flags=re.IGNORECASE)
    
    # Remove availability text
    name_text = re.sub(r'disponibilit[ée]:?\s*\d*', '', name_text, flags=re.IGNORECASE)
    name_text = re.sub(r'stock:?\s*\d*', '', name_text, flags=re.IGNORECASE)
    
    # Remove common product page suffixes
    name_text = re.sub(r'prix\s*de?\s*', '', name_text, flags=re.IGNORECASE)
    name_text = re.sub(r'prix\s*', '', name_text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and punctuation
    name_text = re.sub(r'\s+', ' ', name_text.strip())
    name_text = re.sub(r'^\s*[,\-]\s*', '', name_text)
    name_text = re.sub(r'\s*[,\-]\s*$', '', name_text)
    
    return name_text.strip()

class SmartSelectorDetector:
    """Intelligent selector detection for web scraping"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def analyze_website(self, url: str) -> dict:
        """Analyze website structure and detect optimal selectors"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detect selectors
            selectors = {
                'productContainer': self.detect_product_container_selectors(soup),
                'name': self.detect_product_name_selectors(soup),
                'price': self.detect_price_selectors(soup),
                'image': self.detect_image_selectors(soup),
                'link': self.detect_link_selectors(soup)
            }
            
            # Extract test products
            test_products = self.extract_test_products(soup, url, selectors)
            
            # Generate website overview
            website_overview = self.generate_website_overview(soup, url)
            
            return {
                'detected_selectors': selectors,
                'test_products': test_products,
                'website_overview': website_overview
            }
            
        except Exception as e:
            return {
                'detected_selectors': {},
                'test_products': [],
                'website_overview': f'Error analyzing website: {str(e)}'
            }
    
    def detect_product_container_selectors(self, soup: BeautifulSoup) -> str:
        """Detect product container selectors"""
        container_patterns = [
            '.product-miniature',
            '.product-item',
            '.product-card',
            '.product-box',
            '.product-container',
            '.product-grid-item',
            '.product-list-item',
            '.product',
            '.item',
            '[class*="product"]'
        ]
        
        for pattern in container_patterns:
            if soup.select(pattern):
                return pattern
        
        return ""
    
    def detect_product_name_selectors(self, soup: BeautifulSoup) -> str:
        """Detect product name selectors"""
        name_patterns = [
            '.product_desc h3',
            '.product_desc h2',
            '.product-title',
            '.name a',
            '.product-name',
            '.title',
            'h3 a',
            'h2 a',
            '.product_desc a'
        ]
        
        for pattern in name_patterns:
            if soup.select(pattern):
                return pattern
        
        return ""
    
    def detect_price_selectors(self, soup: BeautifulSoup) -> str:
        """Detect price selectors"""
        price_patterns = [
            '.price',
            '.product-price .price',
            '.current-price',
            '.price-box .price',
            '.product-price',
            '[class*="price"]'
        ]
        
        for pattern in price_patterns:
            if soup.select(pattern):
                return pattern
        
        return ""
    
    def detect_image_selectors(self, soup: BeautifulSoup) -> str:
        """Detect image selectors"""
        image_patterns = [
            'img',
            '.product-image img',
            '.image img',
            'a img'
        ]
        
        for pattern in image_patterns:
            if soup.select(pattern):
                return pattern
        
        return ""
    
    def detect_link_selectors(self, soup: BeautifulSoup) -> str:
        """Detect link selectors"""
        link_patterns = [
            'a',
            '.product a',
            '.product-item a',
            '.product-card a'
        ]
        
        for pattern in link_patterns:
            if soup.select(pattern):
                return pattern
        
        return ""
    
    def extract_test_products(self, soup: BeautifulSoup, url: str, selectors: dict) -> list:
        """Extract sample products for testing"""
        products = []
        
        container_selector = selectors.get('productContainer')
        if not container_selector:
            return products
        
        containers = soup.select(container_selector)[:3]  # Get first 3 products
        
        for container in containers:
            product = {}
            
            # Extract name
            if selectors.get('name'):
                name_elem = container.select_one(selectors['name'])
                if name_elem:
                    product['name'] = name_elem.get_text(strip=True)
            
            # Extract price
            if selectors.get('price'):
                price_elem = container.select_one(selectors['price'])
                if price_elem:
                    product['price'] = price_elem.get_text(strip=True)
            
            # Extract image
            if selectors.get('image'):
                img_elem = container.select_one(selectors['image'])
                if img_elem and img_elem.get('src'):
                    product['image'] = img_elem['src']
            
            # Extract link
            if selectors.get('link'):
                link_elem = container.select_one(selectors['link'])
                if link_elem and link_elem.get('href'):
                    product['link'] = link_elem['href']
            
            if product:
                products.append(product)
        
        return products
    
    def generate_website_overview(self, soup: BeautifulSoup, url: str) -> str:
        """Generate website overview"""
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "Unknown"
        
        return f"Website: {title_text} | URL: {url}"

def generate_recommendations(analysis_results: dict) -> list:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    selectors = analysis_results.get('detected_selectors', {})
    
    if not selectors.get('productContainer'):
        recommendations.append("No product containers detected. Try manual selector configuration.")
    
    if not selectors.get('name'):
        recommendations.append("Product name selectors not found. Consider using '.product-title' or '.name'.")
    
    if not selectors.get('price'):
        recommendations.append("Price selectors not found. Consider using '.price' or '.product-price'.")
    
    if not selectors.get('image'):
        recommendations.append("Image selectors not found. Consider using 'img' or '.product-image img'.")
    
    if not selectors.get('link'):
        recommendations.append("Link selectors not found. Consider using 'a' or '.product a'.")
    
    if not recommendations:
        recommendations.append("Good selector detection! You can proceed with scraping.")
    
    return recommendations

@app.post("/api/search-barcode")
async def search_barcode_endpoint(request: BarcodeRequest):
    try:
        # Use the enhanced smart search system
        from enhanced_search import search_barcode_enhanced
        results = await search_barcode_enhanced(request.barcode)
        
        return {
            "success": True, 
            "message": "Enhanced smart search completed", 
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        logger.error(f"Error in enhanced barcode search: {e}")
        return {"success": False, "message": str(e), "results": []}


@app.get("/api/pipeline-image-search/ping")
async def pipeline_image_search_ping():
    """Quick check that this process loaded the route (restart backend if you get 404 on POST)."""
    return {"ok": True, "message": "POST with multipart field 'image' to run the pipeline."}


@app.post("/api/pipeline-image-search")
async def pipeline_image_search(
    image: UploadFile = File(...),
    min_faiss_score: float = Form(0.88),
):
    """
    YOLOv11 product detection → PaddleOCR → Groq/Llama name cleanup →
    FAISS semantic search (score ≥ min_faiss_score) → sorted by price.
    min_faiss_score is sent by the frontend from the admin-panel slider.
    """
    try:
        body = await image.read()
        result = await asyncio.to_thread(
            run_pipeline_bytes,
            body,
            min_faiss_score=min_faiss_score,
            top_k=100,
            use_cross_encoder_rerank=True,
            rerank_max_candidates=100,
        )
        return result
    except Exception as e:
        logger.error(f"pipeline-image-search: {e}")
        return {
            "success": False,
            "message": str(e),
            "detections": [],
            "results": [],
            "total_found": 0,
        }


@app.post("/api/extract-text")
async def extract_text_from_image(image: UploadFile = File(...)):
    """Extract text from image using OCR"""
    try:
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Use improved OCR extraction
        raw_extracted_text = extract_text_with_multiple_attempts(img)
        
        if not raw_extracted_text:
            return {
                "success": False,
                "message": "No text could be extracted from the image. Try uploading a clearer image with better contrast.",
                "text": ""
            }
        
        # Clean and improve the extracted text
        extracted_text = clean_extracted_text(raw_extracted_text)
        
        return {
            "success": True,
            "message": "Text extracted successfully",
            "text": extracted_text
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Text extraction failed: {str(e)}",
            "text": ""
        }

@app.post("/api/search-text")
async def search_text_endpoint(request: TextSearchRequest):
    try:
        # Use the same search function as barcode search but with text
        results = search_barcode_on_sites(request.searchText)
        return {"success": True, "message": "Search completed", "results": results}
    except Exception as e:
        return {"success": False, "message": str(e), "results": []}

@app.post("/login")
async def login(request: LoginRequest):
    # Simple hardcoded user for testing
    if request.email == "test@example.com" and request.password == "password":
        return {"token": "your_jwt_token_here"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

async def search_google_for_pharma_shop(query: str) -> list:
    """Search Google for pharma-shop.tn links"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": CSE_ID,
            "q": query,
            "num": 10  # Get up to 10 results
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if "items" in data:
            for item in data["items"]:
                link = item.get("link", "")
                if "pharma-shop.tn" in link:
                    results.append({
                        "title": item.get("title", ""),
                        "link": link,
                        "snippet": item.get("snippet", "")
                    })
        
        return results
        
    except Exception as e:
        print(f"Google search error: {str(e)}")
        return []

def extract_barcodes_from_urls(google_results: list) -> list:
    """Extract barcodes from pharma-shop.tn URLs"""
    barcodes = []
    
    for result in google_results:
        url = result.get("link", "")
        if "pharma-shop.tn" in url:
            # Look for barcode patterns in the URL
            # Common patterns: -1234567890123.html, /1234567890123.html, etc.
            barcode_patterns = [
                r'-(\d{13})\.html',  # -1234567890123.html
                r'/(\d{13})\.html',  # /1234567890123.html
                r'-(\d{12})\.html',  # -123456789012.html (12 digits)
                r'/(\d{12})\.html',  # /123456789012.html (12 digits)
                r'-(\d{14})\.html',  # -12345678901234.html (14 digits)
                r'/(\d{14})\.html',  # /12345678901234.html (14 digits)
            ]
            
            for pattern in barcode_patterns:
                matches = re.findall(pattern, url)
                for match in matches:
                    if match not in barcodes:
                        barcodes.append(match)
    
    return barcodes

@app.post("/api/reports")
def save_report(report: ReportRequest, db: Session = Depends(get_db)):
    try:
        print(f"Received report data: {report}")
        # Convert search_date string to datetime object
        search_date = datetime.datetime.fromisoformat(report.search_date.replace('Z', '+00:00'))
        
        db_report = ReportModel(
            barcode=report.barcode,
            product_name=report.product_name,
            search_date=search_date,
            total_results=report.total_results,
            results=report.results
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return {"success": True, "message": "Report saved", "report_id": db_report.id}
    except ValueError as e:
        print(f"Validation error: {e}")
        return {"success": False, "message": f"Validation error: {str(e)}"}
    except Exception as e:
        db.rollback()
        print(f"Error saving report: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/reports")
def get_reports(db: Session = Depends(get_db)):
    """Get all reports from the database"""
    try:
        reports = db.query(ReportModel).all()
        reports_data = []
        for report in reports:
            reports_data.append({
                "id": report.id,
                "barcode": report.barcode,
                "product_name": report.product_name,
                "search_date": report.search_date,
                "total_results": report.total_results,
                "results": report.results
            })
        return {"success": True, "reports": reports_data}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a specific report from the database"""
    try:
        report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
        if not report:
            return {"success": False, "message": "Report not found"}
        
        db.delete(report)
        db.commit()
        return {"success": True, "message": "Report deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

@app.delete("/api/reports")
def delete_all_reports(db: Session = Depends(get_db)):
    """Delete all reports from the database"""
    try:
        db.query(ReportModel).delete()
        db.commit()
        return {"success": True, "message": "All reports deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

# Site Management API Endpoints
from models import Site
import json
import datetime

class SiteRequest(BaseModel):
    site_name: str
    search_url: str
    selectors: dict

@app.get("/api/sites")
def get_sites(db: Session = Depends(get_db)):
    """Get all sites from the database"""
    try:
        sites = db.query(Site).all()
        sites_data = []
        for site in sites:
            sites_data.append({
                "id": site.id,
                "site_name": site.site_name,
                "search_url": site.search_url,
                "selectors": json.loads(site.selectors) if site.selectors else {},
                "is_active": bool(site.is_active),
                "created_at": site.created_at.isoformat() if site.created_at else None,
                "updated_at": site.updated_at.isoformat() if site.updated_at else None
            })
        return {"success": True, "sites": sites_data}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/sites")
def add_site(site: SiteRequest, db: Session = Depends(get_db)):
    """Add a new site to the database"""
    try:
        # Check if site already exists
        existing_site = db.query(Site).filter(Site.site_name == site.site_name).first()
        if existing_site:
            return {"success": False, "message": "Site already exists"}
        
        # Create new site
        new_site = Site(
            site_name=site.site_name,
            search_url=site.search_url,
            selectors=json.dumps(site.selectors, ensure_ascii=False),
            is_active=1
        )
        
        db.add(new_site)
        db.commit()
        db.refresh(new_site)
        
        return {"success": True, "message": "Site added successfully", "site_id": new_site.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

@app.put("/api/sites/{site_id}")
def update_site(site_id: int, site: SiteRequest, db: Session = Depends(get_db)):
    """Update an existing site"""
    try:
        existing_site = db.query(Site).filter(Site.id == site_id).first()
        if not existing_site:
            return {"success": False, "message": "Site not found"}
        
        existing_site.site_name = site.site_name
        existing_site.search_url = site.search_url
        existing_site.selectors = json.dumps(site.selectors, ensure_ascii=False)
        existing_site.updated_at = datetime.datetime.utcnow()
        
        db.commit()
        return {"success": True, "message": "Site updated successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

@app.delete("/api/sites/{site_id}")
def delete_site(site_id: int, db: Session = Depends(get_db)):
    """Delete a site from the database"""
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return {"success": False, "message": "Site not found"}
        
        db.delete(site)
        db.commit()
        return {"success": True, "message": "Site deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

@app.put("/api/sites/{site_id}/toggle")
def toggle_site_status(site_id: int, db: Session = Depends(get_db)):
    """Toggle site active/inactive status"""
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return {"success": False, "message": "Site not found"}
        
        site.is_active = 0 if site.is_active else 1
        site.updated_at = datetime.datetime.utcnow()
        
        db.commit()
        return {"success": True, "message": "Site status updated", "is_active": bool(site.is_active)}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

class WebsiteScrapingRequest(BaseModel):
    website_url: str
    selectors: dict

class SelectorDiscoveryRequest(BaseModel):
    website_url: str
    product_sample_url: Optional[str] = None

class EnhancedWebsiteScrapingRequest(BaseModel):
    website_url: str
    selectors: dict
    max_pages: int = 999999  # Unlimited pages
    max_products: int = 999999  # Unlimited products
    follow_categories: bool = True
    follow_pagination: bool = True
    delay_between_requests: float = 0.1  # Ultra-fast requests (100ms)
    timeout: int = 30  # Reduced timeout for faster processing

@app.post("/api/sites/discover-selectors")
async def discover_selectors(request: SelectorDiscoveryRequest, db: Session = Depends(get_db)):
    """Discover CSS selectors for a website using SmartSelectorDetector"""
    try:
        print(f"🔍 Discovering selectors for: {request.website_url}")
        
        # Use SmartSelectorDetector to analyze the website
        detector = SmartSelectorDetector()
        
        # Analyze the website
        analysis_results = detector.analyze_website(request.website_url)
        
        # Map the detected selectors to the expected format
        detected_selectors = analysis_results['detected_selectors']
        
        discovered_selectors = {
            'product_links': [{'selector': detected_selectors.get('productContainer', ''), 'count': 1, 'sample_text': 'Detected'}] if detected_selectors.get('productContainer') else [],
            'product_name': [{'selector': detected_selectors.get('name', ''), 'count': 1, 'sample_text': 'Detected'}] if detected_selectors.get('name') else [],
            'product_price': [{'selector': detected_selectors.get('price', ''), 'count': 1, 'sample_text': 'Detected'}] if detected_selectors.get('price') else [],
            'product_image': [{'selector': detected_selectors.get('image', ''), 'count': 1, 'sample_text': 'Detected'}] if detected_selectors.get('image') else [],
            'product_reference': [{'selector': detected_selectors.get('link', ''), 'count': 1, 'sample_text': 'Detected'}] if detected_selectors.get('link') else []
        }
        
        # Calculate confidence score
        confidence_score = 0
        if detected_selectors.get('productContainer'):
            confidence_score += 25
        if detected_selectors.get('name'):
            confidence_score += 25
        if detected_selectors.get('price'):
            confidence_score += 25
        if detected_selectors.get('image'):
            confidence_score += 15
        if detected_selectors.get('link'):
            confidence_score += 10
        
        # Generate recommendations
        recommendations = generate_recommendations(analysis_results)
        
        # Clean test products
        test_products = []
        for product in analysis_results.get('test_products', []):
            if product.get('name'):
                product['name'] = clean_product_name(product['name'])
                test_products.append(product)
        
        return {
            "success": True,
            "discovered_selectors": discovered_selectors,
            "confidence_score": confidence_score,
            "recommendations": recommendations,
            "test_products": test_products
        }
        
    except Exception as e:
        print(f"❌ Error discovering selectors: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Error discovering selectors: {str(e)}"}
        price_patterns = [
            '[class*="price"]',
            '[class*="prix"]',
            '[itemprop="price"]',
            '.price',
            '.prix',
            '.cost',
            '.amount',
            '[class*="currency"]',
            'span:contains("DT")',
            'span:contains("TND")',
            'span:contains("€")',
            'span:contains("$")'
        ]
        
        # Manual search for price-like text
        price_elements = []
        for element in soup.find_all(['span', 'div', 'p', 'strong']):
            text = element.get_text(strip=True)
            if re.search(r'\d+[.,]?\d*\s*(DT|TND|€|\$|dinar)', text, re.IGNORECASE):
                if element.get('class'):
                    selector = f".{'.'.join(element.get('class'))}"
                elif element.get('id'):
                    selector = f"#{element.get('id')}"
                else:
                    selector = element.name
                
                price_elements.append({
                    'selector': selector,
                    'text': text[:50],
                    'element': element
                })
        
        # Add unique price selectors
        seen_selectors = set()
        for elem in price_elements[:10]:  # Limit to first 10
            if elem['selector'] not in seen_selectors:
                discovered_selectors['product_price'].append({
                    'selector': elem['selector'],
                    'count': 1,
                    'sample_text': elem['text']
                })
                seen_selectors.add(elem['selector'])
        
        # Discover product images
        print("🔍 Discovering product image selectors...")
        image_patterns = [
            'img[src*="product"]',
            'img[src*="produit"]',
            'img[src*="item"]',
            'img[src*="article"]',
            'img[class*="product"]',
            'img[class*="main"]',
            'img[class*="primary"]',
            '[class*="product"] img',
            '[class*="image"] img',
            '.product img',
            '.produit img',
            '[itemprop="image"]'
        ]
        
        for pattern in image_patterns:
            elements = soup.select(pattern)
            if elements:
                discovered_selectors['product_image'].append({
                    'selector': pattern,
                    'count': len(elements),
                    'sample_src': elements[0].get('src', '')[:100] if elements[0].get('src') else 'No src'
                })
        
        # Discover product references/SKUs
        print("🔍 Discovering product reference selectors...")
        reference_patterns = [
            '[class*="ref"]',
            '[class*="sku"]',
            '[class*="reference"]',
            '[class*="code"]',
            '[class*="model"]',
            '[itemprop="sku"]',
            '[itemprop="mpn"]',
            '.ref',
            '.sku',
            '.reference',
            '.code',
            '.model'
        ]
        
        for pattern in reference_patterns:
            elements = soup.select(pattern)
            if elements:
                discovered_selectors['product_reference'].append({
                    'selector': pattern,
                    'count': len(elements),
                    'sample_text': elements[0].get_text(strip=True)[:50] if elements[0].get_text(strip=True) else 'No text'
                })
        
        # Also look for barcode-like patterns
        barcode_elements = []
        for element in soup.find_all(['span', 'div', 'p']):
            text = element.get_text(strip=True)
            if re.search(r'\b\d{8,13}\b', text):  # 8-13 digit numbers (typical barcode length)
                if element.get('class'):
                    selector = f".{'.'.join(element.get('class'))}"
                elif element.get('id'):
                    selector = f"#{element.get('id')}"
                else:
                    selector = element.name
                
                barcode_elements.append({
                    'selector': selector,
                    'text': text[:50],
                    'element': element
                })
        
        # Add unique barcode selectors
        seen_barcode_selectors = set()
        for elem in barcode_elements[:5]:  # Limit to first 5
            if elem['selector'] not in seen_barcode_selectors:
                discovered_selectors['product_reference'].append({
                    'selector': elem['selector'],
                    'count': 1,
                    'sample_text': elem['text']
                })
                seen_barcode_selectors.add(elem['selector'])
        
        print(f"✅ Selector discovery completed!")
        print(f"📊 Found selectors:")
        for category, selectors in discovered_selectors.items():
            print(f"  {category}: {len(selectors)} selectors")
        
        return {
            "success": True,
            "discovered_selectors": discovered_selectors,
            "website_url": request.website_url,
            "total_selectors": sum(len(selectors) for selectors in discovered_selectors.values())
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching website: {e}")
        return {"success": False, "message": f"Error fetching website: {str(e)}"}
    except Exception as e:
        print(f"❌ Error discovering selectors: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Error discovering selectors: {str(e)}"}

class PaginationInfo:
    def __init__(self):
        self.current_page = 1
        self.has_next = True
        self.next_url = None
        self.total_pages = None
        self.visited_urls: Set[str] = set()

class ProductScraper:
    def __init__(self, base_url: str, selectors: dict, max_pages: int = 50, max_products: int = 1000, delay: float = 1.0):
        self.base_url = base_url
        self.selectors = selectors
        self.max_pages = max_pages
        self.max_products = max_products
        self.delay = delay
        self.all_products: List[Dict] = []
        self.visited_urls: Set[str] = set()
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def normalize_url(self, url: str) -> str:
        """Convert relative URLs to absolute URLs"""
        if not url:
            return ""
        if url.startswith('//'):
            return f"https:{url}"
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        if not url.startswith(('http://', 'https://')):
            return urljoin(self.base_url, url)
        return url
    
    def find_pagination_links(self, soup, current_url: str) -> List[str]:
        """Find all pagination links on the page"""
        pagination_urls = []
        
        # Common pagination selectors
        pagination_selectors = [
            'a[href*="page="]',
            'a[href*="p="]',
            'a[href*="pg="]',
            '.pagination a',
            '.pager a',
            '.page-numbers a',
            'a[rel="next"]',
            'a.next',
            'a[class*="next"]',
            'a[class*="page"]',
            'a[href*="offset="]',
            'a[href*="start="]'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = self.normalize_url(href)
                    if full_url and full_url not in self.visited_urls:
                        pagination_urls.append(full_url)
        
        # Also look for numbered pagination
        numbered_links = soup.find_all('a', href=re.compile(r'page=\d+|p=\d+|pg=\d+'))
        for link in numbered_links:
            href = link.get('href')
            if href:
                full_url = self.normalize_url(href)
                if full_url and full_url not in self.visited_urls:
                    pagination_urls.append(full_url)
        
        return list(set(pagination_urls))
    
    def find_category_links(self, soup) -> List[str]:
        """Find category/catalog links that might contain products"""
        category_urls = []
        
        # Common category selectors
        category_selectors = [
            'a[href*="/category/"]',
            'a[href*="/catalog/"]',
            'a[href*="/products/"]',
            'a[href*="/shop/"]',
            'a[href*="/collection/"]',
            '.category-link a',
            '.catalog-link a',
            'nav a[href*="/"]',
            '.menu a[href*="/"]',
            'a[href*="cat="]',
            'a[href*="category="]'
        ]
        
        for selector in category_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = self.normalize_url(href)
                    if full_url and full_url not in self.visited_urls:
                        # Filter out non-product URLs
                        if any(keyword in full_url.lower() for keyword in ['product', 'catalog', 'category', 'shop', 'collection']):
                            category_urls.append(full_url)
        
        return list(set(category_urls))
    
    def extract_products_from_page(self, soup, page_url: str) -> List[Dict]:
        """Extract products from a single page"""
        products = []
        
        # Extract website logo once per page (optional)
        website_logo = ''
        if self.selectors.get('logo'):
            logo_elem = soup.select_one(self.selectors['logo'])
            if logo_elem:
                logo_src = logo_elem.get('src') or logo_elem.get('data-src')
                if logo_src:
                    website_logo = self.normalize_url(logo_src)
        
        # Find product containers
        product_containers = soup.select(self.selectors.get('productContainer', ''))
        
        if not product_containers:
            return products
        
        for container in product_containers:
            try:
                product = {'source_url': page_url}
                
                # Add website logo to each product (same for all products on the page)
                if website_logo:
                    product['website_logo'] = website_logo
                
                # Extract product name
                if self.selectors.get('name'):
                    name_elem = container.select_one(self.selectors['name'])
                    product['name'] = name_elem.get_text(strip=True) if name_elem else ''
                
                # Extract product price
                if self.selectors.get('price'):
                    price_elem = container.select_one(self.selectors['price'])
                    product['price'] = price_elem.get_text(strip=True) if price_elem else ''
                
                # Extract product image
                if self.selectors.get('image'):
                    img_elem = container.select_one(self.selectors['image'])
                    if img_elem:
                        img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
                        if img_src:
                            product['image'] = self.normalize_url(img_src)
                        else:
                            product['image'] = ''
                    else:
                        product['image'] = ''
                
                # Extract product link
                if self.selectors.get('link'):
                    link_elem = container.select_one(self.selectors['link'])
                    if link_elem:
                        link_href = link_elem.get('href')
                        if link_href:
                            product['link'] = self.normalize_url(link_href)
                        else:
                            product['link'] = ''
                    else:
                        product['link'] = ''
                
                # Only add product if it has at least name and price
                if product.get('name') and product.get('price'):
                    # Check for duplicates based on name and price
                    is_duplicate = any(
                        p.get('name') == product['name'] and p.get('price') == product['price']
                        for p in self.all_products
                    )
                    if not is_duplicate:
                        products.append(product)
                
            except Exception as e:
                print(f"Error extracting product: {e}")
                continue
        
        return products
    
    async def scrape_page(self, url: str) -> tuple[List[Dict], List[str], List[str]]:
        """Scrape a single page and return products, pagination links, and category links"""
        if url in self.visited_urls:
            return [], [], []
        
        self.visited_urls.add(url)
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return [], [], []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract products
                products = self.extract_products_from_page(soup, url)
                
                # Find pagination links
                pagination_links = self.find_pagination_links(soup, url)
                
                # Find category links
                category_links = self.find_category_links(soup)
                
                return products, pagination_links, category_links
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return [], [], []
    
    async def scrape_all_products(self, start_url: str, follow_categories: bool = True, follow_pagination: bool = True) -> List[Dict]:
        """Scrape all products from the website"""
        urls_to_visit = [start_url]
        category_urls = []
        
        page_count = 0
        
        while urls_to_visit and page_count < self.max_pages and len(self.all_products) < self.max_products:
            current_url = urls_to_visit.pop(0)
            
            print(f"Scraping page {page_count + 1}: {current_url}")
            
            # Scrape current page
            products, pagination_links, new_category_links = await self.scrape_page(current_url)
            
            # Add new products
            self.all_products.extend(products)
            
            # Add new category URLs if following categories
            if follow_categories:
                for cat_url in new_category_links:
                    if cat_url not in self.visited_urls and cat_url not in category_urls:
                        category_urls.append(cat_url)
            
            # Add pagination URLs if following pagination
            if follow_pagination:
                for pag_url in pagination_links:
                    if pag_url not in self.visited_urls and pag_url not in urls_to_visit:
                        urls_to_visit.append(pag_url)
            
            # If no more pagination URLs, start visiting category URLs
            if not urls_to_visit and follow_categories and category_urls:
                urls_to_visit = category_urls[:10]  # Limit to prevent too many requests
                category_urls = category_urls[10:]
            
            page_count += 1
            
            # Delay between requests
            if self.delay > 0:
                await asyncio.sleep(self.delay)
        
        return self.all_products

# Auto-detection endpoint for intelligent selector detection


if __name__ == "__main__":
    import uvicorn

    # HOST: default 127.0.0.1 (fewer Windows socket permission issues than 0.0.0.0). Use HOST=0.0.0.0 for LAN access.
    # PORT: if 8000 is busy, set PORT=8001 (stop the old server first — see netstat).
    # UVICORN_RELOAD=1 to enable auto-reload (can trigger WinError 10013 on some setups if port is already taken).
    _host = os.environ.get("HOST", "127.0.0.1")
    _port = int(os.environ.get("PORT", "8000"))
    _reload = os.environ.get("UVICORN_RELOAD", "").strip().lower() in ("1", "true", "yes", "on")

    uvicorn.run("main:app", host=_host, port=_port, reload=_reload)
