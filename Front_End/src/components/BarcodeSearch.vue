<template>
  <div class="app-container">
    <!-- Navigation Bar -->
    <Navigation @language-changed="handleLanguageChange">
      <template #logo>
        <img :src="barcodeIconSrc" alt="Barcode Logo" class="logo-barcode-icon" />
      </template>
    </Navigation>

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
              <li class="menu-item active">
                <img :src="barcodeIconSrc" alt="Barcode" class="sidebar-barcode-icon" />
                {{ t.barcodeSearch }}
              </li>
              <li class="menu-item" @click="$router.push('/image-search')">
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
          <h1>{{ t.barcodeSearchTitle }}</h1>
          <p class="content-subtitle">{{ t.barcodeSearchSubtitle }}</p>
        </div>
        
        <div class="barcode-search-container">
          <form @submit.prevent="onSubmit">
            <div class="search-input-section">
              <div class="form-group">
                <label class="barcode-label">
                  {{ t.productBarcode }}
                  <div class="input-scanner-group">
                    <input 
                      v-model="barcode" 
                      type="text" 
                      class="barcode-input" 
                      :placeholder="t.barcodePlaceholder"
                      @keyup.enter="onManualBarcodeSubmit"
                    />
                    <!-- Barcode Scanner Component -->
                    <BarcodeScanner 
                      ref="barcodeScanner"
                      v-model="barcode" 
                    />
                  </div>
                </label>
              </div>
            </div>

            <!-- File Upload for Barcode List -->
            <div class="form-group">
              <label class="upload-label">
                <svg class="upload-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>
                {{ fileUploading ? t.uploadingFile : t.uploadBarcodeList }}
                <input 
                  type="file" 
                  @change="onFileChange" 
                  accept=".csv,.xlsx,.xls,.txt" 
                  class="file-input"
                  :disabled="fileUploading"
                />
              </label>
              <div v-if="fileUploading" class="upload-progress">
                <div class="upload-spinner"></div>
                <span>{{ t.processingFile }}</span>
              </div>
            </div>

            <!-- Add scanned/manual barcode to list -->
            <div class="form-group">
              <button 
                type="button" 
                @click="addBarcodeToList" 
                :disabled="!barcode || barcode.trim() === ''"
                class="add-barcode-btn"
              >
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
                </svg>
                {{ t.addCurrentBarcode }}
              </button>
            </div>

            <!-- List of barcodes to search -->
            <div class="barcode-list-container" v-if="barcodeList.length">
              <div class="barcode-list-header">
                <h4>Barcodes to Search ({{ barcodeList.length }})</h4>
                <button 
                  type="button" 
                  @click="clearBarcodeList" 
                  class="clear-all-btn"
                >
                  Clear All
                </button>
              </div>
              <div class="barcode-list">
                <div 
                  v-for="(code, idx) in barcodeList" 
                  :key="idx"
                  class="barcode-item"
                >
                  <span class="barcode-text">{{ code }}</span>
                  <span class="barcode-type">{{ getBarcodeType(code) }}</span>
                  <button 
                    type="button" 
                    @click="removeBarcode(idx)"
                    class="remove-btn"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>

            <div class="selectors" v-if="false">
              <div class="selector-field">
                <label>
                  {{ t.nameSelector }}
                  <input v-model="selectors.name" type="text" :placeholder="t.nameSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
              <div class="selector-field">
                <label>
                  {{ t.imageSelector }}
                  <input v-model="selectors.photo" type="text" :placeholder="t.imageSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
              <div class="selector-field">
                <label>
                  {{ t.descriptionSelector }}
                  <input v-model="selectors.description" type="text" :placeholder="t.descriptionSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
              <div class="selector-field">
                <label>
                  {{ t.priceSelector }}
                  <input v-model="selectors.price" type="text" :placeholder="t.priceSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
              <div class="selector-field">
                <label>
                  {{ t.brandSelector }}
                  <input v-model="selectors.brand" type="text" :placeholder="t.brandSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
              <div class="selector-field">
                <label>
                  {{ t.stockSelector }}
                  <input v-model="selectors.stock" type="text" :placeholder="t.stockSelectorPlaceholder" class="selector-input" />
                </label>
              </div>
            </div>
            
            <div class="fields-container">
              <label v-for="field in fields" :key="field.value" class="field-checkbox">
                <input type="checkbox" v-model="selectedFields" :value="field.value" />
                {{ field.label }}
              </label>
            </div>
            
            <button type="submit" class="search-btn">{{ t.search }}</button>
          </form>
          
          <!-- Loading State -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>{{ t.searching }}</p>
          </div>

          <!-- Error State -->
          <div v-if="error" class="error-container">
            <div class="error-icon">⚠️</div>
            <p class="error-message">{{ error }}</p>
            <button @click="clearError" class="retry-button">{{ t.retry }}</button>
          </div>
          
          <!-- Results Container -->
          <div class="product-results-container" v-if="results.length">
            <!-- Product Summary Section -->
            <div class="product-summary">
              <div class="summary-left">
                <img v-if="mainProductImage" :src="mainProductImage" :alt="productNameUsed" class="summary-image" />
              </div>
              <div class="summary-right">
                <h3 class="summary-name">{{ productNameUsed }}</h3>
                <div v-if="mainProductDescription" class="summary-description">
                  {{ truncatedDescription }}
                  <button v-if="needsReadMore" @click="showFullDescription = !showFullDescription" class="read-more-btn">
                    {{ showFullDescription ? t.reduce : t.readMore }}
                  </button>
                </div>
                <div class="summary-price-range">
                  <span v-if="priceRange">{{ t.price }} {{ priceRange }}</span>
                </div>
                <div v-if="mainProductBrand" class="summary-brand">{{ t.brand }} {{ mainProductBrand }}</div>
              </div>
            </div>
            

            
            <!-- Save Results Button -->
            <div class="save-results-section" v-if="filteredResults.length > 0">
              <button 
                @click="saveToReports" 
                class="save-results-btn"
                :disabled="saving"
              >
                <span v-if="saving" class="save-loading">{{ t.saveLoading }}</span>
                {{ saving ? t.saving : t.saveToReports }}
              </button>
            </div>
            
            <!-- Results Controls -->
            <div v-if="filteredResults.length > 0" class="results-controls">
              <div class="sorting-controls">
                <div class="sort-header">
                  <span class="sort-label">{{ t.sortByPrice }}</span>
                  <button 
                    @click="toggleSortDirection" 
                    class="sort-toggle"
                    :title="sortDirection === 'asc' ? t.descending : t.ascending"
                  >
                    <span class="sort-text">{{ sortDirection === 'asc' ? t.ascending : t.descending }}</span>
                  </button>
                </div>
              </div>
              <div class="stock-filter">
                <label class="stock-checkbox">
                  <input 
                    type="checkbox" 
                    v-model="filterInStock"
                    @change="updateFilterInStock"
                  />
                  <span class="checkbox-custom"></span>
                  <span class="checkbox-text">{{ t.showInStockOnly }}</span>
                  <span class="stock-count" v-if="getSingleStockCount()">
                    ({{ getSingleStockCount() }})
                  </span>
                </label>
              </div>
            </div>
            
            <!-- Results Cards -->
            <div class="product-cards">
              <div class="results-debug" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                {{ t.debugResultsFound.replace('{count}', filteredResults.length) }}
              </div>
              <div 
                v-for="(result, index) in filteredResults" 
                :key="`${result.site_name || getSiteName(result.lien)}-${result.nom || productNameUsed}-${index}`" 
                class="product-card"
              >
                <!-- Logo and stock status on top row, other elements in one line below -->
                <div class="product-content">
                  <div class="top-row">
                    <div class="vendor-logo">
                      <img 
                        :src="getSiteLogo(result.site_name || getSiteName(result.lien))" 
                        :alt="result.site_name || getSiteName(result.lien)"
                        class="site-logo"
                        @error="handleLogoError"
                      />
                    </div>
                    
                    <div 
                      class="stock-indicator" 
                      :class="getStockClass(result.disponibilite)"
                    >
                      <img 
                        v-if="isInStock(result.disponibilite)" 
                        src="/src/assets/1x/check.png" 
                        alt="En stock" 
                        class="stock-icon-img"
                        title="En stock"
                        style="width:24px;height:24px;display:inline-block;vertical-align:middle;"
                      />
                      <img 
                        v-else 
                        src="https://cdn-icons-png.flaticon.com/512/1828/1828778.png" 
                        alt="Hors stock" 
                        class="stock-icon-img"
                        title="Hors stock"
                        style="width:24px;height:24px;display:inline-block;vertical-align:middle;"
                      />
                      <span 
                        class="stock-text"
                        :class="getStockClass(result.disponibilite)"
                        :style="isInStock(result.disponibilite) ? 'color:#22c55e;margin-left:0.4rem;margin-top:6px;display:inline-block;font-weight:600;font-size:1rem;position:relative;top:4px;' : 'color:#ef4444;margin-left:0.4rem;margin-top:6px;display:inline-block;font-weight:600;font-size:1rem;position:relative;top:4px;'"
                      >
                        {{ isInStock(result.disponibilite) ? t.inStock : t.outOfStock }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="divider-line"></div>
                  
                  <div class="product-details-row">
                    <h4 class="product-name">{{ result.nom || productNameUsed }}</h4>
                    
                    <div class="price-display">
                      <span class="price-value">{{ result.prix ? formatPrice(result.prix) : t.priceNotAvailable }}</span>
                    </div>
                    
                                          <a :href="result.lien || result.link || result.url" target="_blank" class="view-offer-btn">
                        <span class="btn-text">{{ t.viewOffer }}</span>
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                          <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </a>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- No Results Message -->
            <div 
              v-if="filteredResults.length === 0" 
              class="no-results-message"
            >
              {{ t.noResultsMatchCriteria }}
            </div>
          </div>
        </div>
        
        <!-- Multi-Barcode Results Container -->
        <div class="multi-barcode-results-container" v-if="multiBarcodeResults && Object.keys(multiBarcodeResults).length > 0">
          <h2 class="multi-results-title">{{ t.multiBarcodeResults }}</h2>
          
          <!-- Multi-Barcode Error State -->
          <div v-if="multiBarcodeError" class="error-container">
            <div class="error-icon">⚠️</div>
            <p class="error-message">{{ multiBarcodeError }}</p>
          </div>
          
          <!-- Multi-Barcode Loading State -->
          <div v-if="multiBarcodeLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>{{ t.searchingMultipleBarcodes }}</p>
          </div>
          
          <!-- Individual Barcode Results -->
          <div class="barcode-results-list">
            <div 
              v-for="(barcodeData, barcode) in multiBarcodeResults" 
              :key="barcode"
              class="barcode-result-section"
            >
              <div class="barcode-result-header">
                <h3 class="barcode-title">
                  <span class="barcode-code">{{ barcode }}</span>
                  <span class="barcode-type-badge">{{ getBarcodeType(barcode) }}</span>
                </h3>
                <div class="barcode-status">
                  <span v-if="barcodeData.success" class="status-success">
                    {{ barcodeData.results.length }} {{ t.resultsFound }}
                  </span>
                  <span v-else class="status-error">
                    {{ barcodeData.error || t.noResultsFound }}
                  </span>
                </div>
              </div>
              <!-- Product Summary Section -->
              <div v-if="barcodeData && barcodeData.success && barcodeData.results && barcodeData.results.length > 0" class="product-summary">
                <div class="summary-left">
                  <img v-if="getMultiBarcodeMainImage(barcode, barcodeData.results)" :src="getMultiBarcodeMainImage(barcode, barcodeData.results)" :alt="barcodeData.productName" class="summary-image" />
                </div>
                <div class="summary-right">
                  <div class="summary-header">
                    <h3 class="summary-name">{{ barcodeData.productName || getMultiBarcodeProductName(barcode, barcodeData.results) || 'Produit sans nom' }}</h3>
                  </div>
                  <div v-if="getMultiBarcodeDescription(barcode, barcodeData.results)" class="summary-description">
                    {{ getMultiBarcodeTruncatedDescription(barcode, barcodeData.results) }}
                    <button v-if="getMultiBarcodeNeedsReadMore(barcode, barcodeData.results)" @click="toggleMultiBarcodeDescription(barcode)" class="read-more-btn">
                      {{ getMultiBarcodeShowFullDescription(barcode) ? t.reduce : t.readMore }}
                    </button>
                  </div>
                  <div class="summary-price-range">
                    <span v-if="getMultiBarcodePriceRange(barcode, barcodeData.results)">{{ t.price }} {{ getMultiBarcodePriceRange(barcode, barcodeData.results) }}</span>
                  </div>
                  <div v-if="getMultiBarcodeBrand(barcode, barcodeData.results)" class="summary-brand">{{ t.brand }} {{ getMultiBarcodeBrand(barcode, barcodeData.results) }}</div>
                </div>
              </div>

              <!-- Results Controls -->
              <div v-if="barcodeData && barcodeData.success && barcodeData.results && barcodeData.results.length > 0" class="results-controls">
                <div class="sorting-controls">
                  <div class="sort-header">
                    <span class="sort-label">{{ t.sortByPrice }}</span>
                    <button 
                      @click="toggleMultiSortDirection(barcode)" 
                      class="sort-toggle"
                      :title="getMultiSortDirection(barcode) === 'asc' ? t.descending : t.ascending"
                    >
                      <span class="sort-text">{{ getMultiSortDirection(barcode) === 'asc' ? t.ascending : t.descending }}</span>
                    </button>
                  </div>
                </div>
                <div class="stock-filter">
                  <label class="stock-checkbox">
                    <input 
                      type="checkbox" 
                      v-model="multiFilterInStock[barcode]"
                      @change="updateMultiFilterInStock(barcode)"
                    />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-text">{{ t.showInStockOnly }}</span>
                    <span class="stock-count" v-if="getStockCount(barcode, barcodeData.results)">
                      ({{ getStockCount(barcode, barcodeData.results) }})
                    </span>
                  </label>
                </div>
              </div>

              <div v-if="barcodeData && barcodeData.success && barcodeData.results && barcodeData.results.length > 0" class="product-cards">
                <div 
                  v-for="(result, index) in getSortedFilteredMultiResults(barcode, barcodeData.results)" 
                  :key="`${barcode}-${result.site_name || getSiteName(result.lien)}-${result.nom || barcodeData.productName}-${index}`" 
                  class="product-card"
                >
                  <div class="product-content">
                    <div class="top-row">
                      <div class="vendor-logo">
                        <img 
                          :src="getSiteLogo(result.site_name || getSiteName(result.lien))" 
                          :alt="result.site_name || getSiteName(result.lien)"
                          class="site-logo"
                          @error="handleLogoError"
                        />
                      </div>
                      <div 
                        class="stock-indicator" 
                        :class="getStockClass(result.disponibilite)"
                      >
                        <img 
                          v-if="isInStock(result.disponibilite)" 
                          src="/src/assets/1x/check.png" 
                          alt="En stock" 
                          class="stock-icon-img"
                          title="En stock"
                          style="width:24px;height:24px;display:inline-block;vertical-align:middle;"
                        />
                        <img 
                          v-else 
                          src="https://cdn-icons-png.flaticon.com/512/1828/1828778.png" 
                          alt="Hors stock" 
                          class="stock-icon-img"
                          title="Hors stock"
                          style="width:24px;height:24px;display:inline-block;vertical-align:middle;"
                        />
                        <span 
                          class="stock-text"
                          :class="getStockClass(result.disponibilite)"
                          :style="isInStock(result.disponibilite) ? 'color:#22c55e;margin-left:0.4rem;margin-top:6px;display:inline-block;font-weight:600;font-size:1rem;position:relative;top:4px;' : 'color:#ef4444;margin-left:0.4rem;margin-top:6px;display:inline-block;font-weight:600;font-size:1rem;position:relative;top:4px;'"
                        >
                          {{ isInStock(result.disponibilite) ? t.inStock : t.outOfStock }}
                        </span>
                      </div>
                    </div>
                    <div class="divider-line"></div>
                    <div class="product-details-row">
                      <h4 class="product-name">{{ result.nom || barcodeData.productName }}</h4>
                      <div class="price-display">
                        <span class="price-value">{{ result.prix ? formatPrice(result.prix) : t.priceNotAvailable }}</span>
                      </div>
                      <a :href="result.lien || result.link || result.url" target="_blank" class="view-offer-btn">
                        <span class="btn-text">{{ t.viewOffer }}</span>
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                          <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="barcodeData.success && barcodeData.results.length === 0" class="no-results-message">
                {{ t.noResultsFound }}
              </div>
            </div>
          </div>
          
          <!-- Save Multi-Barcode Results Button -->
          <div class="multi-save-section" v-if="Object.keys(multiBarcodeResults).length > 0">
            <button 
              @click="saveToReports" 
              class="multi-save-btn"
              :disabled="saving"
            >
              <span v-if="saving" class="save-loading">{{ t.saving }}</span>
              {{ saving ? t.saving : t.saveMultiBarcodeReports }}
            </button>
          </div>
        </div>
      </main>
    </div>
    
    <div v-if="imageModal.show" class="image-modal">
      <img :src="imageModal.src" :alt="imageModal.alt" class="image-modal-content" />
      <button @click="closeImageModal" class="image-modal-close">{{ t.close }}</button>
    </div>
  </div>
</template>

<script>
import BarcodeScanner from './BarcodeScanner.vue';
import Navigation from './Navigation.vue';
import { getCurrentTranslations } from '@/locales';
import { ref, computed, onMounted } from 'vue';
import barcodeIcon from '@/assets/1x/barcode.png';
import cleopatreLogo from '@/assets/1x/logo-1672327200.jpg';
import pharmavieLogo from '@/assets/1x/pharmavie-logo-1612955224.jpg';
import checkIcon from '@/assets/1x/check.png';
let barcodeIconDark;
try {
  barcodeIconDark = require('@/assets/1x/barcode-dark.png');
} catch (e) {
  barcodeIconDark = barcodeIcon;
}
const isDarkMode = ref(document.documentElement.classList.contains('dark-mode'));
const barcodeIconSrc = computed(() => isDarkMode.value ? barcodeIconDark : barcodeIcon);

onMounted(() => {
  const update = () => {
    isDarkMode.value = document.documentElement.classList.contains('dark-mode');
  };
  update();
  const observer = new MutationObserver(update);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
});

export default {
  name: 'BarcodeSearch',
  components: {
    BarcodeScanner,
    Navigation
  },
  data() {
    return {
      barcode: '',
      selectors: {
        price: '',
        brand: '',
        stock: '',
        name: '',
        photo: '',
        description: ''
      },
      fields: [
        { label: this.t?.name || 'Nom', value: 'nom', icon: '📝' },
        { label: this.t?.photo || 'Photo', value: 'photo', icon: '📷' },
        { label: this.t?.priceTND || 'Prix (TND)', value: 'prix', icon: '💰' },
        { label: this.t?.description || 'Description', value: 'description', icon: '📄' }
      ],
      selectedFields: ['nom', 'photo', 'prix', 'description'],
      results: [],
      loading: false,
      error: '',
      productNameUsed: '',
      mainProductImage: null,
      showAdvanced: false,
      hasSearched: false,
      sortBy: 'prix',
      sortDirection: 'asc',
      filterInStock: false,
      imageModal: {
        show: false,
        src: '',
        alt: ''
      },
      mainProductDescription: '',
      mainProductBrand: '',
      priceRange: '',
      showFullDescription: false,
      saving: false,
      currentLanguage: 'fr',
      isDarkMode: false,
      barcodeIconDark: barcodeIcon,
      barcodeList: [], // New: List of barcodes to search
      multiBarcodeResults: {}, // New: Store results for each barcode separately
      multiBarcodeLoading: false, // New: Loading state for multi-barcode search
      multiBarcodeError: '', // New: Error state for multi-barcode search
      fileUploading: false, // New: Loading state for file upload
      multiSortDirection: {}, // { [barcode]: 'asc' or 'desc' }
      multiFilterInStock: {}, // { [barcode]: true/false }
      multiBarcodeShowFullDescription: {} // { [barcode]: true/false }
    };
  },
  computed: {
    t() {
      return getCurrentTranslations(this.currentLanguage);
    },
    barcodeIconSrc() {
      return this.isDarkMode ? this.barcodeIconDark : barcodeIcon;
    },
    filteredResults() {
      // Apply filtering and sorting
      let filteredResults = [...this.results];
      
      // Apply stock filter
      if (this.filterInStock) {
        filteredResults = filteredResults.filter(result => this.isInStock(result.disponibilite));
      }
      
      // Apply sorting
      filteredResults.sort((a, b) => {
        const priceA = this.extractNumericPrice(a.prix) || 0;
        const priceB = this.extractNumericPrice(b.prix) || 0;
        
        if (this.sortDirection === 'asc') {
          return priceA - priceB;
        } else {
          return priceB - priceA;
        }
      });
      
      console.log('filteredResults - Filtered and sorted count:', filteredResults.length);
      return filteredResults;
    },
    truncatedDescription() {
      if (!this.mainProductDescription) return '';
      if (this.showFullDescription || this.mainProductDescription.length <= 180) {
        return this.mainProductDescription;
      }
      return this.mainProductDescription.slice(0, 180) + '...';
    },
    needsReadMore() {
      return this.mainProductDescription && this.mainProductDescription.length > 180;
    }
  },
  watch: {
    results(newResults) {
      // Set main product image, name, description, brand, and price range from results
      const firstWithImage = newResults.find(r => r.photo);
      this.mainProductImage = firstWithImage ? firstWithImage.photo : '';
      const firstWithName = newResults.find(r => r.nom);
      this.productNameUsed = firstWithName ? firstWithName.nom : this.productNameUsed;
      // Find the longest description from non-pharma-shop.tn sites
      const nonPharmaResults = newResults.filter(r => r.site_name !== 'pharma-shop.tn');
      const bestDescriptionResult = nonPharmaResults.reduce((best, current) => {
        const currentDesc = current.description || '';
        const bestDesc = best.description || '';
        return currentDesc.length > bestDesc.length ? current : best;
      }, { description: '' });
      
      this.mainProductDescription = bestDescriptionResult.description || '';
      const firstWithBrand = newResults.find(r => r.brand);
      this.mainProductBrand = firstWithBrand ? firstWithBrand.brand : '';
      // Price range
      const prices = newResults.map(r => this.extractNumericPrice(r.prix)).filter(p => !isNaN(p));
      if (prices.length) {
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        this.priceRange = min === max ? `${min} DT` : `${min} DT - ${max} DT`;
      } else {
        this.priceRange = '';
      }
    }
  },
  created() {
    try {
      // Initialize any necessary data
      this.setDefaultSelectors();
      
      // Optional: Add any initial setup
      console.log('BarcodeSearch component created successfully');
    } catch (error) {
      console.error('Error during BarcodeSearch component creation:', error);
      // Optionally set a default error state
      this.error = 'Erreur lors de l\'initialisation du composant';
    }
  },
  mounted() {
    try {
      // Any additional setup after component is mounted to the DOM
      console.log('BarcodeSearch component mounted');
      // Debug log added
      
      // Set up dark mode observer
      this.updateDarkMode();
      const observer = new MutationObserver(() => {
        this.updateDarkMode();
      });
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    } catch (error) {
      console.error('Error during BarcodeSearch component mount:', error);
    }
  },
  errorCaptured(err, vm, info) {
    // Global error capture for this component
    console.error('Erreur capturée dans BarcodeSearch:', err);
    console.error('Informations supplémentaires:', info);
    
    // Optionally set a user-friendly error message
    this.error = 'Une erreur est survenue. Veuillez réessayer.';
    
    // Prevent the error from propagating
    return false;
  },
  methods: {
    updateDarkMode() {
      this.isDarkMode = document.documentElement.classList.contains('dark-mode');
    },
    handleLanguageChange(lang) {
      // Handle language change from navigation component
      console.log('Language changed to:', lang);
      this.currentLanguage = lang;
      // Update fields labels when language changes
      this.fields = [
        { label: this.t.name, value: 'nom', icon: '📝' },
        { label: this.t.photo, value: 'photo', icon: '📷' },
        { label: this.t.priceTND, value: 'prix', icon: '💰' },
        { label: this.t.description, value: 'description', icon: '📄' }
      ];
    },
    setDefaultBarcode() {
      // Add a default barcode for testing
      this.barcode = '3017620422002'; // Example barcode
      this.onSubmit(); // Automatically submit
    },
    extractNumericPrice(price) {
      if (!price) return NaN;
      
      // Extract only digits, dots, and commas from the price
      const numericString = price.toString().replace(/[^\d.,]/g, '');
      
      // Replace commas with dots for decimal format, then convert to number
      const numericPrice = parseFloat(numericString.replace(/,/g, '.'));
      
      console.log(`extractNumericPrice: "${price}" -> ${numericPrice}`);
      return numericPrice;
    },
    toggleSortDirection() {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
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
    isInStock(stockStatus) {
      console.log('isInStock called with:', stockStatus);
      if (!stockStatus) {
        console.log('No stock status, defaulting to available');
        return true; // Default to available if no status found
      }
      const status = stockStatus.toString().toLowerCase();
      console.log('Checking stock status:', status);
      const isAvailable = status.includes('en stock') || status.includes('disponible');
      console.log('Is available:', isAvailable);
      return isAvailable;
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
    getSiteShortName(siteName) {
      // Extract first few characters or a meaningful abbreviation
      if (!siteName) return '';
      if (siteName.includes('.')) {
        const parts = siteName.split('.');
        return parts[0].substring(0, 3).toUpperCase();
      }
      return siteName.substring(0, 3).toUpperCase();
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
      
      // Try to get logo from search results first (from database)
      const result = this.results.find(r => r.site_name === siteName);
      if (result && (result.logo_url || result.logo)) {
        return result.logo_url || result.logo;
      }
      
      // Fallback to hardcoded logic if no logo in database
      const domain = siteName.toLowerCase();
      
      // Try to construct a logo URL based on common patterns
      if (domain.includes('1001para')) {
        return 'https://1001para.tn/img/logo-1717458224.jpg';
      } else if (domain.includes('pharma-shop')) {
        return 'https://pharma-shop.tn/img/logo.png';
      } else if (domain.includes('paraexpert')) {
        return '/paraexpert-logo.jpg';
      } else if (domain.includes('pharmavie')) {
        return 'https://pharmavie.tn/img/logo.png';
      } else if (domain.includes('parashop')) {
        return 'https://www.parashop.tn/image/cache/catalog/logo-parashop-250x100-250x100.png.webp';
      } else if (domain.includes('parapharmacie')) {
        return 'https://parapharmacie.tn/wp-content/uploads/2025/03/cropped-cropped-logo-para-rose-vert-menu.webp';
      } else if (domain.includes('parafendri')) {
        return 'https://parafendri.tn/img/logo-1736929701.jpg';
      } else if (domain.includes('amal-medical')) {
        return 'https://amal-medical.com/img/logo-1733237756.jpg';
      } else if (domain.includes('cosmetique')) {
        return 'https://cosmetique.tn/img/logo-1743181730.jpg';
      } else if (domain.includes('cleopatre')) {
        return 'https://www.cleopatre.tn/img/logo-1672327200.jpg';
      } else if (domain.includes('paramust')) {
        return 'https://paramust.tn/img/logo-1683799514.jpg';
      } else if (domain.includes('parapharmacieplus')) {
        return 'https://parapharmacieplus.tn/media/info_site/q32bd8_1740051189.webp';
      } else if (domain.includes('parazone')) {
        return 'https://parazone.otospexerp.com/wp-content/uploads/2024/09/cropped-logo-2.png';
      } else if (domain.includes('mlpara')) {
        return 'https://mlpara.tn/img/logo-1696847652.jpg';
      } else if (domain.includes('laparadulac')) {
        return 'https://laparadulac.com/cdn/shop/files/En-tete_21.png?v=1733142707&width=600';
      }
      
      // Default: return empty string if no specific logo found
      return '';
    },
    handleLogoError(event) {
      // Fallback to text placeholder if image fails to load
      const vendorLogo = event.target.parentElement;
      vendorLogo.innerHTML = `<span class="vendor-placeholder">${this.getSiteShortName(event.target.alt)}</span>`;
    },
    async onSubmit() {
      console.log('onSubmit called!'); // Debug log added
      console.log('Current barcode list:', this.barcodeList);
      console.log('Current single barcode input:', this.barcode);
      
      // Prevent duplicate submissions
      if (this.loading) {
        console.log('Search already in progress, ignoring duplicate submission');
        return;
      }
      
      // Determine which barcodes to search
      let barcodesToSearch = [];
      
      if (this.barcodeList.length > 0) {
        // Use all barcodes from the list
        barcodesToSearch = [...this.barcodeList];
        console.log('Using all barcodes from list:', barcodesToSearch);
      } else if (this.barcode && this.barcode.trim() !== '') {
        // Use the single barcode input
        barcodesToSearch = [this.barcode.trim()];
        console.log('Using single barcode input:', barcodesToSearch);
      } else {
        // No barcode available - show error
        console.log('No barcode available for search');
        this.error = this.t.pleaseAddBarcodes;
        return;
      }

      // Set default selectors if any are blank
      const defaultSelectors = {
        name: 'h1, h1.h1, h1.product-title, h1.product_name, .product-name h1, #product_name, .name',
        photo: '#bigpic, .product-image img, .product-image-container img, img.product-image, .product-gallery-slider img, .product-media img, .woocommerce-product-gallery img',
        price: '.price, .current-price, .product-price, [itemprop=\'price\'], .prc, .product-info-price .price',
        brand: '.product-manufacturer, .brand, [itemprop=\'brand\'], .manufacturer',
        stock: '.product-availability, .stock-status, .availability, #product-availability',
        description: '.product-description, #description, .description, [itemprop=\'description\']'
      };
      Object.keys(defaultSelectors).forEach(key => {
        if (!this.selectors[key]) {
          this.selectors[key] = defaultSelectors[key];
        }
      });

      this.loading = true;
      this.error = '';
      this.results = [];
      this.mainProductImage = null;
      this.hasSearched = true;
      
      // Clear previous multi-barcode results
      this.multiBarcodeResults = {};
      this.multiBarcodeError = '';
      
      // If searching multiple barcodes, use multi-barcode logic
      if (barcodesToSearch.length > 1) {
        console.log('Searching multiple barcodes:', barcodesToSearch);
        this.multiBarcodeLoading = true;
        
        try {
          // Search each barcode individually
          for (const barcode of barcodesToSearch) {
            console.log('Searching barcode:', barcode);
            
            const requestBody = {
              barcode: barcode
            };
            
            const response = await fetch('http://127.0.0.1:8000/api/search-barcode', {
              method: 'POST',
              credentials: 'include',
              headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify(requestBody)
            });
            
            if (response.ok) {
              const data = await response.json();
              console.log(`Results for barcode ${barcode}:`, data);
              
              this.multiBarcodeResults[barcode] = {
                success: data.success,
                results: data.results || [],
                productName: data.product_name || null,
                error: data.success ? null : (data.message || 'Unknown error')
              };
            } else {
              const errorText = await response.text();
              console.error(`Error for barcode ${barcode}:`, errorText);
              
              this.multiBarcodeResults[barcode] = {
                success: false,
                results: [],
                productName: null,
                error: `HTTP ${response.status}: ${errorText}`
              };
            }
          }
          
          // Check if any barcode had results
          const hasAnyResults = Object.values(this.multiBarcodeResults).some(result => 
            result.success && result.results.length > 0
          );
          
          if (!hasAnyResults) {
            this.multiBarcodeError = this.t.noResultsFound;
          }
          
        } catch (err) {
          console.error('Error in multi-barcode search:', err);
          this.multiBarcodeError = '❌ Error during multi-barcode search: ' + err.message;
        } finally {
          this.multiBarcodeLoading = false;
          this.loading = false;
        }
        
        return; // Exit early for multi-barcode search
      }
      
      // Single barcode search (original logic)
      const barcodeToSearch = barcodesToSearch[0];
      console.log('Submitting single barcode to API:', barcodeToSearch);
      console.log('API URL: http://127.0.0.1:8000/api/search-barcode');
      
      try {
        const requestBody = {
          barcode: barcodeToSearch
        };
        console.log('Request body:', requestBody);
        
        const response = await fetch('http://127.0.0.1:8000/api/search-barcode', {
          method: 'POST',
          credentials: 'include',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          
          switch(response.status) {
            case 404:
              this.error = this.t.endpointNotFound;
              break;
            case 500:
              this.error = this.t.serverError;
              break;
            case 403:
              this.error = this.t.accessDenied;
              break;
            default:
              this.error = `${this.t.unexpectedError} ${errorText}`;
          }
          
          return;
        }
        
        const data = await response.json();
        console.log('Received data from API:', data);
        console.log('Data type:', typeof data);
        console.log('Data keys:', Object.keys(data));
        
        if (data.results && data.results.length > 0) {
          console.log('Setting results:', data.results);
          console.log('Number of results:', data.results.length);
          this.results = data.results;
          this.productNameUsed = data.product_name || 'Produit sans nom';
          
          // Find the first result with an image to use as the main product image
          const resultWithImage = this.results.find(r => r.photo);
          if (resultWithImage) {
            this.mainProductImage = resultWithImage.photo;
          }
          
          // Scroll to top to show results after a short delay
          this.$nextTick(() => {
            setTimeout(() => {
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
          });
        } else {
          console.log('No results found in API response');
          console.log('API response data:', data);
          this.error = this.t.noResultsFound;
          console.warn('No results found for barcode:', barcodeToSearch);
        }
      } catch (err) {
        console.error('Network or parsing error:', err);
        
        if (err instanceof TypeError) {
          if (err.message.includes('Failed to fetch')) {
            this.error = '❌ Backend server is not running! Please start your backend server on http://127.0.0.1:8000';
          } else if (err.message.includes('JSON')) {
            this.error = '❌ Data processing error. Response format is incorrect.';
          } else {
            this.error = '❌ Unexpected network error: ' + err.message;
          }
        } else {
          this.error = '❌ Unexpected error: ' + err.message;
        }
      } finally {
        this.loading = false;
      }
    },
        clearError() {
      this.error = '';
    },
    
    onManualBarcodeSubmit(event) {
      // Prevent the Enter key event from bubbling up to the BarcodeScanner
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      // Handle manual barcode input with enter key
      if (this.loading) {
        console.log('Search already in progress, ignoring manual input');
        return;
      }
      
      // Prevent scanner from opening if it's trying to open
      if (this.$refs.barcodeScanner && this.$refs.barcodeScanner.showScanner) {
        this.$refs.barcodeScanner.showScanner = false;
      }
      
      // Add barcode to list if it's not empty
      if (this.barcode && this.barcode.trim() !== '') {
        console.log('Manual barcode submitted:', this.barcode);
        this.addBarcodeToList(); // Add to list
      } else if (this.barcodeList.length === 0) {
        // Only show error if there are no barcodes in the list
        this.error = this.t.pleaseEnterValidBarcode;
      }
    },
    setDefaultSelectors() {
      // Safely set default selectors
      this.selectors = {
        name: '',
        photo: '',
        price: '',
        brand: '',
        stock: ''
      };
    },
    async saveToReports() {
      // Check if we have multi-barcode results
      if (Object.keys(this.multiBarcodeResults).length > 0) {
        await this.saveMultiBarcodeReports();
        return;
      }

      // Original single barcode logic
      if (this.filteredResults.length === 0) {
        this.error = this.t.noResultsMatchCriteria;
        return;
      }

      this.saving = true;
      this.error = '';

      try {
        // Determine which barcode was used for the search
        let barcodeUsed = '';
        if (this.barcodeList.length > 0) {
          barcodeUsed = this.barcodeList[0]; // Use first barcode from list
        } else {
          barcodeUsed = this.barcode; // Use single barcode input
        }

        // Get product name with fallback
        let productName = this.productNameUsed;
        if (!productName && this.filteredResults.length > 0) {
          const firstResult = this.filteredResults[0];
          productName = firstResult.nom || `Product ${barcodeUsed}`;
        }
        if (!productName) {
          productName = `Product ${barcodeUsed}`;
        }

        // Prepare the report data
        const reportData = {
          barcode: barcodeUsed,
          search_date: new Date().toISOString(),
          product_name: productName,
          total_results: this.filteredResults.length,
          results: JSON.stringify(this.filteredResults.map(result => ({
            site_name: result.site_name || this.getSiteName(result.lien),
            nom: result.nom,
            prix: result.prix,
            lien: result.lien || result.link || result.url,
            photo: result.photo,
            description: result.description,
            reference: result.reference,
            disponibilite: result.disponibilite,
            saved_at: new Date().toISOString() // Add actual save timestamp
          })))
        };

        // Send to backend API
        console.log('Saving report data:', reportData);
        const response = await fetch('http://localhost:8000/api/reports', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(reportData)
        });
        const data = await response.json();
        console.log('Save report response:', data);

        if (data.success) {
          const successMessage = this.t.reportSavedSuccess
            .replace('{barcode}', barcodeUsed)
            .replace('{product}', this.productNameUsed)
            .replace('{count}', this.filteredResults.length);
          alert(successMessage);
        } else {
          this.error = data.message || 'Erreur lors de l\'enregistrement du rapport.';
        }
      } catch (error) {
        console.error('Error saving report:', error);
        this.error = 'Erreur lors de l\'enregistrement du rapport.';
      } finally {
        this.saving = false;
      }
    },

    async saveMultiBarcodeReports() {
      this.saving = true;
      this.error = '';

      try {
        let savedCount = 0;
        let failedCount = 0;
        const failedBarcodes = [];

        console.log('Multi-barcode results to save:', this.multiBarcodeResults);
        // Save each barcode result individually
        for (const [barcode, barcodeData] of Object.entries(this.multiBarcodeResults)) {
          console.log(`Processing barcode ${barcode}:`, barcodeData);
          if (barcodeData.success && barcodeData.results.length > 0) {
            try {
              // Get product name from results if not available in barcodeData
              let productName = barcodeData.productName;
              if (!productName && barcodeData.results && barcodeData.results.length > 0) {
                const firstResult = barcodeData.results[0];
                productName = firstResult.nom || `Product ${barcode}`;
              }
              if (!productName) {
                productName = `Product ${barcode}`;
              }

              const reportData = {
                barcode: barcode,
                search_date: new Date().toISOString(),
                product_name: productName,
                total_results: barcodeData.results.length,
                results: JSON.stringify(barcodeData.results.map(result => ({
                  site_name: result.site_name || this.getSiteName(result.lien),
                  nom: result.nom,
                  prix: result.prix,
                  lien: result.lien || result.link || result.url,
                  photo: result.photo,
                  description: result.description,
                  reference: result.reference,
                  disponibilite: result.disponibilite,
                  saved_at: new Date().toISOString() // Add actual save timestamp
                })))
              };
              console.log(`Report data for barcode ${barcode}:`, reportData);

              const response = await fetch('http://localhost:8000/api/reports', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify(reportData)
              });
              
              const data = await response.json();
              
              if (data.success) {
                savedCount++;
              } else {
                failedCount++;
                failedBarcodes.push(barcode);
              }
            } catch (error) {
              console.error(`Error saving report for barcode ${barcode}:`, error);
              failedCount++;
              failedBarcodes.push(barcode);
            }
          } else {
            // Skip barcodes with no results or failed searches
            console.log(`Skipping barcode ${barcode} - no results or failed search`);
          }
        }

        // Show summary message
        if (savedCount > 0) {
          let successMessage = this.t.multiReportSavedSuccess
            .replace('{saved}', savedCount)
            .replace('{total}', Object.keys(this.multiBarcodeResults).length)
            .replace('{failed}', failedCount);
          
          if (failedBarcodes.length > 0) {
            successMessage += `\n\nFailed barcodes: ${failedBarcodes.join(', ')}`;
          }
          
          alert(successMessage);
        } else {
          this.error = this.t.noReportsToSave;
        }

      } catch (error) {
        console.error('Error saving multi-barcode reports:', error);
        this.error = 'Erreur lors de l\'enregistrement des rapports multi-codes-barres.';
      } finally {
        this.saving = false;
      }
    },
    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('File uploaded:', file.name, file.size, 'bytes');
        this.fileUploading = true;
        this.error = '';
        
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const content = e.target.result;
            console.log('File content:', content);
            const barcodes = content.split('\n').map(code => code.trim()).filter(code => code);
            console.log('Extracted barcodes:', barcodes);
            this.barcodeList = [...new Set([...this.barcodeList, ...barcodes])]; // Add unique barcodes
            console.log('Updated barcode list:', this.barcodeList);
            this.barcode = ''; // Clear the input field
            
            // File uploaded successfully - barcodes added to list
            console.log('File uploaded successfully. Barcodes added to list:', this.barcodeList.length);
          } catch (error) {
            console.error('Error reading file:', error);
            this.error = this.t.fileReadError;
          } finally {
            this.fileUploading = false;
          }
        };
        reader.readAsText(file);
      }
    },
    addBarcodeToList() {
      if (this.barcode && this.barcode.trim() !== '') {
        this.barcodeList.push(this.barcode.trim());
        this.barcode = ''; // Clear the input field
        
        // Barcode added to list successfully
        console.log('Barcode added to list. Total barcodes:', this.barcodeList.length);
      }
    },
    removeBarcode(index) {
      this.barcodeList.splice(index, 1);
    },
    clearBarcodeList() {
      this.barcodeList = [];
    },
    isValidBarcode(code) {
      // Implement your barcode validation logic here
      // For example, you can use a regular expression to check the format
      return /^[0-9]{13}$/.test(code);
    },
    getBarcodeType(code) {
      // Simple barcode type detection based on length
      switch (code.length) {
        case 13:
          return 'EAN-13';
        case 8:
          return 'UPC-A';
        case 12:
          return 'EAN-12';
        case 14:
          return 'EAN-14';
        default:
          return 'Unknown';
      }
    },
    
    async searchMultipleBarcodes() {
      if (this.barcodeList.length === 0) {
        this.multiBarcodeError = this.t.pleaseAddBarcodes;
        return;
      }

      this.multiBarcodeLoading = true;
      this.multiBarcodeError = '';
      this.multiBarcodeResults = {};
      this.hasSearched = true;

      try {
        // Search each barcode individually
        for (const barcode of this.barcodeList) {
          console.log('Searching barcode:', barcode);
          
          const response = await fetch('http://127.0.0.1:8000/api/search-barcode', {
            method: 'POST',
            credentials: 'include',
            headers: { 
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({
              barcode: barcode.trim()
            })
          });

          if (response.ok) {
            const data = await response.json();
            this.multiBarcodeResults[barcode] = {
              results: data.results || [],
              productName: data.product_name || 'Produit sans nom',
              success: true
            };
          } else {
            this.multiBarcodeResults[barcode] = {
              results: [],
              productName: '',
              success: false,
              error: `Erreur ${response.status}: ${response.statusText}`
            };
          }
        }

        // Scroll to results
        this.$nextTick(() => {
          setTimeout(() => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }, 100);
        });

      } catch (err) {
        console.error('Error in multi-barcode search:', err);
        this.multiBarcodeError = this.t.networkError;
      } finally {
        this.multiBarcodeLoading = false;
      }
    },
    

    toggleMultiSortDirection(barcode) {
      if (!this.multiSortDirection[barcode]) this.multiSortDirection[barcode] = 'asc';
      this.multiSortDirection[barcode] = this.multiSortDirection[barcode] === 'asc' ? 'desc' : 'asc';
    },
    
    getMultiSortDirection(barcode) {
      return this.multiSortDirection && this.multiSortDirection[barcode] || 'asc';
    },
    
    getSortedFilteredMultiResults(barcode, results) {
      if (!results || !Array.isArray(results)) return [];
      
      // Create a copy to avoid mutating the original array
      let filteredResults = [...results];
      
      // Apply stock filter
      if (this.multiFilterInStock && this.multiFilterInStock[barcode]) {
        filteredResults = filteredResults.filter(result => this.isInStock(result.disponibilite));
      }
      
      // Apply sorting
      const sortDirection = this.getMultiSortDirection(barcode);
      filteredResults.sort((a, b) => {
        const priceA = this.extractNumericPrice(a.prix) || 0;
        const priceB = this.extractNumericPrice(b.prix) || 0;
        
        if (sortDirection === 'asc') {
          return priceA - priceB;
        } else {
          return priceB - priceA;
        }
      });
      
      return filteredResults;
    },
    
    updateMultiFilterInStock(barcode) {
      // This method is called when the stock filter checkbox changes
      // The filtering is handled in getSortedFilteredMultiResults
    },
    
    getStockCount(barcode, results) {
      if (!results || !Array.isArray(results)) return 0;
      return results.filter(result => this.isInStock(result.disponibilite)).length;
    },
    
    // Multi-barcode summary methods
    getMultiBarcodeMainImage(barcode, results) {
      if (!results || !Array.isArray(results)) return null;
      const resultWithImage = results.find(r => r.photo);
      return resultWithImage ? resultWithImage.photo : null;
    },
    
    getMultiBarcodeDescription(barcode, results) {
      if (!results || !Array.isArray(results)) return '';
      // Find the longest description from non-pharma-shop.tn sites
      const nonPharmaResults = results.filter(r => r.site_name !== 'pharma-shop.tn');
      const bestDescriptionResult = nonPharmaResults.reduce((best, current) => {
        const currentDesc = current.description || '';
        const bestDesc = best.description || '';
        return currentDesc.length > bestDesc.length ? current : best;
      }, { description: '' });
      
      return bestDescriptionResult.description || '';
    },
    
    getMultiBarcodeTruncatedDescription(barcode, results) {
      if (!results || !Array.isArray(results)) return '';
      const description = this.getMultiBarcodeDescription(barcode, results);
      if (this.getMultiBarcodeShowFullDescription(barcode) || description.length <= 180) {
        return description;
      }
      return description.slice(0, 180) + '...';
    },
    
    getMultiBarcodeNeedsReadMore(barcode, results) {
      if (!results || !Array.isArray(results)) return false;
      const description = this.getMultiBarcodeDescription(barcode, results);
      return description && description.length > 180;
    },
    
    getMultiBarcodeShowFullDescription(barcode) {
      return this.multiBarcodeShowFullDescription && this.multiBarcodeShowFullDescription[barcode] || false;
    },
    
    toggleMultiBarcodeDescription(barcode) {
      if (!this.multiBarcodeShowFullDescription) {
        this.multiBarcodeShowFullDescription = {};
      }
      this.multiBarcodeShowFullDescription[barcode] = !this.getMultiBarcodeShowFullDescription(barcode);
    },
    
    getMultiBarcodePriceRange(barcode, results) {
      if (!results || !Array.isArray(results)) return '';
      const prices = results.map(r => this.extractNumericPrice(r.prix)).filter(p => !isNaN(p));
      if (prices.length) {
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        return min === max ? `${min} DT` : `${min} DT - ${max} DT`;
      }
      return '';
    },
    
    getMultiBarcodeBrand(barcode, results) {
      if (!results || !Array.isArray(results)) return '';
      const firstWithBrand = results.find(r => r.brand);
      return firstWithBrand ? firstWithBrand.brand : '';
    },
    
    getMultiBarcodeProductName(barcode, results) {
      if (!results || !Array.isArray(results)) return '';
      const firstWithName = results.find(r => r.nom);
      return firstWithName ? firstWithName.nom : '';
    },
    
    updateFilterInStock() {
      // This method is called when the stock filter checkbox changes
      // The filtering is handled in filteredResults computed property
    },
    
    getSingleStockCount() {
      return this.results.filter(result => this.isInStock(result.disponibilite)).length;
    },

  }
};
</script>

<style scoped>
/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
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
  margin-bottom: 2rem;
  text-align: center;
}

.content-header h1 {
  font-size: 2.25rem;
  font-weight: 700;
  color: #1A2E26;
  margin-bottom: 0.5rem;
}

.content-subtitle {
  color: #718096;
  font-size: 1.1rem;
}

/* Barcode Search Container */
.barcode-search-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
   position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.search-input-section {
  margin-bottom: 1.5rem;
}

.input-scanner-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.barcode-search-container h2 {
  font-size: 1.75rem;
  margin-bottom: 2rem;
  color: #2d3748;
  text-align: center;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.barcode-label {
  font-size: 1.1rem;
  color: #2d3748;
  font-weight: 500;
  display: block;
}

.barcode-input {
  display: block;
  flex: 1;
  min-width: 0;
  padding: 0.6rem 1rem;
  font-size: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.3s;
}

.barcode-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  outline: none;
}

/* Selector Fields */
.selectors {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.2rem;
  margin: 1.5rem 0;
}

.selector-field label {
  display: block;
  font-size: 1rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.selector-input {
  display: block;
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.selector-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  outline: none;
}

/* Fields Selection */
.fields-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin: 1.5rem 0;
  justify-content: center;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f7fafc;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  color: #4a5568;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.field-checkbox:hover {
  background: #edf2f7;
  transform: translateY(-1px);
}

/* Search Button */
.search-btn {
  display: block;
  width: 100%;
  max-width: 300px;
  margin: 2rem auto;
  padding: 0.9rem 0;
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

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(26,127,90,0.35);
}

/* Loading & Error States */
.loading, .error {
  text-align: center;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
}

.loading {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.error {
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.1);
}

/* New Product Results Styles */
.product-results-container {
  margin-top: 2rem;
}

.product-title {
  font-size: 1.6rem;
  color: #2d3748;
  margin-bottom: 1.5rem;
  text-align: center;
}

.filter-container {
  display: flex;
  justify-content: flex-end;
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
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.product-card {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 0.3rem 0.5rem;
  margin-bottom: 0.15rem;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}
.product-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
}

.product-content {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  width: 100%;
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.3rem;
  width: 100%;
  margin-bottom: 0.05rem;
}

.divider-line {
  height: 1px;
  background: #e2e8f0;
  width: 100%;
  margin: 0.05rem 0;
}

.product-details-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  width: 100%;
}

.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 140px;
}
.vendor-logo {
  width: 120px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
  border: 1px solid #e2e8f0;
  padding: 0.2rem;
  background: #f8fafc;
}
.vendor-placeholder {
  font-size: 0.8rem;
  font-weight: 700;
  color: #4a5568;
}
.site-logo {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 4px;
}
.product-info {
  margin-bottom: 0.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.product-name {
  font-size: 0.5rem;
  color: #2d3748;
  font-weight: 500;
  margin: 0;
  flex: 1;
  line-height: 1.2;
  min-width: 0;
}
.product-description {
  font-size: 0.98rem;
  color: #4a5568;
  margin-bottom: 0;
  max-width: 90%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-price-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
}
.price-display {
  font-size: 1.1rem;
  font-weight: 700;
  color: #764ba2;
  white-space: nowrap;
}

/* Read More Button Styles */
.read-more-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  margin-left: 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  text-decoration: underline;
}

.read-more-btn:hover {
  background: #f7fafc;
  color: #4c51bf;
}

/* Sort Toggle Button Styles */
.sort-toggle {
  background: #1A7F5A;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.sort-toggle:hover {
  background: #155c41;
}

.sort-icon {
  font-weight: bold;
  font-size: 0.9rem;
}

/* Stock Filter Checkbox Styles */
.stock-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #4a5568;
  cursor: pointer;
}

.stock-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #667eea;
}

.stock-indicator {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.2rem 0.6rem;
  border-radius: 0.5rem;
  background: #f8fafc;
}

.stock-text {
  font-weight: 600;
  font-size: 1rem;
  transition: color 0.3s;
}

.stock-available {
  color: #22c55e; /* Green for in stock */
}

.stock-unavailable {
  color: #ef4444; /* Red for out of stock */
}

.stock-unknown {
  color: #6b7280; /* Gray for unknown status */
}

.stock-icon-img {
  width: 18px;
  height: 18px;
  object-fit: contain;
}
.stock-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
}
.in-stock-icon {
  color: #10b981;
  font-size: 1.3rem;
  font-weight: bold;
}
.out-of-stock-icon {
  color: #ef4444;
  font-size: 1.3rem;
  font-weight: bold;
}
.stock-text {
  font-size: 1.02rem;
  font-weight: 500;
}
.stock-available {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}
.stock-unavailable {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}
.stock-unknown {
  color: #6b7280;
}
.action-section {
  margin-top: 0.5rem;
  text-align: right;
}
.view-offer-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  border: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 36px;
  min-width: 120px;
  text-align: center;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.view-offer-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.view-offer-btn:hover::before {
  left: 100%;
}

.view-offer-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.btn-text {
  font-weight: 600;
  letter-spacing: 0.02em;
  position: relative;
  z-index: 1;
}

.btn-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 1;
}

.view-offer-btn:hover .btn-icon {
  transform: translateX(2px) scale(1.1);
}

.view-offer-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

/* Image Modal */
.image-modal {
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

.image-modal-content {
  max-width: 80%;
  max-height: 80%;
  border-radius: 8px;
}

.image-modal-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Price Stats Styles */
.price-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stats-item {
  text-align: center;
}

.stats-label {
  font-size: 0.8rem;
  color: #718096;
  margin-bottom: 0.3rem;
}

.stats-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
}

/* Save Results Button Styles */
.save-results-section {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.save-results-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.save-results-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.save-results-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.save-icon, .save-loading {
  font-size: 1.1rem;
}

/* Results Controls Styles */
.results-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem 1.2rem;
  background: #f8fafc;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.results-controls:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.sort-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.sort-label {
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 600;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-toggle {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.7rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(102, 126, 234, 0.2);
  transition: all 0.2s ease;
}

.sort-toggle:hover {
  background: #5a67d8;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.sort-text {
  font-weight: 600;
  font-size: 0.8rem;
}

.stock-filter {
  display: flex;
  align-items: center;
}

.stock-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #4a5568;
  cursor: pointer;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  position: relative;
}

.stock-checkbox:hover {
  background: rgba(102, 126, 234, 0.05);
  color: #667eea;
}

.stock-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-custom {
  position: relative;
  height: 18px;
  width: 18px;
  background-color: #fff;
  border: 2px solid #cbd5e0;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stock-checkbox:hover .checkbox-custom {
  border-color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
}

.stock-checkbox input:checked ~ .checkbox-custom {
  background-color: #667eea;
  border-color: #667eea;
}

.checkbox-custom:after {
  content: "";
  position: absolute;
  display: none;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.stock-checkbox input:checked ~ .checkbox-custom:after {
  display: block;
}

.checkbox-text {
  font-weight: 500;
  color: inherit;
}

.stock-count {
  font-size: 0.8rem;
  color: #718096;
  font-weight: 400;
  margin-left: 0.2rem;
}

.no-results-message {
  text-align: center;
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  margin-top: 1.5rem;
  color: #718096;
  font-size: 1rem;
}

.reset-filters-btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.6rem 1.2rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
  transition: all 0.3s;
}

.reset-filters-btn:hover {
  background: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Loading State */
.loading-container {
  text-align: center;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.loading-spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  text-align: center;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.error-message {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.retry-button {
  padding: 0.6rem 1.2rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
  transition: all 0.3s;
}

.retry-button:hover {
  background: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Product Summary Styles */
.product-summary {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #f7fafc;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.08);
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}
.summary-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  min-width: 220px;
}
.summary-image {
  width: 280px;
  height: 280px;
  object-fit: contain;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.summary-header {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  background-color: #f8fafc;
  padding: 0.5rem;
  border-radius: 4px;
}

.summary-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
  line-height: 1.3;
}
.summary-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
  justify-content: flex-start;
  padding-left: 2rem;
}
.sidebar-barcode-icon {
  width:12px;
  height: 12px;
  margin-right: 0.3rem;
  vertical-align: middle;
  filter: drop-shadow(0 0 1px #0002);
}
.logo-barcode-icon {
  width: 40px !important;
  height: 2rem !important;
  object-fit: fill;
  filter: brightness(0) invert(1);
  vertical-align: middle;
  margin-right: 10px;
}
.summary-description {
  font-size: 1.05rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
}
.summary-price-range {
  font-size: 1.1rem;
  font-weight: 600;
  color: #764ba2;
}
.summary-brand {
  font-size: 1.05rem;
  color: #667eea;
}

/* New Barcode List Styles */
.upload-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #475569;
}

.upload-label:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
  transform: translateY(-1px);
}

.upload-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.file-input {
  display: none;
}

.add-barcode-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.2rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
  transition: all 0.3s ease;
}

.add-barcode-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
}

.add-barcode-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.barcode-list-container {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.barcode-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

.barcode-list-header h4 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
}

.clear-all-btn {
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
}

.clear-all-btn:hover {
  background: #c82333;
}

.barcode-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.barcode-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.6rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  max-width: 240px;
}

.barcode-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.barcode-text {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #495057;
  font-weight: 600;
  flex: 1;
}

.barcode-type {
  font-size: 0.7rem;
  color: #6c757d;
  background: #f8f9fa;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  border: 1px solid #dee2e6;
  margin: 0 0.5rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.15rem;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #f8d7da;
  transform: scale(1.1);
}

.barcode-item:last-child {
  margin-bottom: 0;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.barcode-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.barcode-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.barcode-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.barcode-value {
  font-family: 'Courier New', monospace;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #d1d5db;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.barcode-type {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
  background: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.barcode-validation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.validation-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.validation-status.valid {
  color: #1d4ed8;
  background: #dbeafe;
  border: 1px solid #93c5fd;
}

.validation-status.invalid {
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.validation-icon {
  width: 14px;
  height: 14px;
}

.item-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.status-indicator {
  font-size: 0.85rem;
  color: #3b82f6;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-icon {
  width: 16px;
  height: 16px;
  animation: spin 2s linear infinite;
}

.item-length {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
  background: #f9fafb;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 0. 4rem;
}

.remove-item-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.remove-item-btn:hover {
  background-color: #fef2f2;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.remove-item-icon {
  width: 18px;
  height: 18px;
}

/* Enhanced Chip Styles */
.barcode-chip.chip-valid {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.barcode-chip.chip-invalid {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fef2f2 100%);
}

.chip-type {
  font-size: 0.7rem;
  color: #6b7280;
  font-weight: 600;
  background: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes itemSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.1;
  }
}

.item-added {
  animation: itemSlideIn 0.4s ease-out;
}

/* Horizontal Barcode List Styles */
.horizontal-barcode-list {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.75rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.horizontal-barcode-list:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.barcode-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  flex: 1;
}

.barcode-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #d1d5db;
  border-radius: 20px;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  color: #374151;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  animation: chipSlideIn 0.3s ease-out;
  position: relative;
  overflow: hidden;
}

.barcode-chip::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.barcode-chip:hover::before {
  left: 100%;
}

.barcode-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
  background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
}

.chip-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.chip-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
}

.chip-remove-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.chip-remove-btn:hover {
  background-color: #fef2f2;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.chip-remove-icon {
  width: 16px;
  height: 16px;
}

.chip-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  flex-shrink: 0;
}

.chip-count {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
  text-align: right;
}

.clear-all-btn-small {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
  transition: all 0.3s ease;
}

.clear-all-btn-small:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  transform: translateY(-1px);
}

.clear-icon {
  width: 16px;
  height: 16px;
}

@keyframes chipSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.chip-added {
  animation: chipSlideIn 0.3s ease-out;
}

/* Barcode List Container Styles */
.barcode-list-container {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.barcode-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.barcode-list-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 700;
}

.list-icon {
  width: 24px;
  height: 24px;
  color: #667eea;
}

.clear-all-btn {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
  transition: all 0.3s ease;
}

.clear-all-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  transform: translateY(-1px);
}

.barcode-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* Responsive Styles */
@media (max-width: 768px) {
  .navbar-menu {
    display: none;
  }
  
  .sidebar {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 1.5rem;
  }
  
  .selectors {
    grid-template-columns: 1fr;
  }
  
  .product-card {
    padding: 0.3rem 0.5rem;
  }
  
  .product-content {
    flex-direction: column;
    align-items: stretch;
    gap: 0.3rem;
  }
  
  .product-details-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.6rem;
  }
  
  .action-section {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    min-width: auto;
  }
  
  .product-name {
    order: 1;
  }
  
  .stock-indicator {
    order: 2;
    align-self: center;
  }
  
  .price-display {
    order: 3;
    align-self: center;
  }
  
  .view-offer-btn {
    order: 4;
    align-self: center;
  }

  .product-summary {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }
  .summary-right {
    padding-left: 0;
  }
  .summary-left {
    align-items: center;
    min-width: 0;
  }
  .summary-image {
    width: 150px;
    height: 150px;
  }
}

@media (max-width: 480px) {
  
  .main-content {
    padding: 1rem;
  }
  
  .barcode-search-container {
    padding: 1.5rem 1rem;
  }
  
  .content-header h1 {
    font-size: 1.5rem;
  }
  
  .input-scanner-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .barcode-input {
    width: 100%;
  }
  
  .fields-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-btn {
    max-width: 100%;
  }
  
  .product-card {
    padding: 0.4rem;
  }
  
  .price-value {
    font-size: 1.25rem;
  }
}
@media (max-width: 900px) {
  .product-card {
    grid-template-columns: 1fr;
    gap: 0.4rem;
    padding: 0.6rem 0.4rem;
  }
  .product-info {
    margin-bottom: 0.2rem;
  }
  .product-price-section {
    align-items: flex-start;
  }
  .view-offer-btn {
    min-height: 36px;
    font-size: 0.85rem;
    padding: 0.5rem 0.8rem;
  }
  .vendor-logo {
    width: 220px;
    height: 100px;
  }
  
  .top-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .stock-indicator {
    align-self: center;
  }
  }

  .sidebar-barcode-icon {
    width: 14px;
    height: 14px;
    margin-right: 0.3rem;
    vertical-align: middle;
    filter: drop-shadow(0 0 1px #0002);
  }

  .logo-barcode-icon {
  width: 40px !important;
  height: 2rem !important;
  object-fit: fill;
  filter: brightness(0) invert(1);
  vertical-align: middle;
  margin-right: 10px;
}

/* Multi-Barcode Search Styles */
.multi-search-section {
  margin-top: 1.5rem;
  text-align: center;
}

.multi-search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.multi-search-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.multi-search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.search-loading {
  display: inline-block;
  margin-right: 0.5rem;
}

/* Multi-Barcode Results Styles - Compact Style */
.multi-barcode-results-container {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.multi-results-title {
  color: #2d3748;
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
}

.barcode-results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.barcode-result-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.barcode-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.barcode-title {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin: 0;
}

.barcode-code {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Courier New', monospace;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  background: #f7fafc;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.barcode-type-badge {
  font-size: 0.8rem;
  color: #4a5568;
  background: #f7fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  font-weight: 500;
  text-transform: uppercase;
}

.barcode-status {
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-success {
  color: #047857;
  background: #d1fae5;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #6ee7b7;
}

.status-success::before {
  content: '✓';
  margin-right: 0.5rem;
  font-weight: bold;
}

.status-error {
  color: #dc2626;
  background: #fee2e2;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #f87171;
}

.status-error::before {
  content: '⚠';
  margin-right: 0.5rem;
  font-weight: bold;
}

.barcode-product-name {
  font-size: 1rem;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 0.8rem;
  padding: 0.5rem;
  background: #f7fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.barcode-product-name::before {
  content: '📦';
  margin-right: 0.5rem;
}

/* Use the same compact product-cards style as single barcode results */
.product-cards {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.product-card {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 0.3rem 0.5rem;
  margin-bottom: 0.15rem;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.product-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
}

.product-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  width: 100%;
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.3rem;
  width: 100%;
}

.vendor-logo {
  width: 120px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
  border: 1px solid #e2e8f0;
  padding: 0.2rem;
  background: #f8fafc;
}

.site-logo {
  max-width: 100%;
  max-height: 100%;
}

.stock-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stock-available {
  color: #059669;
  font-weight: 600;
}

.stock-unavailable {
  color: #dc2626;
  font-weight: 600;
}

.divider-line {
  height: 1px;
  background: #e2e8f0;
  margin: 1rem 0;
}

.product-details-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.product-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a202c;
}

.price-display {
  font-size: 1.15rem;
  font-weight: 700;
  color: #059669;
}

.view-offer-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
}

.view-offer-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.view-offer-btn:hover::before {
  left: 100%;
}

.view-offer-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.view-offer-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.product-image-row {
  margin-top: 1rem;
  text-align: center;
}

.product-image {
  max-width: 120px;
  max-height: 120px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f9fafb;
}

.product-description-row {
  margin-top: 0.5rem;
}

.product-description {
  color: #374151;
  font-size: 0.98rem;
  line-height: 1.5;
}

/* Multi-Save Button Styles - Compact */
.multi-save-section {
  margin-top: 1.5rem;
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.multi-save-btn {
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.multi-save-btn:hover:not(:disabled) {
  background: #059669;
}

.multi-save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-loading {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.save-loading::before {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Multi-Barcode Loading and Error States */
.multi-barcode-loading {
  text-align: center;
  padding: 2rem;
  color: #4a5568;
}

.multi-barcode-error {
  text-align: center;
  padding: 2rem;
  color: #dc2626;
  background: #fee2e2;
  border-radius: 8px;
  border: 1px solid #f87171;
  margin-top: 1rem;
}

/* Results Controls - Classic Style */
.results-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.sorting-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sort-btn {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.sort-btn:hover {
  background: #5a67d8;
}

.stock-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stock-filter input[type="checkbox"] {
  margin: 0;
}

.stock-filter label {
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 500;
}
</style>

