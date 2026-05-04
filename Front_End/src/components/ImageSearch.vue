<template>
  <div class="app-container" :dir="direction">
    <!-- Navigation Bar -->
    <Navigation @language-changed="handleLanguageChange" @direction-changed="handleDirectionChange" />

    <div class="content-wrapper">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>{{ t.searchTools }}</h3>
        </div>
        <div class="sidebar-menu">
          <div class="menu-section">
            <h4>{{ t.productSearch }}</h4>
            <ul>
              <li class="menu-item" @click="$router.push('/barcode-search')">
                <svg viewBox="0 0 24 24">
                  <path d="M2 6H4V18H2V6ZM5 6H6V18H5V6ZM7 6H10V18H7V6ZM11 6H12V18H11V6ZM13 6H14V18H13V6ZM16 6H17V18H16V6ZM18 6H19V18H18V6ZM20 6H22V18H20V6Z" fill="currentColor"/>
                </svg>
                {{ t.barcodeSearch }}
              </li>
              <li class="menu-item active">
                <svg viewBox="0 0 24 24">
                  <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="currentColor"/>
                </svg>
                {{ t.imageSearch }}
              </li>
            </ul>
          </div>
          <div class="menu-section">
            <h4>{{ t.analyses }}</h4>
            <ul>
              <li class="menu-item" @click="$router.push('/reports')">
                <svg viewBox="0 0 24 24">
                  <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19ZM17 12H7V10H17V12ZM13 16H7V14H13V16ZM17 8H7V6H17V8Z" fill="currentColor"/>
                </svg>
                {{ t.reports }}
              </li>
              <li class="menu-item" @click="$router.push('/statistics')">
                <svg viewBox="0 0 24 24">
                  <path d="M16 6L18.29 8.29L13.41 13.17L9.41 9.17L2 16.59L3.41 18L9.41 12L13.41 16L19.71 9.71L22 12V6H16Z" fill="currentColor"/>
                </svg>
                {{ t.statistics }}
              </li>
            </ul>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <div class="content-header">
          <h1>{{ t.imageSearchTitle }}</h1>
          <p class="content-subtitle">{{ t.imageSearchSubtitle }}</p>
        </div>
        
                <div class="image-search-container">

                     <!-- Image Upload Section -->
           <div class="upload-section">
             <div class="upload-options vertical-upload-options">
               <button @click="openWebcam" class="webcam-btn centered-webcam-btn">
                 {{ t.takePhotoWithWebcam }}
               </button>
               <span class="upload-divider horizontal-divider">{{ t.or }}</span>
               <div class="upload-area" 
                    @click="triggerFileInput" 
                    @dragover.prevent 
                    @drop.prevent="handleDrop"
                    @dragover="handleDragOver"
                    @dragleave="handleDragLeave"
                    :class="{ 'drag-over': isDragOver }">
                 <input 
                   ref="fileInput" 
                   type="file" 
                   accept="image/*" 
                   @change="handleFileSelect" 
                   style="display: none;"
                 />
                 
                 <div v-if="!selectedImage" class="upload-placeholder">
                   <div class="upload-icon">📷</div>
                   <p>{{ t.uploadImageText }}</p>
                   <p class="upload-hint">{{ t.uploadImageHint }}</p>
                 </div>
                 
                 <div v-else class="image-preview">
                   <img :src="selectedImage" :alt="t.uploadedImage" class="preview-img" />
                   <button
                     @click.stop="removeImage"
                     class="remove-btn"
                     aria-label="Remove photo"
                     title="Remove photo"
                   >
                     ✖
                   </button>
                 </div>
               </div>
             </div>
           </div>

           <!-- Webcam Modal -->
           <div v-if="showWebcam" class="webcam-modal">
             <div class="webcam-container">
               <div class="webcam-header">
                 <h3>{{ t.takePhotoWithWebcam }}</h3>
                 <button @click="closeWebcam" class="close-webcam-btn">×</button>
               </div>
               
               <div class="webcam-content">
                 <video ref="webcamVideo" autoplay playsinline class="webcam-video"></video>
                 <canvas ref="webcamCanvas" style="display: none;"></canvas>
                 
                 <div class="webcam-controls">
                   <button @click="capturePhoto" class="capture-btn">
                     <span class="capture-icon">📸</span>
                     {{ t.capturePhoto }}
                   </button>
                   <button @click="closeWebcam" class="cancel-btn">{{ t.cancel }}</button>
                 </div>
                 
                 <div v-if="capturedPhoto" class="captured-preview">
                   <img :src="capturedPhoto" :alt="t.capturedPhoto" class="captured-img" />
                   <div class="captured-actions">
                     <button @click="useCapturedPhoto" class="use-photo-btn">{{ t.useThisPhoto }}</button>
                     <button @click="retakePhoto" class="retake-btn">{{ t.retakePhoto }}</button>
                   </div>
                 </div>
               </div>
             </div>
           </div>

          <!-- Extracted Text Display -->
          <div v-if="extractedText" class="extracted-text-section">
            <h3>{{ t.extractedText }}</h3>
            <div class="text-display">
              <p>{{ extractedText }}</p>
              <button @click="editText" class="edit-btn">{{ t.editText }}</button>
            </div>
          </div>

          <!-- Search Button -->
          <button 
            @click="searchProducts" 
            :disabled="!hasValidImage || loading" 
            class="search-btn"
            :class="{ 'search-btn-ready': hasValidImage && !loading }"
          >
            <span v-if="loading" class="search-loading">{{ t.searching }}</span>
            <span v-else-if="!hasValidImage">{{ t.uploadImageFirst }}</span>
            <span v-else>{{ t.searchProducts }}</span>
          </button>



          <!-- Loading & Error States -->
          <div v-if="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>{{ t.processingImage }}</p>
            
            <!-- Enhanced Progress Indicator -->
            <div v-if="searchProgress.currentStep" class="search-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: searchProgressPercentage + '%' }"></div>
              </div>
              <p class="progress-text">{{ searchProgress.currentStep }}</p>
              <p class="progress-percentage">{{ searchProgressPercentage }}%</p>
            </div>
          </div>

          <!-- Image Processing Status -->
          <div v-if="selectedImage && !loading && !hasSearched" class="processing-status">
            <div class="status-item">
              <span class="status-icon">✅</span>
              <span>{{ t.readyForSearch }}</span>
            </div>
          </div>



          <div v-if="error" class="error" @click="clearError">
            <span class="error-icon">⚠️</span>
            <span>{{ error }}</span>
            <span class="close-error">×</span>
          </div>

          <!-- Results Section -->
          <div v-if="results.length > 0" class="results-section">

            <!-- Product Summary Panel -->
            <div class="product-summary-card" v-if="primaryDetection">
              <div class="summary-image-col" v-if="selectedImage">
                <img :src="selectedImage" alt="Produit" class="summary-img" />
              </div>
              <div class="summary-details-col">
                <h2 class="summary-title">{{ primaryDetection.product_text_clean || extractedText }}</h2>
                <p class="summary-desc" v-if="primaryDetection.description">{{ primaryDetection.description }}</p>
                
                <div class="summary-meta" v-if="priceRange">
                  <div class="meta-item">
                    <div class="meta-text">
                      <span class="meta-value" style="font-size: 1.4rem; color: #2b6cb0;">{{ priceRange.min.toFixed(3) }} <small style="font-size: 1rem">DT</small> - {{ priceRange.max.toFixed(3) }} <small style="font-size: 1rem">DT</small></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="results-header">
              <h2 class="results-title">{{ t.searchResults }}</h2>
              <!-- Save to Reports Button (right side) -->
              <button
                @click="saveImageReport"
                class="save-report-btn"
                :class="{ saved: reportSaved }"
                id="save-image-report-btn"
              >
                <span v-if="reportSaved">{{ t.savedToReports }}</span>
                <span v-else>{{ t.saveToReports }}</span>
              </button>
            </div>

            <!-- Filters -->
            <div class="filters">
              <label class="stock-filter">
                <input type="checkbox" v-model="filterInStock" />
                {{ t.showInStockOnly }}
              </label>
            </div>

            <!-- Results Cards -->
            <div class="product-cards">
              <div 
                v-for="(result, index) in filteredResults" 
                :key="index" 
                class="product-card"
                :class="{ 'lowest-price-card': priceRange && extractNumericPrice(result.prix) === priceRange.min }"
              >
                <!-- Lowest Price Badge -->
                <div v-if="priceRange && extractNumericPrice(result.prix) === priceRange.min" class="lowest-price-badge">
                  🏆 Meilleur Prix
                </div>
                <div class="product-content">
                  <div class="top-row">
                    <div class="vendor-logo">
                      <img 
                        :src="getSiteLogo(result.site_name || result.site || getSiteName(result.lien || result.link))" 
                        :alt="result.site_name || result.site || getSiteName(result.lien || result.link)"
                        class="site-logo"
                        @error="handleLogoError"
                      />
                    </div>
                  </div>
                    
                  <div class="divider-line"></div>
                  
                  <div class="product-details-col">
                    <h4 class="product-name">{{ result.nom }}</h4>
                    
                    <div class="price-display">
                      <span class="price-value">{{ result.prix ? formatPrice(result.prix) : t.priceNotAvailable }}</span>
                    </div>
                    
                    <a :href="result.lien || result.link || result.url" target="_blank" class="view-offer-btn">
                      {{ t.viewOffer }}
                      <span class="btn-arrow">›</span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- No Results Message -->
          <div 
            v-if="results.length === 0 && hasSearched" 
            class="no-results-message"
          >
            {{ t.noResultsFound }}
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import Navigation from './Navigation.vue';
import { getCurrentTranslations } from '@/locales';

export default {
  name: 'ImageSearch',
  components: {
    Navigation
  },
  data() {
    return {
      selectedImage: null,
      extractedText: '',
      results: [],
      loading: false,
      error: '',
      isDragOver: false,
      hasSearched: false,
      filterInStock: false,
      currentLanguage: 'fr',
      showWebcam: false,
      capturedPhoto: null,
      webcamStream: null,
      direction: 'ltr',
      imageHash: null,
      searchProgress: {
        currentStep: '',
        progress: 0,
        totalSteps: 0
      },
      cacheEnabled: true,
      similarityThreshold: 0.88,
      brandFilter: true,
      maxResults: 20,
      showSettings: false,
      detections: [],
      reportSaved: false,
      cacheStats: {
        total: 0,
        size: 0,
        oldest: null,
        newest: null
      }
    };
  },
  mounted() {
    this.refreshCacheStats();
    this.loadSettingsFromAdmin();
  },
  computed: {
    t() {
      return getCurrentTranslations(this.currentLanguage);
    },
    filteredResults() {
      let results = [...this.results];

      if (this.filterInStock) {
        results = results.filter(result => this.isInStock(result.disponibilite));
      }

      // Brand filter: only keep results whose name contains the detected brand
      if (this.brandFilter && this.primaryDetection) {
        const cleanName = (this.primaryDetection.product_text_clean || '').toLowerCase();
        // Extract brand = first word(s) before ' - ' or first word
        let brandPart = cleanName.includes(' - ')
          ? cleanName.split(' - ')[0].trim()
          : cleanName.split(' ')[0].trim();
          
        // If there are multiple words (e.g. "eau thermale avène"), taking the last word ("avène") is safer for matching
        const brandWords = brandPart.split(' ');
        if (brandWords.length > 0) {
          brandPart = brandWords[brandWords.length - 1];
        }

        if (brandPart.length >= 2) {
          // Normalize accents for comparison (avène → avene, etc.)
          const normBrand = brandPart.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
          results = results.filter(r => {
            const nom = (r.nom || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
            return nom.includes(normBrand);
          });
        }
      }

      // Lowest price first
      results.sort((a, b) => {
        const pa = this.extractNumericPrice(a.prix);
        const pb = this.extractNumericPrice(b.prix);
        const na = Number.isNaN(pa) ? Number.POSITIVE_INFINITY : pa;
        const nb = Number.isNaN(pb) ? Number.POSITIVE_INFINITY : pb;
        return na - nb;
      });

      // Apply max results limit from admin settings
      return results.slice(0, this.maxResults || 50);
    },
    // New computed properties for enhanced search
    searchProgressPercentage() {
      if (this.searchProgress.totalSteps === 0) return 0;
      return Math.round((this.searchProgress.progress / this.searchProgress.totalSteps) * 100);
    },
    hasValidImage() {
      return !!this.selectedImage;
    },
    primaryDetection() {
      return this.detections && this.detections.length > 0 ? this.detections[0] : null;
    },
    priceRange() {
      const prices = this.results
        .map(r => this.extractNumericPrice(r.prix))
        .filter(p => !isNaN(p) && isFinite(p));
      if (!prices.length) return null;
      return { min: Math.min(...prices), max: Math.max(...prices) };
    }
  },
  watch: {
    $route() {
      if (this.showWebcam) {
        this.closeWebcam();
      }
    }
  },
  beforeDestroy() {
    // Clean up webcam stream when component is destroyed
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach(track => track.stop());
    }
  },
  methods: {
    handleLanguageChange(lang) {
      this.currentLanguage = lang;
    },
    handleDirectionChange(dir) {
      this.direction = dir;
    },

    // Load settings saved by AdminPanel
    loadSettingsFromAdmin() {
      try {
        const saved = JSON.parse(localStorage.getItem('image_search_settings') || 'null');
        if (saved) {
          if (saved.similarityThreshold != null) this.similarityThreshold = saved.similarityThreshold;
          if (saved.brandFilter != null)         this.brandFilter         = saved.brandFilter;
          if (saved.maxResults != null)           this.maxResults         = saved.maxResults;
          if (saved.cacheEnabled != null)         this.cacheEnabled       = saved.cacheEnabled;
          if (saved.filterInStock != null)        this.filterInStock      = saved.filterInStock;
        }
      } catch (_) {}
    },
    async validateImage(file) {
      const maxSize = 10 * 1024 * 1024; // 10MB
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      
      if (file.size > maxSize) {
        throw new Error('Image size must be less than 10MB');
      }
      
      if (!allowedTypes.includes(file.type)) {
        throw new Error('Only JPEG, PNG, and WebP images are supported');
      }
      
      return true;
    },
    
    async generateImageHash(file) {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const img = new Image();
          
          img.onload = () => {
            canvas.width = 8;
            canvas.height = 8;
            ctx.drawImage(img, 0, 0, 8, 8);
            
            const imageData = ctx.getImageData(0, 0, 8, 8).data;
            let hash = '';
            
            for (let i = 0; i < imageData.length; i += 4) {
              const avg = (imageData[i] + imageData[i + 1] + imageData[i + 2]) / 3;
              hash += avg > 128 ? '1' : '0';
            }
            
            resolve(hash);
          };
          
          img.src = e.target.result;
        };
        reader.readAsDataURL(file);
      });
    },
    
    async checkCache(imageHash) {
      if (!this.cacheEnabled) return null;
      
      try {
        const cachedResults = localStorage.getItem(`image_search_${imageHash}`);
        if (cachedResults) {
          const parsed = JSON.parse(cachedResults);
          const cacheAge = Date.now() - parsed.timestamp;
          const maxAge = 30 * 60 * 1000; // 30 minutes
          
          if (cacheAge < maxAge) {
            return parsed.results;
          }
        }
      } catch (error) {
        console.warn('Cache check failed:', error);
      }
      
      return null;
    },
    
    async saveToCache(imageHash, results) {
      if (!this.cacheEnabled) return;
      
      try {
        const cacheData = {
          results,
          timestamp: Date.now()
        };
        localStorage.setItem(`image_search_${imageHash}`, JSON.stringify(cacheData));
      } catch (error) {
        console.warn('Cache save failed:', error);
      }
    },
    
    updateSearchProgress(step, progress, totalSteps) {
      this.searchProgress = {
        currentStep: step,
        progress,
        totalSteps
      };
    },
    
    async searchProducts() {
      if (!this.selectedImage) {
        this.error = this.t.pleaseUploadImage;
        return;
      }

      this.loading = true;
      this.error = '';
      this.hasSearched = true;
      this.results = [];

      try {
        this.updateSearchProgress(this.t.processingImage || '…', 1, 4);
        let imageFile;

        if (this.selectedImage.startsWith('data:')) {
          const response = await fetch(this.selectedImage);
          const blob = await response.blob();
          imageFile = new File([blob], 'image.jpg', { type: blob.type || 'image/jpeg' });
        } else {
          imageFile = this.selectedImage;
        }

        await this.validateImage(imageFile);
        this.imageHash = await this.generateImageHash(imageFile);

        const cachedResults = await this.checkCache(this.imageHash);
        if (cachedResults) {
          this.results = cachedResults;
          if (this.results.length === 0) {
            this.error = this.t.noProductsFound;
          }
          this.loading = false;
          this.updateSearchProgress('', 0, 0);
          return;
        }

        this.updateSearchProgress('YOLO + OCR + matching…', 2, 4);
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('min_faiss_score', this.similarityThreshold.toString());

        const res = await fetch('http://localhost:8000/api/pipeline-image-search', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
          throw new Error(data.message || this.t.searchError);
        }

        this.updateSearchProgress('…', 4, 4);
        this.results = data.results || [];
        this.detections = data.detections || [];
        await this.saveToCache(this.imageHash, this.results);

        if (this.results.length === 0) {
          this.error = data.message || this.t.noProductsFound;
        }
      } catch (error) {
        console.error('Image pipeline search error:', error);
        this.error = error.message || this.t.searchError;
        this.results = [];
      } finally {
        this.loading = false;
        this.updateSearchProgress('', 0, 0);
      }
    },

    async processImage(file) {
      try {
        await this.validateImage(file);
        this.hasSearched = false;
        this.results = [];
        this.error = '';
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedImage = e.target.result;
        };
        reader.readAsDataURL(file);
      } catch (error) {
        this.error = error.message;
        this.selectedImage = null;
      }
    },
    
    // Webcam functionality
    async openWebcam() {
      this.showWebcam = true;
      await this.$nextTick();
      await this.startWebcam();
    },
    
    async startWebcam() {
      try {
        this.webcamStream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' // Use back camera if available
          } 
        });
        
        if (this.$refs.webcamVideo) {
          this.$refs.webcamVideo.srcObject = this.webcamStream;
          // Wait for the video to be ready
          await new Promise((resolve) => {
            this.$refs.webcamVideo.onloadedmetadata = resolve;
          });
        }
      } catch (error) {
        console.error('Error accessing webcam:', error);
        this.error = this.t.webcamAccessError;
        this.showWebcam = false;
      }
    },
    
    async capturePhoto() {
      if (!this.$refs.webcamVideo || !this.$refs.webcamCanvas) return;
      
      const video = this.$refs.webcamVideo;
      const canvas = this.$refs.webcamCanvas;
      const context = canvas.getContext('2d');
      
      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL
      this.capturedPhoto = canvas.toDataURL('image/jpeg', 0.8);
    },
    
    useCapturedPhoto() {
      this.selectedImage = this.capturedPhoto;
      this.closeWebcam();
      this.processCapturedImage();
    },
    
    async processCapturedImage() {
      try {
        // Convert data URL to File object
        const response = await fetch(this.capturedPhoto);
        const blob = await response.blob();
        const file = new File([blob], 'webcam-photo.jpg', { type: 'image/jpeg' });
        
        await this.processImage(file);
      } catch (error) {
        console.error('Error processing captured image:', error);
        this.error = this.t.imageProcessingError;
      }
    },
    
    retakePhoto() {
      this.capturedPhoto = null;
    },
    
    closeWebcam() {
      this.showWebcam = false;
      this.capturedPhoto = null;
      
      // Stop webcam stream
      if (this.webcamStream) {
        this.webcamStream.getTracks().forEach(track => track.stop());
        this.webcamStream = null;
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.processImage(file);
      }
    },
    
    handleDrop(event) {
      this.isDragOver = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        this.processImage(file);
      }
    },
    
    handleDragOver(event) {
      event.preventDefault();
      this.isDragOver = true;
    },
    
    handleDragLeave(event) {
      event.preventDefault();
      this.isDragOver = false;
    },
    
    editText() {
      // Simple text editing - you could make this more sophisticated
      const newText = prompt(this.t.editTextPrompt, this.extractedText);
      if (newText !== null) {
        this.extractedText = newText;
      }
    },
    
    removeImage() {
      this.selectedImage = null;
      this.extractedText = '';
      this.results = [];
      this.detections = [];
      this.reportSaved = false;
      this.hasSearched = false;
      this.imageHash = null;
      this.error = '';
      this.updateSearchProgress('', 0, 0);
      this.$refs.fileInput.value = '';
    },
    
    clearError() {
      this.error = '';
    },
    
    formatPrice(price) {
      if (!price) return '';
      
      // Extract only the numeric part of the price
      const numericPrice = this.extractNumericPrice(price);
      
      // If we successfully extracted a numeric price, format it with DT
      if (!isNaN(numericPrice)) {
        // Format to always show 3 decimal places
        const formattedPrice = numericPrice.toFixed(3);
        return `${formattedPrice} DT`;
      }
      
      // If extraction failed, return the original price as is
      return price;
    },
    
    extractNumericPrice(price) {
      if (!price) return NaN;

      let s = price.toString().trim();

      // 1. Strip currency symbols BEFORE removing non-numeric chars
      //    Arabic د.ت contains a dot — remove the whole symbol first
      s = s
        .replace(/\u062f\.\u062a/g, '')  // Arabic د.ت
        .replace(/\bTND\b/gi, '')
        .replace(/\bDT\b/gi, '')
        .replace(/\bDinar[s]?\b/gi, '')
        .trim();

      // 2. Keep only digits, commas and dots
      s = s.replace(/[^\d.,]/g, '').trim();
      if (!s) return NaN;

      // 3. Determine decimal separator
      const lastComma = s.lastIndexOf(',');
      const lastDot   = s.lastIndexOf('.');

      if (lastComma > lastDot) {
        // Comma is the rightmost separator → it is the decimal point
        // e.g. "46,000" → 46.000 DT  |  "1.234,56" → 1234.56
        s = s.replace(/\./g, '').replace(',', '.');
      } else {
        // Dot is decimal (or no separator at all)
        // Remove commas used as thousands separators, e.g. "1,234.56" → "1234.56"
        s = s.replace(/,/g, '');
      }

      return parseFloat(s);
    },
    
    isInStock(stockStatus) {
      if (!stockStatus) return true;
      const status = stockStatus.toString().toLowerCase();
      return status.includes('en stock') || status.includes('disponible');
    },
    
    getStockClass(stockStatus) {
      if (!stockStatus) return 'stock-unknown';
      const status = stockStatus.toString().toLowerCase();
      if (status.includes('en stock') || status.includes('disponible')) {
        return 'stock-available';
      } else if (status.includes('rupture') || status.includes('hors stock')) {
        return 'stock-unavailable';
      }
      return 'stock-unknown';
    },
    
    getSiteName(link) {
      try {
        const url = new URL(link);
        return url.hostname.replace('www.', '');
      } catch {
        return '';
      }
    },
    
    getSiteLogo(siteName) {
      if (!siteName) return '';

      const domain = siteName.toLowerCase();

      // Mapping: domain keyword → local logo filename in /logos/
      const logoMap = [
        { key: 'anais',              file: 'anais.tn.jpg' },
        { key: 'azalee',             file: 'azalee-para.com.png' },
        { key: 'cosmedic',           file: 'cosmedic.tn.jpg' },
        { key: 'cosmetique',         file: 'cosmetique.tn.jpg' },
        { key: 'drest',              file: 'drest.png' },
        { key: 'hdparashop',         file: 'hdparashop.tn_og.webp' },
        { key: 'laparadulac',        file: 'laparadulac.avif' },
        { key: 'lifepara',           file: 'lifepara.tn.png' },
        { key: 'bpharma',            file: 'logo-bpharma.webp.png' },
        { key: 'med-coast',          file: 'Med-Coast-1-1.png' },
        { key: 'mymedi',             file: 'Med-Coast-1-1.png' },
        { key: 'maparatunisie',      file: 'maparatunisie.tn.png' },
        { key: 'mspara',             file: 'mspara.com.png' },
        { key: 'mycare',             file: 'mycare.tn.jpg' },
        { key: 'my-pharmacy',        file: 'My-pharmacy-logo@2x.webp.png' },
        { key: 'mypharmacy',         file: 'My-pharmacy-logo@2x.webp.png' },
        { key: 'paraclic',           file: 'paraclic.tn.jpg' },
        { key: 'paradise',           file: 'paradise.tn.webp' },
        { key: 'paradream',          file: 'paradream.tn.jpeg' },
        { key: 'paraelfarabi',       file: 'paraelfarabi.com.png' },
        { key: 'paraexpert',         file: 'paraexpert.tn.jpg' },
        { key: 'parafendri',         file: 'parafendri.tn.jpg' },
        { key: 'parahealth',         file: 'parahealth.tn.png' },
        { key: 'paraikram',          file: 'paraikram.tn.png' },
        { key: 'paralabel',          file: 'paralabel.tn.jpg' },
        { key: 'paramasmoudi',       file: 'paramasmoudi.tn.png' },
        { key: 'paranaturalia',      file: 'paranaturalia.tn.png' },
        { key: 'paranet',            file: 'paranet.tn.jpg' },
        { key: 'parapharmacieplus',  file: 'parapharmacieplus.tn.webp' },
        { key: 'parapharm',          file: 'parapharm.tn.png' },
        { key: 'paraplume',          file: 'paraplume.com.png' },
        { key: 'paylesspara',        file: 'paylesspara.png' },
        { key: 'pcommepara',         file: 'pcommepara.tn.png' },
        { key: 'pharma-shop',        file: 'pharma-shop.tn.png' },
        { key: 'pharmavie',          file: 'pharmavie.com.tn.jpg' },
        { key: 'tunisiepara',        file: 'tunisiepara.com.tn.png' },
      ];

      const match = logoMap.find(entry => domain.includes(entry.key));
      if (match) return `/logos/${match.file}`;

      // Default: return empty string if no specific logo found
      return '';
    },
    
    handleLogoError(event) {
      event.target.style.display = 'none';
    },

    getCacheStats() {
      this.refreshCacheStats();
      return `${this.cacheStats.total} items, ${this.cacheStats.size}, oldest: ${this.cacheStats.oldest}, newest: ${this.cacheStats.newest}`;
    },

    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    async clearCache() {
      if (confirm(this.t.clearCacheConfirm)) {
        localStorage.clear();
        this.cacheStats = {
          total: 0,
          size: '0 Bytes',
          oldest: 'N/A',
          newest: 'N/A'
        };
        this.imageHash = null;
        this.results = [];
        this.hasSearched = false;
        this.error = '';
        this.extractedText = '';
        this.selectedImage = null;
        this.$refs.fileInput.value = '';
        this.updateSearchProgress('', 0, 0);
        alert(this.t.cacheCleared);
      }
    },
    
    async saveImageReport() {
      if (!this.results || this.results.length === 0) return;
      
      // Generate a tiny 150px thumbnail to permanently solve the 5MB Quota Limit
      let thumbnailBase64 = null;
      if (this.selectedImage && this.selectedImage.startsWith('data:image')) {
        try {
          thumbnailBase64 = await new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
              const canvas = document.createElement('canvas');
              const maxDim = 150;
              let w = img.width;
              let h = img.height;
              if (w > maxDim || h > maxDim) {
                if (w > h) { h *= maxDim/w; w = maxDim; }
                else { w *= maxDim/h; h = maxDim; }
              }
              canvas.width = w; canvas.height = h;
              const ctx = canvas.getContext('2d');
              ctx.drawImage(img, 0, 0, w, h);
              resolve(canvas.toDataURL('image/jpeg', 0.7));
            };
            img.onerror = () => resolve(null);
            img.src = this.selectedImage;
          });
        } catch(e) { console.warn('Thumbnail generation failed', e); }
      }
      
      const report = {
        id: Date.now(),
        type: 'image',
        savedAt: new Date().toISOString(),
        searchDate: new Date().toISOString(),
        image: thumbnailBase64, // Dramatically reduced from 4MB to ~5KB!
        productName: this.primaryDetection ? this.primaryDetection.product_text_clean : 'Produit détecté',
        description: this.primaryDetection ? this.primaryDetection.description : '',
        priceRange: this.priceRange,
        results: this.results,
        totalResults: this.results.length,
      };
      
      try {
        let existing = [];
        try {
          existing = JSON.parse(localStorage.getItem('image_search_reports') || '[]');
          if (!Array.isArray(existing)) existing = [];
        } catch (_) { existing = []; }
        existing.unshift(report);
        if (existing.length > 50) existing.splice(50);
        localStorage.setItem('image_search_reports', JSON.stringify(existing));
        this.reportSaved = true;
        setTimeout(() => { this.reportSaved = false; }, 3500);
      } catch (e) {
        console.error('Could not save image report:', e);
        this.error = 'Impossible de sauvegarder le rapport. Stockage insuffisant.';
      }
    },

    refreshCacheStats() {
      let total = 0;
      let size = 0;
      let oldest = null;
      let newest = null;

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('image_search_')) {
          try {
            const cachedItem = JSON.parse(localStorage.getItem(key));
            if (cachedItem && cachedItem.timestamp) {
              total++;
              size += JSON.stringify(cachedItem).length;
              const timestamp = cachedItem.timestamp;
              if (oldest === null || timestamp < oldest) {
                oldest = timestamp;
              }
              if (newest === null || timestamp > newest) {
                newest = timestamp;
              }
            }
          } catch (error) {
            console.warn('Error parsing cached item:', error);
          }
        }
      }

      this.cacheStats = {
        total,
        size: this.formatBytes(size),
        oldest: oldest ? new Date(oldest).toLocaleDateString() : 'N/A',
        newest: newest ? new Date(newest).toLocaleDateString() : 'N/A'
      };
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ===== FOREST GREEN PALETTE ===== */
:root {
  --color-forest-green: #1A7F5A;
  --color-mint-tint: #E8F7F2;
  --color-off-white: #F7F9F8;
  --color-deep-forest: #1A2E26;
  --color-coral: #FF6B35;
}

/* Container */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  max-width: 100vw;
  background-color: #F7F9F8;
  overflow-x: hidden;
}

/* Content Wrapper */
.content-wrapper {
  display: flex;
  width: 100vw;
  margin-top: 70px;
  min-height: calc(100vh - 70px);
  background-color: #F7F9F8;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: #1A2E26 !important;
  border-right: 1px solid rgba(26,127,90,0.3);
  padding: 1.5rem;
  box-shadow: 2px 0 12px rgba(26,46,38,0.15);
  position: fixed;
  top: 70px;
  left: 0;
  height: calc(100vh - 70px);
  overflow-y: auto;
  z-index: 50;
  display: flex;
  flex-direction: column;
}

.sidebar-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(232,247,242,0.2);
}

.sidebar-header h3 {
  color: #E8F7F2 !important;
  font-size: 1.1rem;
  font-weight: 600;
}

.menu-section {
  margin-bottom: 2rem;
}

.menu-section h4 {
  color: rgba(232,247,242,0.6) !important;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.menu-section ul {
  list-style: none;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(232,247,242,0.85) !important;
  font-weight: 500;
}

.menu-item:hover {
  background: rgba(26,127,90,0.25);
  color: #E8F7F2 !important;
}

.menu-item.active {
  background: #1A7F5A !important;
  color: white !important;
  box-shadow: 0 2px 8px rgba(26,127,90,0.4);
}

.menu-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Main Content - with sidebar */
.main-content {
  flex: 1;
  padding: 2rem;
  margin-left: 280px;
  background-color: #F7F9F8;
  min-height: calc(100vh - 70px);
}

.content-header {
  margin-bottom: 3rem;
  text-align: center;
}

.content-header h1 {
  font-size: 2.75rem;
  font-weight: 800;
  color: #1A2E26;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.content-subtitle {
  color: #1A7F5A;
  font-size: 1.15rem;
  font-weight: 500;
}

/* Product Summary Card */
.product-summary-card {
  display: flex;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(26,127,90,0.1), 0 2px 4px -1px rgba(26,127,90,0.06);
  padding: 1.5rem;
  margin-bottom: 2rem;
  gap: 1.5rem;
  border: 1px solid #E8F7F2;
}

.summary-image-col {
  flex-shrink: 0;
  width: 200px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #edf2f7;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.summary-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.summary-details-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.summary-title {
  font-size: 1.7rem;
  font-weight: 700;
  color: #1A2E26;
  margin: 0 0 0.75rem 0;
  line-height: 1.3;
}

.summary-desc {
  font-size: 1rem;
  color: #4a5568;
  margin: 0 0 1.25rem 0;
  line-height: 1.6;
}

.summary-meta {
  display: flex;
  gap: 2rem;
  padding-top: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.meta-icon {
  font-size: 1.5rem;
}

.meta-text {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #a0aec0;
  font-weight: 600;
}

.meta-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2b6cb0;
}

/* Base Styles */
.image-search-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(26,127,90,0.08);
  padding: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

 .upload-section {
   margin-bottom: 2rem;
 }

 .upload-options {
   display: flex;
   align-items: center;
   gap: 1rem;
   margin-bottom: 1rem;
 }

 .webcam-btn {
   display: flex;
   align-items: center;
   gap: 0.5rem;
   background: linear-gradient(90deg, #1A7F5A 0%, #155c41 100%);
   color: white;
   border: none;
   padding: 0.75rem 1.5rem;
   border-radius: 8px;
   font-size: 1rem;
   font-weight: 600;
   cursor: pointer;
   transition: all 0.3s ease;
   box-shadow: 0 2px 8px rgba(26,127,90,0.25);
 }

 .webcam-btn:hover {
   transform: translateY(-1px);
   box-shadow: 0 4px 12px rgba(26,127,90,0.35);
 }

 .webcam-icon {
   font-size: 1.2rem;
 }

 .upload-divider {
   color: #718096;
   font-weight: 500;
   font-size: 0.9rem;
 }

.upload-area {
  border: 3px dashed rgba(26,127,90,0.3);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.upload-area:hover {
  border-color: #1A7F5A;
  background: #E8F7F2;
}

.upload-area.drag-over {
  border-color: #1A7F5A;
  background: #E8F7F2;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #1A2E26;
  font-weight: 600;
  font-size: 1.2rem;
}

.upload-icon {
  font-size: 3.5rem;
  color: #1A7F5A;
  margin-bottom: 0.5rem;
}

.upload-hint {
  font-size: 0.95rem;
  color: #1A7F5A;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 0.5rem;
}

.image-preview {
  position: relative;
  display: inline-block;
}

.preview-img {
  max-width: 300px;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.remove-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(229, 62, 62, 0.15);
  transition: background 0.2s, box-shadow 0.2s;
}
.remove-btn:hover, .remove-btn:focus {
  background: #c53030;
  box-shadow: 0 4px 16px rgba(229, 62, 62, 0.25);
}

.extracted-text-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.text-display p {
  flex: 1;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 6px;
  margin: 0;
  font-size: 1rem;
  line-height: 1.5;
}

.edit-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.search-btn {
  display: block;
  width: 100%;
  max-width: 300px;
  margin: 2rem auto;
  padding: 1rem 0;
  background: linear-gradient(90deg, #1A7F5A 0%, #155c41 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(26,127,90,0.25);
  transition: all 0.3s;
}

.search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(26,127,90,0.35);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #a0aec0;
}

.search-btn-ready {
  background: linear-gradient(90deg, #1A7F5A 0%, #155c41 100%);
  box-shadow: 0 4px 12px rgba(26,127,90,0.25);
}

.search-btn-ready:hover {
  box-shadow: 0 6px 16px rgba(26,127,90,0.35);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #1A7F5A;
}

.loading-spinner {
  border: 3px solid #E8F7F2;
  border-top: 3px solid #1A7F5A;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.close-error {
  margin-left: auto;
  font-size: 1.2rem;
  font-weight: bold;
}

.results-section {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.results-title {
  color: #1A2E26;
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
}

.filters {
  margin-bottom: 1rem;
}

.stock-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #4a5568;
  cursor: pointer;
}

.product-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 1100px) {
  .product-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 700px) {
  .product-cards {
    grid-template-columns: 1fr;
  }
}

.product-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: visible;
  box-shadow: 0 2px 8px rgba(26,127,90,0.08);
  padding: 1rem 1.2rem;
  border: 1.5px solid #E8F7F2;
  transition: all 0.25s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  box-shadow: 0 6px 20px rgba(26,127,90,0.18);
  transform: translateY(-3px);
  border-color: #1A7F5A;
}

/* Lowest price card gets coral accent border */
.lowest-price-card {
  border: 2.5px solid #FF6B35 !important;
  box-shadow: 0 4px 14px rgba(255,107,53,0.2) !important;
}

.lowest-price-card:hover {
  box-shadow: 0 8px 24px rgba(255,107,53,0.3) !important;
}

.lowest-price-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #FF6B35;
  color: white;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(255,107,53,0.35);
  z-index: 2;
  letter-spacing: 0.03em;
}

.product-content {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  width: 100%;
  flex: 1;
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  width: 100%;
}

.divider-line {
  height: 1px;
  background: #E8F7F2;
  width: 100%;
  margin: 0.2rem 0;
}

/* Vertical column layout for card content */
.product-details-col {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  width: 100%;
  flex: 1;
}

.vendor-logo {
  width: 140px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.site-logo {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.stock-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.stock-available {
  background: rgba(72, 187, 120, 0.1);
  color: #48bb78;
}

.stock-unavailable {
  background: rgba(245, 101, 101, 0.1);
  color: #f56565;
}

.stock-unknown {
  background: rgba(160, 174, 192, 0.1);
  color: #a0aec0;
}

.stock-icon-img {
  width: 16px;
  height: 16px;
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1A2E26;
  margin: 0;
  line-height: 1.4;
}

.price-display {
  margin-top: auto;
}

.price-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1A7F5A;
}

.view-offer-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background: #1A7F5A;
  color: white;
  text-decoration: none;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  transition: all 0.25s ease;
  white-space: nowrap;
  margin-top: 0.5rem;
  align-self: flex-start;
}

.view-offer-btn:hover {
  transform: translateY(-1px);
  background: #155c41;
  box-shadow: 0 4px 12px rgba(26,127,90,0.3);
}

.btn-arrow {
  font-size: 0.8rem;
}

 .no-results-message {
   text-align: center;
   padding: 3rem;
   color: #718096;
   font-size: 1.1rem;
 }

 /* Webcam Modal Styles */
 .webcam-modal {
   position: fixed;
   top: 0;
   left: 0;
   width: 100%;
   height: 100%;
   background: rgba(0, 0, 0, 0.8);
   display: flex;
   align-items: center;
   justify-content: center;
   z-index: 1000;
 }

 .webcam-container {
   background: white;
   border-radius: 12px;
   padding: 2rem;
   max-width: 600px;
   width: 90%;
   max-height: 90vh;
   overflow-y: auto;
   box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
 }

 .webcam-header {
   display: flex;
   justify-content: space-between;
   align-items: center;
   margin-bottom: 1.5rem;
   padding-bottom: 1rem;
   border-bottom: 1px solid #e2e8f0;
 }

 .webcam-header h3 {
   margin: 0;
   color: #2d3748;
   font-size: 1.25rem;
   font-weight: 600;
 }

 .close-webcam-btn {
   background: none;
   border: none;
   font-size: 1.5rem;
   color: #718096;
   cursor: pointer;
   padding: 0.25rem;
   border-radius: 4px;
   transition: color 0.2s ease;
 }

 .close-webcam-btn:hover {
   color: #e53e3e;
 }

 .webcam-content {
   text-align: center;
 }

 .webcam-video {
   width: 100%;
   max-width: 500px;
   height: auto;
   border-radius: 8px;
   margin-bottom: 1rem;
   border: 2px solid #e2e8f0;
 }

 .webcam-controls {
   display: flex;
   gap: 1rem;
   justify-content: center;
   margin-bottom: 1rem;
 }

 .capture-btn {
   display: flex;
   align-items: center;
   gap: 0.5rem;
   background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
   color: white;
   border: none;
   padding: 0.75rem 1.5rem;
   border-radius: 8px;
   font-size: 1rem;
   font-weight: 600;
   cursor: pointer;
   transition: all 0.3s ease;
 }

 .capture-btn:hover {
   transform: translateY(-1px);
   box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
 }

 .capture-icon {
   font-size: 1.2rem;
 }

 .cancel-btn {
   background: #e53e3e;
   color: white;
   border: none;
   padding: 0.75rem 1.5rem;
   border-radius: 8px;
   font-size: 1rem;
   font-weight: 600;
   cursor: pointer;
   transition: all 0.3s ease;
 }

 .cancel-btn:hover {
   background: #c53030;
   transform: translateY(-1px);
 }

 .captured-preview {
   margin-top: 1rem;
   padding: 1rem;
   background: #f7fafc;
   border-radius: 8px;
 }

 .captured-img {
   max-width: 100%;
   max-height: 300px;
   border-radius: 8px;
   margin-bottom: 1rem;
   border: 2px solid #e2e8f0;
 }

 .captured-actions {
   display: flex;
   gap: 1rem;
   justify-content: center;
 }

 .use-photo-btn {
   background: #48bb78;
   color: white;
   border: none;
   padding: 0.5rem 1rem;
   border-radius: 6px;
   font-size: 0.9rem;
   font-weight: 500;
   cursor: pointer;
   transition: all 0.3s ease;
 }

 .use-photo-btn:hover {
   background: #38a169;
   transform: translateY(-1px);
 }

 .retake-btn {
   background: #718096;
   color: white;
   border: none;
   padding: 0.5rem 1rem;
   border-radius: 6px;
   font-size: 0.9rem;
   font-weight: 500;
   cursor: pointer;
   transition: all 0.3s ease;
 }

 .retake-btn:hover {
   background: #4a5568;
   transform: translateY(-1px);
 }

 .similarity-score {
   display: flex;
   align-items: center;
   gap: 0.5rem;
   background: #E8F7F2;
   padding: 0.35rem 0.7rem;
   border-radius: 15px;
   font-size: 0.78rem;
   font-weight: 500;
   color: #1A2E26;
   border: 1px solid rgba(26,127,90,0.2);
   justify-content: center;
   align-self: flex-start;
 }

 .similarity-label {
   font-weight: 600;
   color: #1A7F5A;
 }

 .similarity-value {
   font-weight: 700;
   color: #1A7F5A;
 }

/* Enhanced Progress Indicator */
.search-progress {
  margin-top: 1rem;
  text-align: center;
}

.progress-bar {
  width: 100%;
  max-width: 400px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1A7F5A 0%, #155c41 100%);
  transition: width 0.3s ease;
}

.progress-text {
  color: #1A2E26;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.progress-percentage {
  color: #1A7F5A;
  font-weight: 600;
  font-size: 1.1rem;
}

/* Processing Status */
.processing-status {
  background: #f0fff4;
  border: 1px solid #9ae6b4;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #22543d;
  font-size: 0.9rem;
}

.status-icon {
  font-size: 1.1rem;
}

/* Cache Status */
.cache-status {
  background: #fef5e7;
  border: 1px solid #f6ad55;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #744210;
  font-size: 0.9rem;
  font-family: monospace;
}

.cache-icon {
  font-size: 1.1rem;
}

/* Enhanced Search Settings */
.search-settings {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.settings-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(90deg, #1A7F5A 0%, #155c41 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(26,127,90,0.2);
  width: 100%;
  text-align: left;
  justify-content: space-between;
}

.settings-toggle:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26,127,90,0.3);
}

.settings-toggle .settings-icon {
  font-size: 1.2rem;
}

.settings-panel {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.setting-group {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #e2e8f0;
}

.setting-group:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.setting-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 500;
}

.setting-value {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

.similarity-slider {
  width: 100%;
  -webkit-appearance: none;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  outline: none;
  margin-top: 0.5rem;
}

.similarity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: background 0.2s ease;
}

.similarity-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: background 0.2s ease;
}

.setting-description {
  font-size: 0.8rem;
  color: #a0aec0;
  margin-top: 0.5rem;
}

.cache-stats {
  font-size: 0.8rem;
  color: #718096;
  margin-bottom: 1rem;
}

.clear-cache-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  text-align: center;
}

.clear-cache-btn:hover {
  background: #c53030;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
    height: auto;
  }
  
  .content {
    margin-left: 0;
    transform: none;
    left: 0;
  }
  
  .main-content {
    flex-direction: column;
  }
  
  .product-details-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .price-display {
    text-align: left;
  }
}

.vertical-upload-options {
  flex-direction: column !important;
  align-items: stretch;
  gap: 1.5rem;
}
.horizontal-divider {
  display: block;
  width: 100%;
  text-align: center;
  color: #1A7F5A;
  font-weight: 600;
  font-size: 1.1rem;
  margin: 1.5rem 0;
  position: relative;
}
.horizontal-divider::before,
.horizontal-divider::after {
  content: '';
  display: inline-block;
  vertical-align: middle;
  width: 40%;
  height: 2px;
  background: rgba(26,127,90,0.2);
  margin: 0 0.5rem;
}
.centered-webcam-btn {
  margin: 0 auto;
  display: block;
  min-width: 180px;
  max-width: 250px;
  width: 100%;
  padding: 0.5rem 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  justify-content: center;
  align-items: center;
  background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(72, 187, 120, 0.13);
}
.centered-webcam-btn:hover {
  background: linear-gradient(90deg, #38a169 0%, #48bb78 100%);
  transform: translateY(-1px);
}
/* ── Product Summary Panel ──────────────────────────────────── */
.product-summary-panel {
  display: flex;
  gap: 1.75rem;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
  border: 1px solid rgba(102, 126, 234, 0.18);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  position: relative;
  overflow: hidden;
  align-items: stretch;
}
.product-summary-panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1A7F5A 0%, #1A2E26 100%);
}
.summary-image-col {
  flex-shrink: 0;
  width: 160px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.summary-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.summary-info-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  min-width: 0;
}
.summary-product-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
  line-height: 1.3;
  margin: 0;
}
.summary-description {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.75;
  margin: 0;
}
.summary-price-range {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
  border: 1px solid #9ae6b4;
  color: #276749;
  padding: 0.35rem 0.9rem;
  border-radius: 20px;
  font-size: 0.88rem;
  font-weight: 700;
  width: fit-content;
}
.save-report-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.2rem;
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(72,187,120,0.25);
}
.save-report-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(72,187,120,0.35);
}
.save-report-btn.saved {
  background: linear-gradient(135deg, #2d9250 0%, #276749 100%);
  box-shadow: 0 3px 10px rgba(45,146,80,0.3);
  cursor: default;
}
@media (max-width: 640px) {
  .product-summary-card {
    flex-direction: column;
  }
  .summary-image-col {
    width: 100%;
    height: 200px;
  }
  .summary-meta {
    flex-direction: column;
    gap: 1rem;
  }
}
</style> 