# barcode_search.py
# New comprehensive barcode search system with direct e-commerce lookups and Google API fallback

import requests
import urllib.parse
import re
import json
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import urllib3
from database import get_db
from models import Site
from sqlalchemy import text
from database import engine

# Suppress SSL warnings for scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
SEARCH_TIMEOUT = 10
PRODUCT_TIMEOUT = 15
MAX_PRODUCTS_PER_SITE = 5
MAX_RESULTS_TARGET = 20

# Google Custom Search API Configuration
GOOGLE_API_KEY = "AIzaSyCTdEYCSilNZIDsNRrTjpzIlzk7iCq0eRo"
GOOGLE_CSE_ID = "f51de7daff69a450a"

def get_dynamic_site_configs():
    """Load site configurations from database only. No hardcoded fallback."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT site_name, search_url, selectors, logo_url FROM sites"))
            sites = result.fetchall()
            configs = {}
            for site in sites:
                site_name = site[0]
                search_url = site[1]
                selectors = json.loads(site[2]) if site[2] else {}
                logo_url = site[3] if site[3] else None
                configs[site_name] = {
                    "search_url": search_url,
                    "selectors": selectors,
                    "logo_url": logo_url
                }
            return configs
    except Exception as e:
        print(f"[ERROR] Failed to load dynamic site configs from database: {e}")
        return {}  # No fallback, must fix DB if error

def get_all_site_configs() -> Dict:
    """
    Load site configurations ONLY from the database
    No hardcoded configurations
    """
    # Get dynamic configurations from database
    dynamic_configs = get_dynamic_site_configs()
    
    print(f"[DEBUG] Total sites available for search: {len(dynamic_configs)}")
    print(f"[DEBUG] Sites: {list(dynamic_configs.keys())}")
    
    return dynamic_configs

def validate_barcode(barcode: str) -> tuple[bool, str]:
    """
    Validate if the input is a proper barcode format
    Returns (is_valid, error_message)
    """
    if not barcode:
        return False, "Barcode cannot be empty"
    
    # Remove any spaces or special characters
    cleaned_barcode = re.sub(r'[^\w\-\.]', '', barcode)
    
    # Check if it's a website domain (contains .tn, .com, etc.)
    if re.search(r'\.(tn|com|net|org|fr|co|ma|dz|dz|ly|eg|sa|ae|qa|kw|bh|om|jo|lb|sy|iq|ir|tr|pk|in|bd|lk|np|mm|th|vn|ph|my|sg|id|au|nz|jp|kr|cn|tw|hk|mo|ru|ua|by|kz|uz|tm|tj|kg|af)$', cleaned_barcode.lower()):
        return False, f"'{cleaned_barcode}' appears to be a website domain, not a barcode. Please enter a numeric barcode (12-13 digits)."
    
    # Check if it's numeric (standard barcode format)
    if not cleaned_barcode.isdigit():
        return False, f"'{cleaned_barcode}' is not a valid barcode format. Barcodes should be numeric (12-13 digits)."
    
    # Check length (EAN-13: 13 digits, UPC: 12 digits, EAN-8: 8 digits)
    if len(cleaned_barcode) not in [8, 12, 13]:
        return False, f"'{cleaned_barcode}' has {len(cleaned_barcode)} digits. Valid barcodes have 8, 12, or 13 digits."
    
    return True, ""

# Site configurations are now loaded dynamically from the database
# No hardcoded configurations needed

def extract_text_content(element) -> str:
    """Extract text content from an element, handling nested elements"""
    if not element:
        return ""
    
    # Get text content, preserving line breaks
    text = element.get_text(separator=' ', strip=True)
    return text

def expand_read_more_content(soup: BeautifulSoup, site_name: str) -> str:
    """Try to expand 'Read More' content to get full descriptions"""
    expanded_content = ""
    
    # Look for common "Read More" patterns
    read_more_selectors = [
        ".read-more",
        ".readmore", 
        ".expand",
        ".show-more",
        ".more-content",
        ".full-content",
        ".description-full",
        ".product-description-full",
        "[data-toggle='collapse']",
        ".collapsible",
        ".expandable"
    ]
    
    for selector in read_more_selectors:
        elements = soup.select(selector)
        for elem in elements:
            # Check if it's a button/link that might expand content
            if elem.name in ['button', 'a', 'span']:
                # Look for the target content
                target_id = elem.get('data-target') or elem.get('href', '').lstrip('#')
                if target_id:
                    target_elem = soup.find(id=target_id)
                    if target_elem:
                        expanded_content = extract_text_content(target_elem)
                        print(f"[DEBUG] Found expanded content via {selector}: {len(expanded_content)} chars")
                        break
            
            # Check if it's already expanded content
            elif elem.get('class') and any('expanded' in cls.lower() for cls in elem.get('class', [])):
                expanded_content = extract_text_content(elem)
                print(f"[DEBUG] Found already expanded content via {selector}: {len(expanded_content)} chars")
                break
        
        if expanded_content:
            break
    
    return expanded_content

def is_valid_product(product_data: dict, barcode: str) -> bool:
    """
    Validate if the extracted product data is valid and not a generic search result
    """
    if not product_data:
        return False
    
    # Check if we have a product name
    nom = product_data.get('nom', '').strip()
    if not nom:
        return False
    
    # Reject generic search result text
    generic_indicators = [
        'rechercher',
        'recherche', 
        'search',
        'résultats',
        'resultats',
        'résultats de la recherche',
        'resultats de la recherche',
        'produit trouvé',
        'produits trouvés',
        'connexion',
        'connection',
        'panier',
        'compte',
        'catégorie',
        'category'
    ]
    
    nom_lower = nom.lower()
    for indicator in generic_indicators:
        if indicator in nom_lower:
            print(f"[DEBUG] Rejected generic name: '{nom}' (contains '{indicator}')")
            return False
    
    # Reject names that are just the barcode or search terms
    if nom == barcode or nom == f"Rechercher - {barcode}" or nom == f"Search - {barcode}":
        print(f"[DEBUG] Rejected barcode-only name: '{nom}'")
        return False
    
    # More lenient length check - accept shorter names
    if len(nom) < 5:
        print(f"[DEBUG] Rejected very short name: '{nom}' (length: {len(nom)})")
        return False
    
    # Accept any name that's not generic, even if it doesn't contain product keywords
    print(f"[DEBUG] Accepted product name: '{nom}'")
    return True

def extract_image_url(soup, site_name, search_url, selectors):
    """Extract product image with improved logic"""
    photo = ""
    
    # First try to extract from current page
    for selector in selectors.get('product_image', []):
        elements = soup.select(selector)
        for element in elements:
            img_src = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
            if img_src:
                # Skip logo-like images
                img_alt = element.get('alt', '').lower()
                img_class = element.get('class', [])
                img_class_str = ' '.join(img_class).lower()
                
                # Skip if it looks like a logo
                if any(word in img_alt for word in ['logo', 'brand', 'header', 'banner']) or \
                   any(word in img_class_str for word in ['logo', 'brand', 'header', 'banner', 'nav', 'menu']) or \
                   any(word in img_src.lower() for word in ['logo', 'brand', 'header', 'banner', 'nav', 'menu', 'en-tete', 'entete']):
                    continue
                
                # Convert relative URLs to absolute
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    base_url = '/'.join(search_url.split('/')[:3])
                    img_src = base_url + img_src
                elif not img_src.startswith('http'):
                    base_url = '/'.join(search_url.split('/')[:-1])
                    img_src = base_url + '/' + img_src
                
                photo = img_src
                break
        if photo:
            break
    
    # If no image found on current page, try broader search
    if not photo:
        all_images = soup.find_all('img')
        for img in all_images:
            img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if img_src:
                img_alt = img.get('alt', '').lower()
                img_class = img.get('class', [])
                img_class_str = ' '.join(img_class).lower()
                
                # Skip logo-like images
                if any(word in img_alt for word in ['logo', 'brand', 'header', 'banner']) or \
                   any(word in img_class_str for word in ['logo', 'brand', 'header', 'banner', 'nav', 'menu']) or \
                   any(word in img_src.lower() for word in ['logo', 'brand', 'header', 'banner', 'nav', 'menu', 'en-tete', 'entete']):
                    continue
                
                # Look for product-related keywords
                if any(word in img_alt for word in ['product', 'produit', 'image', 'photo', 'svr', 'xerial']) or \
                   any(word in img_class_str for word in ['product', 'produit', 'image', 'photo']):
                    # Convert relative URLs to absolute
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        base_url = '/'.join(search_url.split('/')[:3])
                        img_src = base_url + img_src
                    elif not img_src.startswith('http'):
                        base_url = '/'.join(search_url.split('/')[:-1])
                        img_src = base_url + '/' + img_src
                    
                    photo = img_src
                    break
    
    return photo

def extract_product_details(soup, site_name, search_url, selectors, logo_url=None):
    """
    Extract product details from a product page
    """
    try:
        # Extract product name with improved logic
        nom = ""
        
        # First, try to find product names in actual product links (most reliable)
        for selector in selectors.get('product_links', []):
            links = soup.select(selector)
            for link in links:
                link_text = link.get_text(strip=True)
                href = link.get("href", "")
                
                # Skip if this looks like a search result or navigation text
                if link_text and len(link_text) > 10:
                    if not any(generic in link_text.lower() for generic in [
                        'rechercher', 'recherche', 'search', 'result', 'résultats', 
                        'produit trouvé', 'produits trouvés', 'connexion', 'panier',
                        'compte', 'catégorie', 'category', 'menu', 'navigation'
                    ]):
                        # Check if this looks like a product name
                        if any(word in link_text.lower() for word in ['svr', 'xerial', 'crème', 'pieds', 'creme']):
                            nom = link_text
                            break
            if nom:
                break
        
        # If no good name found in links, try product name selectors
        if not nom:
            for selector in selectors.get('product_name', []):
                element = soup.select_one(selector)
                if element:
                    extracted_name = element.get_text(strip=True)
                    # Skip search result text and ensure it's a meaningful product name
                    if extracted_name and len(extracted_name) > 10:
                        if not any(word in extracted_name.lower() for word in [
                            'résultats', 'recherche', 'search', 'result', 'produit trouvé', 
                            'produits trouvés', 'rechercher', 'connexion', 'panier'
                        ]):
                            nom = extracted_name
                            break
        
        # If still no good name, try to find product names in headings
        if not nom:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                heading_text = heading.get_text(strip=True)
                if heading_text and len(heading_text) > 10:
                    if not any(word in heading_text.lower() for word in [
                        'résultats', 'recherche', 'search', 'result', 'rechercher'
                    ]):
                        if any(word in heading_text.lower() for word in ['svr', 'xerial', 'crème', 'pieds']):
                            nom = heading_text
                            break
        
        # Extract price
        prix = ""
        for selector in selectors.get('product_price', []):
            element = soup.select_one(selector)
            if element:
                prix = element.get_text(strip=True)
                if prix and len(prix) > 2:  # Ensure it's a meaningful price
                    break
        
        # Extract reference
        reference = ""
        for selector in selectors.get('product_reference', []):
            element = soup.select_one(selector)
            if element:
                reference = element.get_text(strip=True)
                if reference and len(reference) > 2:
                    break
        
        # Extract description
        description = ""
        for selector in selectors.get('product_description', []):
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                if description and len(description) > 20:
                    break
        
        # Extract image with improved logic
        photo = extract_image_url(soup, site_name, search_url, selectors)
        
        # Use logo from database if available
        logo = logo_url if logo_url else ""
        
        return {
            'nom': nom,
            'prix': prix,
            'reference': reference,
            'description': description,
            'photo': photo,
            'logo': logo,
            'site_name': site_name,
            'lien': search_url
        }
    except Exception as e:
        print(f"[ERROR] Failed to extract product details from {site_name}: {e}")
        return None

def search_barcode_on_sites(barcode):
    """
    Search for a barcode across multiple e-commerce sites
    """
    print(f"[DEBUG] Starting barcode search for: {barcode}")
    
    # Step 1: Load dynamic site configurations from database
    print("\n" + "=" * 60)
    print("STEP 1: DIRECT E-COMMERCE SITE SEARCH")
    print("=" * 60)
    
    site_configs = get_dynamic_site_configs()
    print(f"[DEBUG] Total sites available for search: {len(site_configs)}")
    print(f"[DEBUG] Sites: {list(site_configs.keys())}")
    
    results = []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Step 2: Search each site
    for site_name, config in site_configs.items():
        try:
            print(f"\n[DEBUG] Checking site: {site_name}")
            
            # Construct search URL
            search_url = config["search_url"].format(barcode=barcode)
            print(f"[DEBUG] Search URL: {search_url}")
            
            # Make request
            response = session.get(search_url, timeout=SEARCH_TIMEOUT, verify=False)
            if response.status_code != 200:
                print(f"[DEBUG] ❌ Failed to load {site_name}: HTTP {response.status_code}")
                continue
            
            print(f"[DEBUG] ✓ Successfully loaded {site_name}")
            
            # Check if barcode exists on the page
            if barcode not in response.text:
                print(f"[DEBUG] ❌ Barcode {barcode} not found on {site_name}")
                continue
            
            print(f"[DEBUG] {site_name} - ✓ Barcode {barcode} found in page content!")
            
            # Parse the page
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Step 3: Check if we're on a product page or search results page
            product_links = []
            
            # First, check if we're already on a product page (direct product URL)
            is_product_page = False
            product_page_indicators = [
                'h1[itemprop="name"]', '.product-title', '.product-name',
                '[class*="product-detail"]', '[class*="product-page"]'
            ]
            
            # Check for search result indicators to avoid false positives
            search_result_indicators = [
                'Résultats de la recherche', 'Search results', 'Résultats',
                '.search-results', '.results', '.search-list'
            ]
            
            # Check if it's a search results page first
            is_search_results = False
            for indicator in search_result_indicators:
                if soup.find(text=lambda text: text and indicator in text):
                    is_search_results = True
                    print(f"[DEBUG] {site_name} - ⚠️ Search results page detected: {indicator}")
                    break
            
            # Only check for product page if it's not a search results page
            if not is_search_results:
                for indicator in product_page_indicators:
                    if soup.select_one(indicator):
                        is_product_page = True
                        print(f"[DEBUG] {site_name} - ✓ Direct product page detected")
                        break
            
            # Additional check: if URL contains product-specific patterns, it's likely a product page
            if not is_product_page and not is_search_results:
                product_url_patterns = ['/produit/', '/product/', '/shop/', '/item/', '/article/']
                if any(pattern in search_url.lower() for pattern in product_url_patterns):
                    is_product_page = True
                    print(f"[DEBUG] {site_name} - ✓ Direct product page detected (URL pattern)")
            
            # Special handling for parapharmacie.tn and paraexpert.tn - treat as direct product pages
            if site_name in ["parapharmacie.tn", "paraexpert.tn"] and barcode in response.text:
                is_product_page = True
                print(f"[DEBUG] {site_name} - ✓ Direct product page detected (special handling)")
            
            if is_product_page:
                # We're already on a product page, but check if it's the right product
                print(f"[DEBUG] {site_name} - ✓ Direct product page detected")
                
                # Check if the barcode exists on this product page
                if barcode in response.text:
                    print(f"[DEBUG] {site_name} - ✓ Barcode confirmed on product page, extracting data...")
                    product_data = extract_product_details(soup, site_name, search_url, config["selectors"], config.get("logo_url"))
                    if product_data and is_valid_product(product_data, barcode):
                        results.append(product_data)
                        print(f"[DEBUG] ✓ Added product from {site_name}: {product_data.get('nom', 'Unknown')}")
                    else:
                        print(f"[DEBUG] ❌ Product validation failed for {site_name}")
                else:
                    print(f"[DEBUG] {site_name} - ❌ Barcode not found on product page, skipping...")
                continue
            
            # If not a product page, look for search results
            print(f"[DEBUG] {site_name} - Looking for search results...")
            
            # First, try to find the search results container
            search_results_selectors = [
                '.search-results', '.results', '.products', '.product-list', 
                '.search-list', '.results-list', '.product-grid', '.search-grid',
                '[class*="search"]', '[class*="result"]', '[class*="product"]',
                '.iqitsearch-results', '.searchiqit-results', '.search-results-wrapper'
            ]
            
            search_container = None
            for selector in search_results_selectors:
                search_container = soup.select_one(selector)
                if search_container:
                    print(f"[DEBUG] {site_name} - Found search container: {selector}")
                    break
            # PATCH: For pharma-shop.tn, always search the whole page
            if site_name == "pharma-shop.tn":
                search_container = None  # Always search the whole page for product links
            
            # If we found a search container, only look for product links within it
            if search_container:
                # Check if the search container is too broad (has too many links)
                all_links_in_container = search_container.find_all('a', href=True)
                if len(all_links_in_container) > 50:  # If container has too many links, it's probably the whole page
                    print(f"[DEBUG] {site_name} - Search container too broad ({len(all_links_in_container)} links), using fallback method")
                    search_container = None
                else:
                    print(f"[DEBUG] {site_name} - Found search container: {selector}")
                    for selector in config["selectors"].get("product_links", []):
                        try:
                            # Only search within the search results container
                            links = search_container.select(selector)
                            for link in links:
                                href = link.get("href", "")
                                if href:
                                    # Make URL absolute if needed
                                    if href.startswith("/"):
                                        href = f"https://{site_name}{href}"
                                    elif not href.startswith("http"):
                                        href = f"https://{site_name}/{href}"
                                    
                                    # Only include actual product links
                                    if any(indicator in href.lower() for indicator in ['.html', '/product', '/produit', 'route=product']):
                                        if not any(exclude in href.lower() for exclude in ['category', 'tag', 'shop', 'categorie', 'search']):
                                            product_links.append(href)
                                    # Also include links that contain the barcode (these are definitely product links)
                                    elif barcode in href:
                                        product_links.append(href)
                        except Exception as e:
                            print(f"[DEBUG] Error with selector {selector}: {e}")
                            continue
            
            # If no search container or container was too broad, use fallback method
            if not search_container:
                print(f"[DEBUG] {site_name} - Using fallback method (no search container or container too broad)")
                for selector in config["selectors"].get("product_links", []):
                    try:
                        links = soup.select(selector)
                        for link in links:
                            href = link.get("href", "")
                            if href:
                                # Make URL absolute if needed
                                if href.startswith("/"):
                                    href = f"https://{site_name}{href}"
                                elif not href.startswith("http"):
                                    href = f"https://{site_name}/{href}"
                                
                                # In the fallback method, patch the filtering for parapharmacieplus.tn
                                if any(indicator in href.lower() for indicator in ['.html', '/product', '/produit', 'route=product']):
                                    link_text = link.get_text(strip=True).lower()
                                    if site_name == "parapharmacieplus.tn":
                                        product_links.append(href)  # Accept all links found by the selector
                                    else:
                                        excludes = ['category', 'tag', 'categorie', 'search', 'blog', 'page']
                                        if site_name != "pharma-shop.tn":
                                            excludes.append('shop')
                                        if not any(exclude in href.lower() for exclude in excludes):
                                            if not any(exclude in link_text for exclude in ['recherche', 'search', 'catégorie', 'category', 'menu', 'connexion', 'panier']):
                                                product_links.append(href)
                                # Also include links that contain the barcode (these are definitely product links)
                                elif barcode in href:
                                    product_links.append(href)
                    except Exception as e:
                        print(f"[DEBUG] Error with selector {selector}: {e}")
                        continue
            
            # After the fallback selector search for product_links (after line 558)
            if site_name == "parapharmacieplus.tn":
                print(f"[DEBUG] parapharmacieplus.tn - All product_links found by selectors:")
                for selector in config["selectors"].get("product_links", []):
                    links = soup.select(selector)
                    for link in links:
                        href = link.get("href", "")
                        print(f"  Selector: {selector} | Href: {href} | Text: {link.get_text(strip=True)}")

            # If still no product links found, try a more aggressive search
            if not product_links:
                print(f"[DEBUG] {site_name} - No product links found with selectors, trying aggressive search...")
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if href and barcode in href:
                        # Make URL absolute if needed
                        if href.startswith("/"):
                            href = f"https://{site_name}{href}"
                        elif not href.startswith("http"):
                            href = f"https://{site_name}/{href}"
                        
                        # Filter out social media and external links
                        if any(external in href.lower() for external in ['facebook.com', 'twitter.com', 'pinterest.com', 'wa.me', 'whatsapp.com', 'instagram.com']):
                            continue
                        
                        # Only add if it looks like a product link
                        if any(indicator in href.lower() for indicator in ['.html', '/product', '/produit', 'route=product']):
                            if not any(exclude in href.lower() for exclude in ['category', 'tag', 'shop', 'categorie', 'search']):
                                product_links.append(href)
                                print(f"[DEBUG] {site_name} - Found product link with aggressive search: {href}")
            
            # Remove duplicates
            product_links = list(set(product_links))
            print(f"[DEBUG] {site_name} - Found {len(product_links)} product links")
            
            # Step 4: More flexible logic - if barcode exists on page, try to extract product info
            if barcode in response.text:
                print(f"[DEBUG] {site_name} - ✓ Barcode found on page, attempting extraction...")
                
                # Try to extract product details directly from the search page
                product_data = extract_product_details(soup, site_name, search_url, config["selectors"], config.get("logo_url"))
                
                if product_data and is_valid_product(product_data, barcode):
                    results.append(product_data)
                    print(f"[DEBUG] ✓ Added product from {site_name}: {product_data.get('nom', 'Unknown')}")
                else:
                    print(f"[DEBUG] ❌ Direct extraction failed for {site_name}")
                    
                    # If direct extraction failed but barcode exists, try to find any product link
                    if product_links:
                        print(f"[DEBUG] {site_name} - Trying to extract from product links...")
                        for product_url in product_links[:3]:  # Try first 3 links
                            try:
                                product_data = extract_product_details_from_url(session, product_url, site_name, config["selectors"], config.get("logo_url"))
                                if product_data and is_valid_product(product_data, barcode):
                                    results.append(product_data)
                                    print(f"[DEBUG] ✓ Added product from {site_name} via link: {product_data.get('nom', 'Unknown')}")
                                    break
                            except Exception as e:
                                print(f"[DEBUG] Error extracting from {product_url}: {e}")
                                continue
                    else:
                        print(f"[DEBUG] {site_name} - No product links found, but barcode exists on page")
            else:
                print(f"[DEBUG] {site_name} - ❌ Barcode not found on page")
            
        except Exception as e:
            print(f"[DEBUG] ❌ Error processing {site_name}: {e}")
            continue
    
    # Step 5: Improve image extraction - prioritize pharma-shop.tn
    pharma_shop_image = None
    for result in results:
        if result.get('site_name') == 'pharma-shop.tn' and result.get('photo'):
            pharma_shop_image = result.get('photo')
            break
    
    # If pharma-shop.tn has an image, use it for sites without images
    if pharma_shop_image:
        for result in results:
            if not result.get('photo') or result.get('photo') == 'N/A':
                result['photo'] = pharma_shop_image
                print(f"[DEBUG] Using pharma-shop.tn image for {result.get('site_name')}")
    
    print(f"\n[DEBUG] Search completed. Found {len(results)} total results.")
    
    # Step 6: Use longest description
    if results:
        longest_desc = max(results, key=lambda x: len(x.get('description', '')))
        best_description = longest_desc.get('description', '')
        print(f"[DEBUG] Using longest description from {len(best_description)} chars")
        
        for result in results:
            result['description'] = best_description
    
    print(f"[DEBUG] Final results count: {len(results)}")
    return results

def barcode_exists_on_page(session, url, barcode):
    """Check if barcode exists on a given page"""
    try:
        response = session.get(url, timeout=PRODUCT_TIMEOUT, verify=False)
        if response.status_code == 200:
            return barcode in response.text
        return False
    except Exception as e:
        print(f"[DEBUG] Error checking barcode on {url}: {e}")
        return False

def extract_product_details_from_url(session, url, site_name, selectors, logo_url=None):
    """Extract product details from a specific URL"""
    try:
        response = session.get(url, timeout=PRODUCT_TIMEOUT, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return extract_product_details(soup, site_name, url, selectors, logo_url)
        return None
    except Exception as e:
        print(f"[DEBUG] Error extracting details from {url}: {e}")
        return None

def search_with_google_api(barcode: str) -> List[Dict]:
    """Search using Google Custom Search API as fallback with enhanced Tunisian site targeting"""
    print(f"[DEBUG] Using Google Custom Search API for barcode: {barcode}")
    
    try:
        # Enhanced list of Tunisian pharmacy sites
        tunisian_sites = [
            "pharma-shop.tn", "parafendri.tn", "maparatunisie.tn", "paranet.tn",
            "lifepara.tn", "drest.tn", "parashop.tn", "parapharmaciebardo.tn",
            "parapharmacie.tn", "med-coast.tn", "paraexpert.tn",
            "parapara.tn", "parapharmacieplus.tn", "paraland.tn", "parazone.tn",
            "cosmetica.tn", "mypharmacy.tn", "amal-medical.com", "1001para.tn",
            "cleopatre.tn", "cosmetique.tn", "paramust.tn"
        ]
        
        # Create site-specific queries for better results
        site_queries = []
        for site in tunisian_sites:
            site_queries.append(f'site:{site} "{barcode}"')
        
        # Also try a general Tunisian search
        site_queries.append(f'site:tn "{barcode}"')
        
        all_results = []
        
        for query in site_queries:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': GOOGLE_API_KEY,
                    'cx': GOOGLE_CSE_ID,
                    'q': query,
                    'num': 5  # Limit per query to avoid rate limits
                }
                response = requests.get(url, params=params, timeout=SEARCH_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    print(f"[DEBUG] Google API returned {len(items)} results for query: {query}")
                    for item in items:
                        try:
                            page_url = item.get('link', '')
                            page_title = item.get('title', '')
                            # Skip if we already have this URL
                            if any(r.get('lien') == page_url for r in all_results):
                                continue
                            print(f"[DEBUG] Checking Google result: {page_url}")
                            # Fetch the page to verify barcode presence
                            page_response = requests.get(page_url, timeout=PRODUCT_TIMEOUT, verify=False)
                            if page_response.status_code == 200 and barcode in page_response.text:
                                print(f"[DEBUG] ✓ Barcode confirmed on Google result: {page_url}")
                                # Extract basic info from the page
                                page_soup = BeautifulSoup(page_response.text, "html.parser")
                                # Try to extract image from meta tags or first img
                                img_elem = page_soup.select_one("img[src*='http']")
                                product_image = extract_image_url(img_elem) if img_elem else ""
                                # Try to extract price
                                price_elem = page_soup.select_one(".price, [class*='price'], [class*='prix']")
                                product_price = extract_text_content(price_elem) if price_elem else ""
                                # Extract site name from URL
                                from urllib.parse import urlparse
                                parsed_url = urlparse(page_url)
                                site_name = parsed_url.netloc
                                all_results.append({
                                    "nom": page_title,
                                    "prix": product_price,
                                    "photo": product_image,
                                    "reference": barcode,
                                    "disponibilite": "Disponible",
                                    "description": item.get('snippet', ''),
                                    "lien": page_url,
                                    "site_name": site_name
                                })
                        except Exception as e:
                            print(f"[DEBUG] Error processing Google result: {str(e)}")
                            continue
                else:
                    print(f"[DEBUG] Google API error for query '{query}': HTTP {response.status_code}")
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            except Exception as e:
                print(f"[DEBUG] Error with Google API query '{query}': {str(e)}")
                continue
        print(f"[DEBUG] Total Google results found: {len(all_results)}")
        return all_results
    
    except Exception as e:
        print(f"[DEBUG] Error with Google API: {str(e)}")
        return []# Legacy function for compatibility
def scrape_product_details(soup: BeautifulSoup, url: str, selectors: dict = None) -> Dict:
    """Legacy function for compatibility with existing code"""
    # Extract basic info without specific selectors
    name_elem = soup.select_one("h1, .product-title, .product-name")
    price_elem = soup.select_one(".price, [class*='price'], [class*='prix']")
    img_elem = soup.select_one("img[src*='http']")
    
    return {
        "nom": extract_text_content(name_elem),
        "prix": extract_text_content(price_elem),
        "photo": extract_image_url(img_elem),
        "reference": "",
        "disponibilite": "Disponible",
        "description": "",
        "lien": url,
        "site_name": "Unknown Site"
    } 

if __name__ == "__main__":
    # Test the barcode search functionality
    test_barcode = "3662361001705"
    print(f"Testing barcode search for: {test_barcode}")
    
    # Validate the barcode format
    is_valid, error_message = validate_barcode(test_barcode)
    if not is_valid:
        print(f"Error: {error_message}")
        exit()
    
    # Search for the barcode
    results = search_barcode_on_sites(test_barcode)
    
    # Step 2: Use the best description from all results
    if results:
        # Find the longest description to use as the best one
        best_description = ""
        best_length = 0
        
        for result in results:
            desc = result.get('description', '')
            if len(desc) > best_length:
                best_description = desc
                best_length = len(desc)
        
        if best_description:
            print(f"[DEBUG] Using longest description from {best_length} chars")
            # Update all results to use the best description
            for result in results:
                result['description'] = best_description
        
        # Step 2.5: Improve image extraction - prioritize pharma-shop.tn
        pharma_shop_image = None
        for result in results:
            if result.get('site_name') == 'pharma-shop.tn' and result.get('photo'):
                pharma_shop_image = result.get('photo')
                break
        
        # If pharma-shop.tn has an image, use it for sites without images
        if pharma_shop_image:
            for result in results:
                if not result.get('photo') or result.get('photo') == 'N/A':
                    result['photo'] = pharma_shop_image
                    print(f"[DEBUG] Using pharma-shop.tn image for {result.get('site_name')}")
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS ({len(results)} found)")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('nom', 'Unknown Product')}")
        print(f"   Site: {result.get('site_name', 'Unknown')}")
        print(f"   Price: {result.get('prix', 'N/A')}")
        print(f"   Reference: {result.get('reference', 'N/A')}")
        print(f"   URL: {result.get('lien', 'N/A')}")
        print(f"   Image: {result.get('photo', 'N/A')}")
        print(f"   Description: {result.get('description', 'N/A')[:100]}...") 