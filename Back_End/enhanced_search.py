#!/usr/bin/env python3
"""
Enhanced Smart Barcode Search - Advanced Price & Name Extraction
"""

import asyncio
import aiohttp
import sqlite3
import json
import re
import hashlib
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import logging
import unicodedata
from urllib.parse import urljoin, urlparse
import time
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Structured extraction result"""
    name: str = ""
    price: str = ""
    reference: str = ""
    description: str = ""
    image_url: str = ""
    confidence: float = 0.0
    extraction_method: str = ""
    is_product_page: bool = False
    page_type: str = "unknown"

class EnhancedBarcodeSearcher:
    def __init__(self):
        self.session = None
        self.cache = {}
        self.verified_sites = {
            'pharma-shop.tn': {'priority': 1, 'reliability': 0.95},
            'parapharmacie.tn': {'priority': 2, 'reliability': 0.92},
            'paraexpert.tn': {'priority': 3, 'reliability': 0.88},
            'parashop.tn': {'priority': 4, 'reliability': 0.85},
            'paramust.tn': {'priority': 5, 'reliability': 0.82},
            'mlpara.tn': {'priority': 6, 'reliability': 0.78},
            'parafendri.tn': {'priority': 7, 'reliability': 0.72},
            'parazone.otospexerp.com': {'priority': 8, 'reliability': 0.65},
            'parapharmacieplus.tn': {'priority': 9, 'reliability': 0.62},
            'lifepara.tn': {'priority': 10, 'reliability': 0.58},
            'maparatunisie.tn': {'priority': 11, 'reliability': 0.55}
        }
        
        # Advanced product page indicators
        self.product_page_indicators = {
            'schema_markers': [
                '[itemtype*="Product"]',
                '[itemtype*="product"]',
                '[itemprop="name"]',
                '[itemprop="price"]',
                '[itemprop="description"]'
            ],
            'class_patterns': [
                r'product[-_]?(detail|page|single|info|view)',
                r'produit[-_]?(detail|page|single|info|view)',
                r'item[-_]?(detail|page|single|info|view)',
                r'product[-_]?container',
                r'product[-_]?main',
                r'product[-_]?content'
            ],
            'id_patterns': [
                r'product[-_]?(detail|page|single|info|view)',
                r'produit[-_]?(detail|page|single|info|view)',
                r'item[-_]?(detail|page|single|info|view)'
            ],
            'url_patterns': [
                r'/product/',
                r'/produit/',
                r'/item/',
                r'product_id=',
                r'productid=',
                r'pid=',
                r'id=.*product',
                r'route=product'
            ],
            'negative_indicators': [
                'search', 'category', 'categorie', 'list', 'grid', 'catalog', 'catalogue',
                'shop', 'boutique', 'results', 'resultats'
            ]
        }
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30, connect=15)
        connector = aiohttp.TCPConnector(limit=25, limit_per_host=10)
        
        self.session = aiohttp.ClientSession(
            timeout=timeout, connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def normalize_text(self, text: str) -> str:
        """Advanced text normalization with Unicode handling"""
        if not text:
            return ""
        text = unicodedata.normalize('NFKC', text.strip())
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text
    
    def analyze_page_type(self, soup: BeautifulSoup, url: str, site_name: str) -> Dict[str, any]:
        """Comprehensive page type analysis"""
        analysis = {
            'is_product_page': False,
            'confidence': 0.0,
            'indicators_found': [],
            'negative_indicators_found': [],
            'page_type': 'unknown'
        }
        
        url_lower = url.lower()
        page_text = soup.get_text().lower()
        
        # Check schema.org markup
        schema_indicators = 0
        for selector in self.product_page_indicators['schema_markers']:
            if soup.select(selector):
                schema_indicators += 1
                analysis['indicators_found'].append(f"schema:{selector}")
        
        if schema_indicators > 0:
            analysis['confidence'] += 0.4
            analysis['is_product_page'] = True
        
        # Check class patterns
        class_indicators = 0
        for pattern in self.product_page_indicators['class_patterns']:
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            if elements:
                class_indicators += 1
                analysis['indicators_found'].append(f"class:{pattern}")
        
        if class_indicators > 0:
            analysis['confidence'] += 0.3
        
        # Check URL patterns
        url_indicators = 0
        for pattern in self.product_page_indicators['url_patterns']:
            if re.search(pattern, url_lower):
                url_indicators += 1
                analysis['indicators_found'].append(f"url:{pattern}")
        
        if url_indicators > 0:
            analysis['confidence'] += 0.3
        
        # Check for negative indicators
        negative_count = 0
        for indicator in self.product_page_indicators['negative_indicators']:
            if indicator in url_lower or indicator in page_text:
                negative_count += 1
                analysis['negative_indicators_found'].append(indicator)
        
        if negative_count > 2:
            analysis['confidence'] -= 0.4
        
        # Determine page type
        if analysis['confidence'] >= 0.6:
            analysis['page_type'] = 'product_page'
            analysis['is_product_page'] = True
        elif analysis['confidence'] >= 0.3:
            analysis['page_type'] = 'likely_product_page'
        elif 'search' in url_lower or 'recherche' in url_lower:
            analysis['page_type'] = 'search_page'
        else:
            analysis['page_type'] = 'unknown'
        
        analysis['confidence'] = max(0.0, min(1.0, analysis['confidence']))
        return analysis
    
    def extract_price_smart(self, soup: BeautifulSoup, config: Dict, site_name: str) -> Tuple[str, float]:
        """Smart price extraction with confidence scoring"""
        candidates = []
        
        # Strategy 1: Use configured selectors
        for selector in config['selectors'].get('product_price', []):
            try:
                elements = soup.select(selector)
                for element in elements:
                    price_text = self.normalize_text(element.get_text())
                    if price_text:
                        price, confidence = self.parse_price_smart(price_text, element)
                        if price:
                            candidates.append((price, confidence, f"selector:{selector}"))
            except Exception as e:
                logger.warning(f"Error with price selector '{selector}': {e}")
                continue
        
        # Strategy 2: Look for price elements with specific attributes
        price_attributes = [
            {'class': re.compile(r'price|amount|cost|prix', re.I)},
            {'itemprop': 'price'},
            {'data-price': True},
            {'data-amount': True}
        ]
        
        for attrs in price_attributes:
            elements = soup.find_all(['span', 'div', 'p', 'strong', 'b'], attrs=attrs)
            for element in elements:
                price_text = self.normalize_text(element.get_text())
                if price_text:
                    price, confidence = self.parse_price_smart(price_text, element)
                    if price:
                        candidates.append((price, confidence, f"attribute:{attrs}"))
        
        # Strategy 3: Look for structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    price = data.get('price') or data.get('offers', {}).get('price')
                    if price:
                        price, confidence = self.parse_price_smart(str(price), None)
                        if price:
                            candidates.append((price, confidence, "structured_data"))
            except:
                continue
        
        # Select best candidate
        if candidates:
            candidates.sort(key=lambda x: (x[1], x[2].startswith('selector')), reverse=True)
            best_price, best_confidence, method = candidates[0]
            
            if self.validate_price_smart(best_price, soup):
                return best_price, best_confidence
        
        return "", 0.0
    
    def parse_price_smart(self, price_text: str, element: Optional[BeautifulSoup]) -> Tuple[str, float]:
        """Advanced price parsing with better validation"""
        if not price_text:
            return "", 0.0
        
        # Clean the price text
        price_text = re.sub(r'[^\d.,\s]', '', price_text)
        price_text = price_text.strip()
        
        # Extract numbers and separators
        price_match = re.search(r'(\d+(?:[.,]\d{1,3})*)', price_text)
        if not price_match:
            return "", 0.0
        
        price_value = price_match.group(1)
        
        # Validate price range (reasonable for parapharmacie products)
        try:
            numeric_price = float(price_value.replace(',', '.'))
            if numeric_price < 0.1 or numeric_price > 5000:  # More reasonable range for parapharmacie
                return "", 0.0
            
            # Additional validation for suspicious prices
            if numeric_price > 1000 and numeric_price < 10000:  # Suspicious range
                return "", 0.0
                
        except ValueError:
            return "", 0.0
        
        # Format with DT
        formatted_price = f"{price_value} DT"
        
        # Calculate confidence based on price format
        confidence = 0.8
        if re.match(r'^\d+[.,]\d{2}$', price_value):  # XX.XX format
            confidence = 1.0
        elif re.match(r'^\d+$', price_value):  # Whole number
            confidence = 0.9
        
        return formatted_price, confidence
    
    def validate_price_smart(self, price: str, soup: BeautifulSoup) -> bool:
        """Advanced price validation with multiple checks"""
        if not price:
            return False
        
        # Check if price contains digits
        if not re.search(r'\d', price):
            return False
        
        # Extract numeric value
        price_match = re.search(r'(\d+(?:[.,]\d{1,3})*)', price)
        if not price_match:
            return False
        
        try:
            numeric_price = float(price_match.group(1).replace(',', '.'))
            
            # Check reasonable price range for parapharmacie products
            if numeric_price < 0.1 or numeric_price > 5000:
                return False
            
            # Additional validation for suspicious prices
            if numeric_price > 1000 and numeric_price < 10000:  # Suspicious range
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'^\d{1,2}$',  # Too small (1-99)
                r'^\d{6,}$',   # Too large (100000+)
                r'^0+\.\d+$',  # Very small decimals
            ]
            
            for pattern in suspicious_patterns:
                if re.match(pattern, str(numeric_price)):
                    return False
                    
        except ValueError:
            return False
        
        return True
    
    def extract_product_name_smart(self, soup: BeautifulSoup, config: Dict, site_name: str) -> Tuple[str, float]:
        """Smart product name extraction with confidence scoring"""
        candidates = []
        
        # Strategy 1: Use configured selectors
        for selector in config['selectors'].get('product_name', []):
            try:
                elements = soup.select(selector)
                for element in elements:
                    name_text = self.normalize_text(element.get_text())
                    if name_text and len(name_text) > 10:
                        confidence = self.calculate_name_confidence_smart(name_text, element, soup)
                        if confidence > 0.3:
                            candidates.append((name_text, confidence, f"selector:{selector}"))
            except Exception as e:
                logger.warning(f"Error with name selector '{selector}': {e}")
                continue
        
        # Strategy 2: Look for structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    name = data.get('name') or data.get('title')
                    if name:
                        name_text = self.normalize_text(name)
                        if name_text and len(name_text) > 10:
                            confidence = self.calculate_name_confidence_smart(name_text, None, soup)
                            if confidence > 0.3:
                                candidates.append((name_text, confidence, "structured_data"))
            except:
                continue
        
        # Strategy 3: Look for H1 tags with product indicators
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            name_text = self.normalize_text(h1.get_text())
            if name_text and len(name_text) > 10:
                confidence = self.calculate_name_confidence_smart(name_text, h1, soup)
                if confidence > 0.3:
                    candidates.append((name_text, confidence, "h1_tag"))
        
        # Select best candidate
        if candidates:
            candidates.sort(key=lambda x: (x[1], x[2].startswith('selector')), reverse=True)
            best_name, best_confidence, method = candidates[0]
            
            if not self.is_generic_name_smart(best_name):
                return best_name, best_confidence
        
        return "", 0.0
    
    def calculate_name_confidence_smart(self, name: str, element: Optional[BeautifulSoup], soup: BeautifulSoup) -> float:
        """Calculate confidence score for a product name"""
        if not name or len(name) < 10:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Length factor
        if 20 <= len(name) <= 100:
            confidence += 0.2
        elif len(name) > 100:
            confidence += 0.1
        
        # Product indicators
        product_keywords = ['mg', 'ml', 'g', 'kg', 'comprimé', 'comprimés', 'capsule', 'capsules', 'sirop', 'gel', 'crème', 'lotion']
        if any(keyword in name.lower() for keyword in product_keywords):
            confidence += 0.2
        
        # Brand recognition
        common_brands = ['paracetamol', 'aspirin', 'vitamin', 'vitamine', 'omega', 'probiotic', 'probiotique']
        if any(brand in name.lower() for brand in common_brands):
            confidence += 0.1
        
        # Element type factor
        if element:
            if element.name == 'h1':
                confidence += 0.2
            elif element.get('itemprop') == 'name':
                confidence += 0.3
            elif 'title' in str(element.get('class', [])).lower():
                confidence += 0.1
        
        # Check for generic names
        generic_patterns = [
            r'^[a-z\s]+(?:votre|your)\s+[a-z\s]+(?:en ligne|online)',
            r'^[a-z\s]+(?:pharmacie|parapharmacie)',
            r'^[a-z\s]+(?:shop|boutique)',
            r'^[a-z\s]+(?:store|magasin)'
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, name.lower()):
                confidence -= 0.5
        
        return max(0.0, min(1.0, confidence))
    
    def is_generic_name_smart(self, name: str) -> bool:
        """SIMPLIFIED generic name detection - only filter obvious junk"""
        if not name:
            return True
        
        name_lower = name.lower().strip()
        
        # Check for very short names
        if len(name.strip()) < 5:
            return True
        
        # Check for names that are just numbers or symbols
        if re.match(r'^[\d\s\-_\.]+$', name):
            return True
        
        # Check for names that are too long
        if len(name.strip()) > 200:
            return True
        
        # Only filter EXACT matches of obvious navigation/UI elements
        generic_names = [
            'résultats de la recherche',
            'search results',
            'accueil',
            'home',
            'menu',
            'navigation',
            'footer',
            'header'
        ]
        
        # Check for exact generic name matches
        if name_lower in generic_names:
            return True
        
        # Check if name contains breadcrumb separators (like "Accueil / Shop / ...")
        if '/' in name and name.count('/') >= 2:
            return True
        
        return False 
    
    async def search_barcode_enhanced(self, barcode: str) -> List[Dict]:
        """Enhanced barcode search with smart extraction and quality filtering"""
        logger.info(f"Starting enhanced search for barcode: {barcode}")
        
        if not self.validate_barcode(barcode):
            logger.warning(f"Invalid barcode format: {barcode}")
            return []
        
        cache_key = f"enhanced_barcode:{barcode}"
        if cache_key in self.cache:
            logger.info("Returning cached results")
            return self.cache[cache_key]
        
        site_configs = self.get_site_configurations()
        prioritized_sites = self.prioritize_sites_enhanced(barcode, site_configs)
        results = await self.search_sites_parallel_enhanced(barcode, prioritized_sites)
        verified_results = self.verify_results_enhanced(results, barcode)
        
        self.cache[cache_key] = verified_results
        
        logger.info(f"Enhanced search completed. Found {len(verified_results)} verified results")
        return verified_results
    
    def validate_barcode(self, barcode: str) -> bool:
        """Validate barcode format"""
        if not barcode or not isinstance(barcode, str):
            return False
        
        clean_barcode = re.sub(r'[\s\-_\.]', '', barcode)
        return re.match(r'^\d{8,14}$', clean_barcode) is not None
    
    def get_site_configurations(self) -> Dict:
        """Get site configurations from database"""
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', 'app.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT site_name, search_url, selectors FROM sites')
            sites = cursor.fetchall()
            
            configs = {}
            for site_name, search_url, selectors in sites:
                if site_name in self.verified_sites:
                    try:
                        parsed_selectors = json.loads(selectors) if selectors else {}
                        configs[site_name] = {
                            'search_url': search_url,
                            'selectors': parsed_selectors,
                            'priority': self.verified_sites[site_name]['priority'],
                            'reliability': self.verified_sites[site_name]['reliability']
                        }
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON selectors for {site_name}, skipping")
                        continue
            
            conn.close()
            logger.info(f"Loaded {len(configs)} site configurations")
            return configs
            
        except Exception as e:
            logger.error(f"Error loading site configurations: {e}")
            return {}
    
    def prioritize_sites_enhanced(self, barcode: str, site_configs: Dict) -> List[tuple]:
        """Enhanced site prioritization"""
        prioritized = []
        
        for site_name, config in site_configs.items():
            score = config['reliability']
            
            selector_count = len(config['selectors'].get('product_name', [])) + \
                           len(config['selectors'].get('product_price', []))
            if selector_count > 3:
                score += 0.1
            
            search_url = config['search_url'].lower()
            if 'search' in search_url or 'recherche' in search_url:
                score += 0.05
            
            prioritized.append((site_name, config, score))
        
        prioritized.sort(key=lambda x: x[2], reverse=True)
        return prioritized
    
    async def search_sites_parallel_enhanced(self, barcode: str, prioritized_sites: List[tuple]) -> List[Dict]:
        """Enhanced parallel search"""
        semaphore = asyncio.Semaphore(10)
        
        async def search_single_site(site_info):
            site_name, config, score = site_info
            async with semaphore:
                try:
                    logger.info(f"Searching {site_name} (score: {score:.2f})")
                    result = await self.search_site_enhanced(site_name, config, barcode)
                    if result:
                        logger.info(f"✓ {site_name} found product: {result.get('nom', 'no name')[:50]}")
                    else:
                        logger.info(f"✗ {site_name} found nothing")
                    return result
                except Exception as e:
                    logger.error(f"Error searching {site_name}: {e}")
                    return None
        
        tasks = [search_single_site(site_info) for site_info in prioritized_sites]
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=35
            )
        except asyncio.TimeoutError:
            logger.warning("Search timeout reached")
            results = []
        
        valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        return valid_results
    
    async def search_site_enhanced(self, site_name: str, config: Dict, barcode: str) -> Optional[Dict]:
        """Enhanced single site search"""
        search_url = config['search_url'].format(barcode=barcode)
        
        try:
            for attempt in range(3):
                try:
                    async with self.session.get(search_url, ssl=False) as response:
                        if response.status == 200:
                            html = await response.text()
                            break
                        elif response.status in [404, 403, 429]:
                            logger.info(f"{site_name}: HTTP {response.status}")
                            return None
                        else:
                            logger.warning(f"{site_name}: HTTP {response.status}")
                            if attempt < 2:
                                await asyncio.sleep(1)
                                continue
                            return None
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {site_name}: {e}")
                    if attempt < 2:
                        await asyncio.sleep(1)
                        continue
                    return None
            else:
                return None
            
            if not self.barcode_in_content_enhanced(html, barcode):
                logger.info(f"Barcode not found in {site_name} content")
                return None
            
            soup = BeautifulSoup(html, 'lxml')
            result = await self.extract_product_enhanced(soup, site_name, search_url, config, barcode)
            
            if result:
                result['site_name'] = site_name
                result['search_url'] = search_url
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching {site_name}: {e}")
            return None
    
    def barcode_in_content_enhanced(self, html: str, barcode: str) -> bool:
        """Enhanced barcode content detection"""
        if not html or not barcode:
            return False
        
        # Check for exact barcode match
        if barcode in html:
            return True
        
        # Check for barcode with common separators
        separators = [' ', '-', '_', '.', '']
        for sep in separators:
            if sep.join(barcode) in html:
                return True
        
        return False
    
    async def extract_product_enhanced(self, soup: BeautifulSoup, site_name: str, url: str, config: Dict, barcode: str) -> Optional[Dict]:
        """Simplified product extraction - NO page analysis, just extract"""
        
        # Try to extract directly from the current page
        result = self.extract_from_page_simple(soup, site_name, url, config, barcode)
        if result:
            logger.info(f"{site_name}: ✓ Extracted product from main page")
            return result
        
        # If nothing found, try product links
        product_links = self.find_product_links_enhanced(soup, site_name, config)
        
        if product_links:
            logger.info(f"{site_name}: Trying {len(product_links[:2])} product links")
            for product_url in product_links[:2]:
                if not product_url.startswith('http'):
                    product_url = urljoin(url, product_url)
                
                try:
                    async with self.session.get(product_url, ssl=False) as response:
                        if response.status == 200:
                            product_html = await response.text()
                            product_soup = BeautifulSoup(product_html, 'lxml')
                            
                            result = self.extract_from_page_simple(product_soup, site_name, product_url, config, barcode)
                            if result:
                                logger.info(f"{site_name}: ✓ Extracted product from link: {product_url}")
                                return result
                except Exception as e:
                    logger.warning(f"Error fetching product page {product_url}: {e}")
                    continue
        
        logger.info(f"{site_name}: ✗ No product extracted")
        return None
    
    def find_product_links_enhanced(self, soup: BeautifulSoup, site_name: str, config: Dict) -> List[str]:
        """Enhanced product link finding with better validation"""
        product_links = []
        
        # First try configured selectors
        for selector in config['selectors'].get('product_links', []):
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and self.is_valid_product_link_enhanced(href, site_name):
                    product_links.append(href)
        
        # If no links found, try common product link patterns
        if not product_links:
            # Look for links with product indicators in href or text
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                link_text = link.get_text(strip=True).lower()
                
                if href and self.is_valid_product_link_enhanced(href, site_name):
                    # Additional validation for specific sites
                    if self.validate_link_for_site(href, link_text, site_name):
                        product_links.append(href)
        
        # Remove duplicates and limit results
        unique_links = list(dict.fromkeys(product_links))  # Preserve order while removing duplicates
        return unique_links[:3]
    
    def is_valid_product_link_enhanced(self, href: str, site_name: str) -> bool:
        """Enhanced product link validation"""
        href_lower = href.lower()
        
        product_indicators = ['.html', '/product', '/produit', 'route=product', 'id=', 'pid=']
        has_product_indicator = any(indicator in href_lower for indicator in product_indicators)
        
        excluded_patterns = ['category', 'tag', 'shop', 'categorie', 'search', 'blog', 'cart', 'login']
        has_excluded = any(pattern in href_lower for pattern in excluded_patterns)
        
        return has_product_indicator and not has_excluded
    
    def validate_link_for_site(self, href: str, link_text: str, site_name: str) -> bool:
        """Advanced site-specific link validation with comprehensive filtering"""
        href_lower = href.lower()
        link_text_lower = link_text.lower()
        
        # Comprehensive exclusion patterns for all sites
        exclusion_patterns = [
            # Navigation and UI elements
            'category', 'categorie', 'brand', 'marque', 'manufacturer', 'fabricant',
            'search', 'recherche', 'filter', 'filtre', 'sort', 'trier', 'order', 'commande',
            'page', 'pagination', 'next', 'prev', 'previous', 'first', 'last',
            'cart', 'panier', 'checkout', 'commande', 'account', 'compte', 'profile',
            'login', 'register', 'inscription', 'signup', 'signin', 'logout',
            'contact', 'about', 'a-propos', 'nous', 'team', 'equipe',
            'faq', 'help', 'aide', 'support', 'terms', 'conditions', 'privacy', 'confidentialite',
            'wishlist', 'favoris', 'compare', 'comparer', 'newsletter', 'news', 'blog',
            'home', 'accueil', 'index', 'main', 'principal',
            'footer', 'header', 'nav', 'menu', 'sidebar', 'side',
            'banner', 'advertisement', 'pub', 'promo', 'promotion',
            'sale', 'solde', 'discount', 'reduction', 'offer', 'offre',
            'new', 'nouveau', 'featured', 'en-vedette', 'popular', 'populaire',
            'best', 'meilleur', 'top', 'trending', 'tendance',
            'info', 'information', 'details', 'detail', 'spec', 'specification',
            'review', 'avis', 'comment', 'commentaire', 'rating', 'note',
            'share', 'partager', 'social', 'facebook', 'twitter', 'instagram',
            'print', 'imprimer', 'email', 'mail', 'pdf', 'download', 'telecharger',
            'print', 'imprimer', 'email', 'mail', 'pdf', 'download', 'telecharger',
            'rss', 'feed', 'sitemap', 'plan', 'map', 'carte',
            'language', 'langue', 'fr', 'en', 'ar', 'arabic', 'english', 'french',
            'currency', 'devise', 'tnd', 'eur', 'usd', 'dollar', 'euro',
            'size', 'taille', 'color', 'couleur', 'variant', 'variante',
            'stock', 'disponibilite', 'availability', 'in-stock', 'out-of-stock',
            'shipping', 'livraison', 'delivery', 'livraison', 'pickup', 'retrait',
            'return', 'retour', 'refund', 'remboursement', 'exchange', 'echange',
            'warranty', 'garantie', 'guarantee', 'certification', 'certificat',
            'ingredient', 'ingredient', 'composition', 'dosage', 'posologie',
            'side-effect', 'effet-secondaire', 'contraindication', 'interaction',
            'storage', 'conservation', 'expiry', 'expiration', 'date',
            'batch', 'lot', 'serial', 'numero', 'code', 'barcode', 'ean',
            'weight', 'poids', 'volume', 'dimension', 'mesure',
            'package', 'emballage', 'packaging', 'box', 'boite', 'bottle', 'bouteille',
            'tablet', 'comprime', 'capsule', 'gelule', 'syrup', 'sirop',
            'cream', 'creme', 'gel', 'lotion', 'oil', 'huile', 'spray',
            'supplement', 'complement', 'vitamin', 'vitamine', 'mineral', 'minerai',
            'herbal', 'plante', 'natural', 'naturel', 'organic', 'bio',
            'prescription', 'ordonnance', 'otc', 'sans-ordonnance',
            'generic', 'generique', 'brand', 'marque', 'original', 'original',
            'import', 'importe', 'local', 'locale', 'tunisian', 'tunisien',
            'pharmacy', 'pharmacie', 'parapharmacy', 'parapharmacie', 'drugstore',
            'medical', 'medical', 'health', 'sante', 'beauty', 'beaute',
            'cosmetic', 'cosmetique', 'personal-care', 'soin-personnel',
            'baby', 'bebe', 'child', 'enfant', 'adult', 'adulte', 'senior', 'senior',
            'men', 'homme', 'women', 'femme', 'unisex', 'unisexe',
            'skin', 'peau', 'hair', 'cheveux', 'face', 'visage', 'body', 'corps',
            'dental', 'dentaire', 'oral', 'buccal', 'eye', 'oeil', 'vision', 'vision',
            'ear', 'oreille', 'nose', 'nez', 'throat', 'gorge', 'respiratory', 'respiratoire',
            'digestive', 'digestif', 'cardiovascular', 'cardiovasculaire',
            'immune', 'immunitaire', 'nervous', 'nerveux', 'endocrine', 'endocrinien',
            'musculoskeletal', 'musculo-squelettique', 'reproductive', 'reproductif',
            'urinary', 'urinaire', 'lymphatic', 'lymphatique', 'integumentary', 'tegumentaire'
        ]
        
        # Check for exclusion patterns
        for pattern in exclusion_patterns:
            if pattern in href_lower or pattern in link_text_lower:
                return False
        
        # Required product patterns (must have at least one)
        required_product_patterns = [
            '/product/', '/produit/', '/item/', '/article/', '/goods/', '/marchandise/',
            'product_id=', 'productid=', 'pid=', 'id=', 'item_id=', 'itemid=',
            '.html', '.php', '.asp', '.aspx', '.jsp', '.jspx',
            'route=product', 'route=produit', 'route=item', 'route=article',
            'c=product', 'c=produit', 'c=item', 'c=article',
            'page=product', 'page=produit', 'page=item', 'page=article',
            'view=product', 'view=produit', 'view=item', 'view=article',
            'action=product', 'action=produit', 'action=item', 'action=article',
            'module=product', 'module=produit', 'module=item', 'module=article',
            'controller=product', 'controller=produit', 'controller=item', 'controller=article'
        ]
        
        has_product_pattern = any(pattern in href_lower for pattern in required_product_patterns)
        if not has_product_pattern:
            return False
        
        # URL structure validation
        if len(href) < 15:  # Too short
            return False
        
        if href_lower.count('/') < 3:  # Must have sufficient path depth
            return False
        
        # Suspicious patterns that indicate non-product pages
        suspicious_patterns = [
            'javascript:', 'mailto:', 'tel:', '#', '?s=', '?q=', '?search=', '?recherche=',
            'admin', 'wp-admin', 'wp-content', 'wp-includes', 'administrator',
            'cgi-bin', 'cgi', 'bin', 'tmp', 'temp', 'cache', 'session',
            'error', '404', '403', '500', 'maintenance', 'maintenance',
            'test', 'demo', 'example', 'sample', 'placeholder',
            'api', 'rest', 'json', 'xml', 'rss', 'feed', 'sitemap',
            'robots', 'favicon', 'apple-touch', 'manifest', 'service-worker',
            'analytics', 'tracking', 'pixel', 'beacon', 'gtm', 'ga',
            'cdn', 'static', 'assets', 'images', 'css', 'js', 'fonts',
            'upload', 'download', 'file', 'document', 'pdf', 'doc', 'xls',
            'backup', 'restore', 'import', 'export', 'sync', 'synchronize',
            'cron', 'job', 'task', 'queue', 'worker', 'daemon',
            'log', 'debug', 'development', 'staging', 'beta', 'alpha',
            'version', 'v1', 'v2', 'api-v1', 'api-v2', 'legacy', 'old',
            'mobile', 'm.', 'www.', 'secure.', 'ssl.', 'https://',
            'redirect', 'forward', 'proxy', 'gateway', 'bridge',
            'webhook', 'callback', 'notification', 'alert', 'message',
            'socket', 'websocket', 'ws://', 'wss://', 'ftp://', 'sftp://',
            'database', 'db', 'mysql', 'postgresql', 'mongodb', 'redis',
            'server', 'host', 'domain', 'subdomain', 'wildcard',
            'wildcard', 'catch-all', 'default', 'fallback', 'error'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in href_lower:
                return False
        
        # Additional validation for specific problematic sites (removed cleopatre.tn and laparadulac.com)
        # No extra validation needed for remaining sites
        
        return True
    
    def extract_from_page_simple(self, soup: BeautifulSoup, site_name: str, url: str, config: Dict, barcode: str) -> Optional[Dict]:
        """SIMPLE extraction - just get name and price, no confidence checks"""
        
        # Extract name using configured selectors
        name = ""
        for selector in config['selectors'].get('product_name', []):
            try:
                elements = soup.select(selector)
                for element in elements:
                    name_text = self.normalize_text(element.get_text())
                    if name_text and len(name_text) > 10:
                        name = name_text
                        break
                if name:
                    break
            except:
                continue
        
        # If no name from selectors, try h1 tags
        if not name:
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags:
                name_text = self.normalize_text(h1.get_text())
                if name_text and len(name_text) > 10:
                    name = name_text
                    break
        
        logger.info(f"{site_name}: Extracted name='{name[:50] if name else 'NONE'}'")
        
        if not name:
            return None
        
        # Extract price
        price = ""
        for selector in config['selectors'].get('product_price', []):
            try:
                elements = soup.select(selector)
                for element in elements:
                    price_text = self.normalize_text(element.get_text())
                    if price_text:
                        price_match = re.search(r'(\d+(?:[.,]\d{1,3})*)', price_text)
                        if price_match:
                            price = f"{price_match.group(1)} DT"
                            break
                if price:
                    break
            except:
                continue
        
        logger.info(f"{site_name}: Extracted price='{price if price else 'NONE'}'")
        
        # Extract other fields
        reference = barcode
        description = self.extract_description_enhanced(soup, config)
        image_url = self.extract_image_enhanced(soup, config, url)
        logo_url = self.get_site_logo_enhanced(site_name)
        
        return {
            'nom': name,
            'prix': price,
            'reference': reference,
            'description': description,
            'photo': image_url,
            'logo': logo_url,
            'site_name': site_name,
            'lien': url
        } 
    
    def extract_reference_enhanced(self, soup: BeautifulSoup, config: Dict) -> str:
        """Enhanced reference extraction"""
        for selector in config['selectors'].get('product_reference', []):
            element = soup.select_one(selector)
            if element:
                ref = element.get_text(strip=True)
                if ref and len(ref) > 5:
                    return ref
        
        # Look for reference in structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    ref = data.get('sku') or data.get('mpn') or data.get('gtin')
                    if ref:
                        return str(ref)
            except:
                continue
        
        return ""
    
    def extract_description_enhanced(self, soup: BeautifulSoup, config: Dict) -> str:
        """Enhanced description extraction"""
        for selector in config['selectors'].get('product_description', []):
            element = soup.select_one(selector)
            if element:
                desc = self.normalize_text(element.get_text())
                if desc and len(desc) > 20:
                    return desc
        
        # Look for description in structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    desc = data.get('description')
                    if desc:
                        return self.normalize_text(desc)
            except:
                continue
        
        return ""
    
    def extract_image_enhanced(self, soup: BeautifulSoup, config: Dict, base_url: str) -> str:
        """Enhanced image extraction"""
        for selector in config['selectors'].get('product_image', []):
            element = soup.select_one(selector)
            if element:
                img_src = element.get('src') or element.get('data-src')
                if img_src and not self.is_logo_image_enhanced(img_src):
                    return self.make_absolute_url_enhanced(img_src, base_url)
        
        # Look for images in structured data
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    image = data.get('image')
                    if image:
                        if isinstance(image, list) and image:
                            image = image[0]
                        if isinstance(image, dict):
                            image = image.get('url')
                        if image and not self.is_logo_image_enhanced(image):
                            return self.make_absolute_url_enhanced(image, base_url)
            except:
                continue
        
        return ""
    
    def is_logo_image_enhanced(self, img_src: str) -> bool:
        """Enhanced logo image detection"""
        if not img_src:
            return True
        
        img_lower = img_src.lower()
        logo_indicators = ['logo', 'brand', 'header', 'nav', 'menu', 'banner']
        return any(indicator in img_lower for indicator in logo_indicators)
    
    def make_absolute_url_enhanced(self, url: str, base_url: str) -> str:
        """Enhanced URL making absolute"""
        if not url:
            return ""
        
        if url.startswith('http'):
            return url
        
        try:
            return urljoin(base_url, url)
        except:
            return url
    
    def get_site_logo_enhanced(self, site_name: str) -> str:
        """Enhanced site logo URL - Get from database"""
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', 'app.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT logo_url FROM sites WHERE site_name = ?', (site_name,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0]
            
            # Fallback to favicon if no logo found in database
            fallback_logos = {
                'pharma-shop.tn': 'https://pharma-shop.tn/favicon.ico',
                'parapharmacie.tn': 'https://parapharmacie.tn/favicon.ico',
                'paraexpert.tn': 'https://paraexpert.tn/favicon.ico',
                'parashop.tn': 'https://parashop.tn/favicon.ico',
                'paramust.tn': 'https://paramust.tn/favicon.ico',
                'mlpara.tn': 'https://mlpara.tn/favicon.ico',
                'parafendri.tn': 'https://parafendri.tn/favicon.ico',
                'parazone.otospexerp.com': 'https://parazone.otospexerp.com/favicon.ico',
                'parapharmacieplus.tn': 'https://parapharmacieplus.tn/favicon.ico',
                'lifepara.tn': 'https://lifepara.tn/favicon.ico',
                'maparatunisie.tn': 'https://maparatunisie.tn/favicon.ico'
            }
            return fallback_logos.get(site_name, '')
            
        except Exception as e:
            logger.warning(f"Error getting logo for {site_name}: {e}")
            return ''
    
    def verify_product_data_enhanced(self, product_data: Dict, barcode: str) -> bool:
        """Simplified product data verification - NO confidence filtering"""
        if not product_data:
            logger.info("Verification failed: No product data")
            return False
        
        # Check required fields
        required_fields = ['nom', 'site_name']
        for field in required_fields:
            if not product_data.get(field):
                logger.info(f"Verification failed: Missing field '{field}'")
                return False
        
        product_name = product_data.get('nom', '')
        site_name = product_data.get('site_name', '')
        
        # Check for generic names (still important to filter out junk)
        if self.is_generic_name_smart(product_name):
            logger.info(f"Verification failed: Generic name detected for {site_name}: '{product_name[:50]}'")
            return False
        
        # NO CONFIDENCE CHECKS - accept any product with a valid name
        logger.info(f"Verification passed for {site_name}: '{product_name[:50]}'")
        return True
    
    def calculate_confidence_enhanced(self, result: Dict, barcode: str) -> float:
        """Enhanced confidence calculation"""
        if not result:
            return 0.0
        
        confidence = 0.0
        
        # Base confidence from extraction
        name_confidence = result.get('name_confidence', 0)
        price_confidence = result.get('price_confidence', 0)
        page_confidence = result.get('page_confidence', 0)
        
        confidence += name_confidence * 0.4
        confidence += price_confidence * 0.3
        confidence += page_confidence * 0.2
        
        # Site reliability bonus
        site_reliability = result.get('site_reliability', 0.5)
        confidence += site_reliability * 0.1
        
        # Extraction method bonus
        extraction_method = result.get('extraction_method', '')
        if extraction_method == 'product_page':
            confidence += 0.1
        elif extraction_method == 'search_page':
            confidence += 0.05
        
        # Data quality bonus
        if result.get('nom') and len(result.get('nom', '')) > 20:
            confidence += 0.05
        
        if result.get('prix') and result.get('prix') != '':
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def verify_results_enhanced(self, results: List[Dict], barcode: str) -> List[Dict]:
        """Simplified results verification - NO confidence sorting"""
        if not results:
            logger.info("No results to verify")
            return []
        
        logger.info(f"Verifying {len(results)} results")
        
        # Filter out invalid results
        valid_results = []
        for result in results:
            site_name = result.get('site_name', 'unknown')
            product_name = result.get('nom', 'no name')
            
            if self.verify_product_data_enhanced(result, barcode):
                valid_results.append(result)
                logger.info(f"✓ ACCEPTED: {site_name} - {product_name[:50]}")
            else:
                logger.info(f"✗ REJECTED: {site_name} - {product_name[:50]}")
        
        # Remove duplicates based on site_name only
        unique_results = []
        seen_sites = set()
        
        for result in valid_results:
            site_name = result.get('site_name', '')
            if site_name not in seen_sites:
                unique_results.append(result)
                seen_sites.add(site_name)
        
        logger.info(f"Final: {len(unique_results)} unique results from {len(results)} total results")
        return unique_results

    def calculate_result_quality_score(self, result: Dict, barcode: str) -> float:
        """Calculate comprehensive quality score for search results"""
        if not result:
            return 0.0
        
        score = 0.0
        
        # Base confidence from extraction
        name_confidence = result.get('name_confidence', 0)
        price_confidence = result.get('price_confidence', 0)
        page_confidence = result.get('page_confidence', 0)
        overall_confidence = result.get('overall_confidence', 0)
        
        score += name_confidence * 0.3
        score += price_confidence * 0.25
        score += page_confidence * 0.2
        score += overall_confidence * 0.25
        
        # Site reliability bonus
        site_reliability = result.get('site_reliability', 0.5)
        score += site_reliability * 0.1
        
        # Data completeness bonus
        has_name = bool(result.get('nom', '').strip())
        has_price = bool(result.get('prix', '').strip())
        has_image = bool(result.get('photo', '').strip())
        has_description = bool(result.get('description', '').strip())
        
        if has_name and has_price:
            score += 0.15
        if has_image:
            score += 0.05
        if has_description:
            score += 0.05
        
        # Name quality bonus
        name = result.get('nom', '')
        if name:
            name_length = len(name.strip())
            if 20 <= name_length <= 150:  # Optimal length
                score += 0.1
            elif name_length > 150:  # Too long
                score -= 0.05
            
            # Check for product indicators in name
            product_indicators = ['mg', 'ml', 'g', 'kg', 'comprimé', 'comprimés', 'capsule', 'capsules', 'sirop', 'gel', 'crème', 'lotion']
            if any(indicator in name.lower() for indicator in product_indicators):
                score += 0.1
        
        # Price quality bonus
        price = result.get('prix', '')
        if price:
            # Check if price is reasonable
            price_match = re.search(r'(\d+(?:[.,]\d{1,3})*)', price)
            if price_match:
                try:
                    numeric_price = float(price_match.group(1).replace(',', '.'))
                    if 0.5 <= numeric_price <= 5000:  # Reasonable range
                        score += 0.1
                    elif numeric_price < 0.1 or numeric_price > 10000:
                        score -= 0.2
                except ValueError:
                    score -= 0.1
        
        # URL quality bonus
        url = result.get('lien', '')
        if url:
            if '/product/' in url.lower() or '/produit/' in url.lower():
                score += 0.05
            if len(url) > 30:  # Longer URLs often indicate product pages
                score += 0.05
        
        # Extraction method bonus
        extraction_method = result.get('extraction_method', '')
        if extraction_method == 'product_page':
            score += 0.1
        elif extraction_method == 'search_page':
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def filter_high_quality_results(self, results: List[Dict], barcode: str) -> List[Dict]:
        """Filter results to only include high-quality ones"""
        if not results:
            return []
        
        # Calculate quality scores
        scored_results = []
        for result in results:
            quality_score = self.calculate_result_quality_score(result, barcode)
            result['quality_score'] = quality_score
            scored_results.append(result)
        
        # Filter by minimum quality threshold
        min_quality_threshold = 0.4
        high_quality_results = [r for r in scored_results if r['quality_score'] >= min_quality_threshold]
        
        # Sort by quality score
        high_quality_results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Remove duplicates based on site and similar names
        unique_results = []
        seen_sites = set()
        seen_names = set()
        
        for result in high_quality_results:
            site_name = result.get('site_name', '')
            name = result.get('nom', '').lower().strip()
            
            # Check if we already have a result from this site
            if site_name in seen_sites:
                continue
            
            # Check for similar names (avoid duplicates with slight variations)
            is_duplicate_name = False
            for seen_name in seen_names:
                if self.names_are_similar(name, seen_name):
                    is_duplicate_name = True
                    break
            
            if not is_duplicate_name:
                unique_results.append(result)
                seen_sites.add(site_name)
                seen_names.add(name)
        
        logger.info(f"Filtered {len(unique_results)} high-quality results from {len(results)} total results")
        return unique_results
    
    def names_are_similar(self, name1: str, name2: str) -> bool:
        """Check if two product names are similar (potential duplicates)"""
        if not name1 or not name2:
            return False
        
        # Normalize names
        name1 = re.sub(r'\s+', ' ', name1.lower().strip())
        name2 = re.sub(r'\s+', ' ', name2.lower().strip())
        
        # Exact match
        if name1 == name2:
            return True
        
        # Check if one is contained in the other
        if name1 in name2 or name2 in name1:
            return True
        
        # Calculate similarity using simple ratio
        if len(name1) > 10 and len(name2) > 10:
            # Count common words
            words1 = set(name1.split())
            words2 = set(name2.split())
            common_words = words1.intersection(words2)
            
            if len(common_words) >= min(len(words1), len(words2)) * 0.7:
                return True
        
        return False 

async def search_barcode_enhanced(barcode: str) -> List[Dict]:
    """Main function to search barcode using enhanced system"""
    async with EnhancedBarcodeSearcher() as searcher:
        return await searcher.search_barcode_enhanced(barcode) 

async def search_barcodes_batch(barcodes: List[str], max_concurrent: int = 5) -> Dict[str, List[Dict]]:
    """Search multiple barcodes in batch with controlled concurrency"""
    logger.info(f"Starting batch search for {len(barcodes)} barcodes")
    
    # Validate barcodes
    valid_barcodes = [barcode for barcode in barcodes if re.match(r'^\d{8,14}$', re.sub(r'[\s\-_\.]', '', barcode))]
    invalid_barcodes = [barcode for barcode in barcodes if barcode not in valid_barcodes]
    
    if invalid_barcodes:
        logger.warning(f"Invalid barcodes found: {invalid_barcodes}")
    
    if not valid_barcodes:
        logger.warning("No valid barcodes to search")
        return {}
    
    # Create semaphore to limit concurrent searches
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def search_single_barcode(barcode: str) -> Tuple[str, List[Dict]]:
        async with semaphore:
            try:
                results = await search_barcode_enhanced(barcode)
                return barcode, results
            except Exception as e:
                logger.error(f"Error searching barcode {barcode}: {e}")
                return barcode, []
    
    # Execute searches in parallel
    tasks = [search_single_barcode(barcode) for barcode in valid_barcodes]
    
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=120  # 2 minutes timeout for batch
        )
    except asyncio.TimeoutError:
        logger.warning("Batch search timeout reached")
        results = []
    
    # Process results
    batch_results = {}
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Exception in batch search: {result}")
            continue
        
        barcode, search_results = result
        batch_results[barcode] = search_results
    
    logger.info(f"Batch search completed. Processed {len(batch_results)} barcodes")
    return batch_results

async def search_barcode_with_fallback(barcode: str) -> List[Dict]:
    """Search barcode with multiple fallback strategies"""
    logger.info(f"Starting search with fallback for barcode: {barcode}")
    
    # Primary search
    results = await search_barcode_enhanced(barcode)
    
    # If no results, try with different barcode formats
    if not results:
        logger.info("No results found, trying alternative barcode formats")
        
        # Try different barcode formats
        alternative_formats = []
        clean_barcode = re.sub(r'[\s\-_\.]', '', barcode)
        
        if len(clean_barcode) >= 8:
            # Try with different lengths
            for length in [8, 12, 13, 14]:
                if len(clean_barcode) >= length:
                    alternative_formats.append(clean_barcode[:length])
        
        # Try with common prefixes/suffixes
        if clean_barcode.startswith('0'):
            alternative_formats.append(clean_barcode[1:])
        if not clean_barcode.startswith('0') and len(clean_barcode) < 13:
            alternative_formats.append('0' + clean_barcode)
        
        # Remove duplicates
        alternative_formats = list(set(alternative_formats))
        
        # Try alternative formats
        for alt_format in alternative_formats[:3]:  # Limit to 3 alternatives
            if alt_format != clean_barcode:
                logger.info(f"Trying alternative format: {alt_format}")
                alt_results = await search_barcode_enhanced(alt_format)
                if alt_results:
                    results = alt_results
                    logger.info(f"Found results with alternative format: {alt_format}")
                    break
    
    return results