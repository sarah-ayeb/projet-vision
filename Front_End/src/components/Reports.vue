<template>
  <div class="app-container">
    <!-- Navigation Bar -->
    <Navigation @language-changed="handleLanguageChange" />

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
              <li class="menu-item active">
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
      <div class="reports-container">
        <div class="page-header">
          <h1>{{ t.searchReports }}</h1>
          <p>{{ t.reportsDescription }}</p>
        </div>

        <!-- Choice Chips -->
        <div class="tab-chips-container">
          <button class="tab-chip" :class="{ active: activeTab === 'barcode' }" @click="switchTab('barcode')" id="chip-barcode">
            <svg viewBox="0 0 24 24" width="18" height="18"><path d="M2 6H4V18H2V6ZM5 6H6V18H5V6ZM7 6H10V18H7V6ZM11 6H12V18H11V6ZM13 6H14V18H13V6ZM16 6H17V18H16V6ZM18 6H19V18H18V6ZM20 6H22V18H20V6Z" fill="currentColor"/></svg>
            Recherche Barcode
          </button>
          <button class="tab-chip" :class="{ active: activeTab === 'image' }" @click="switchTab('image')" id="chip-image">
            <svg viewBox="0 0 24 24" width="18" height="18"><path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="currentColor"/></svg>
            Recherche Image
          </button>
        </div>

        <!-- Loading State (barcode) -->
        <div v-if="loading && activeTab === 'barcode'" class="loading-container">
          <div class="loading-spinner"></div>
          <p>{{ t.loadingReports }}</p>
        </div>

        <!-- Error State (barcode) -->
        <div v-if="error && activeTab === 'barcode'" class="error-container">
          <div class="error-icon">⚠️</div>
          <p class="error-message">{{ error }}</p>
          <button @click="loadReports" class="retry-button">{{ t.retry }}</button>
        </div>

        <!-- Reports Stats (barcode) -->
        <div class="reports-stats" v-if="reports.length > 0 && activeTab === 'barcode'">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ reports.length }}</div>
              <div class="stat-label">{{ t.savedReports }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ totalSearches }}</div>
              <div class="stat-label">{{ t.searchesPerformed }}</div>
            </div>
          </div>
        </div>

        <!-- No Reports Message (barcode) -->
        <div v-if="reports.length === 0 && activeTab === 'barcode'" class="no-reports-message">
          <h3>{{ t.noSavedReports }}</h3>
          <p>{{ t.noReportsMessage }}</p>
          <button @click="$router.push('/barcode-search')" class="start-search-btn">
            {{ t.startSearch }}
          </button>
        </div>

        <!-- Reports List (barcode) -->
        <div v-if="reports.length > 0 && activeTab === 'barcode'" class="reports-list">
          <div 
            v-for="(report, index) in sortedReports" 
            :key="index" 
            class="report-card"
            @click="toggleReportDetails(index)"
          >
            <div class="report-header">
              <div class="report-info">
                <div class="report-barcode">{{ report.barcode }}</div>
                <div class="report-product">{{ report.productName || report.product_name || t.productNotSpecified }}</div>
                <div class="report-date">
                  <div class="search-date">{{ t.searchDate || 'Date de recherche' }}: {{ formatDate(report.searchDate || report.search_date) }}</div>
                  <div v-if="report.saved_at" class="save-date">{{ t.savedDate || 'Date de sauvegarde' }}: {{ formatDate(report.saved_at) }}</div>
                </div>
              </div>
              <div class="report-summary">
                <div class="results-count">
                  <span class="count-number">{{ report.totalResults || report.total_results }}</span>
                  <span class="count-label">{{ t.results }}</span>
                </div>
                <div class="expand-icon" :class="{ 'expanded': expandedReports.includes(index) }">
                  <span :aria-label="t.showDetails" :title="t.showDetails">▼</span>
                </div>
              </div>
            </div>

            <!-- Report Details -->
            <div v-if="expandedReports.includes(index)" class="report-details">
              <div class="results-grid">
                <div 
                  v-for="(result, resultIndex) in report.results" 
                  :key="resultIndex"
                  class="result-item"
                >
                  <div class="result-header">
                    <img 
                      :src="getSiteLogo(result.site_name)" 
                      :alt="result.site_name"
                      class="site-logo"
                      @error="handleLogoError"
                    />
                    <div class="result-info">
                      <div class="result-name">{{ result.nom || t.nameNotAvailable }}</div>
                      <div class="result-price">{{ formatPrice(result.prix) }}</div>
                    </div>
                  </div>
                  <div class="result-actions">
                    <a 
                      :href="result.lien" 
                      target="_blank" 
                      class="view-offer-btn"
                      @click.stop
                    >
                      <span class="btn-text">{{ t.viewOffer }}</span>
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                        <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
              
              <!-- Report Actions -->
              <div class="report-actions">
                <button @click.stop="exportReport(report)" class="export-btn">
                   {{ t.export }}
                </button>
                <button @click.stop="deleteReport(index)" class="delete-btn">
                   {{ t.delete }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Clear All Button (barcode) -->
        <div v-if="reports.length > 0 && activeTab === 'barcode'" class="clear-all-section">
          <button @click="clearAllReports" class="clear-all-btn">
             {{ t.deleteAllReports }}
          </button>
        </div>

        <!-- ===== IMAGE SEARCH TAB ===== -->
        <div v-if="activeTab === 'image'" class="image-tab-section">
          <div class="reports-stats" v-if="imageReports.length > 0">
            <div class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ imageReports.length }}</div>
                <div class="stat-label">Rapports image sauvegardés</div>
              </div>
            </div>
          </div>

          <div v-if="imageReports.length === 0" class="no-reports-message">
            <h3>Aucun rapport image sauvegardé</h3>
            <p>Effectuez une recherche par image et cliquez sur "🔖 Sauvegarder dans les rapports".</p>
            <button @click="$router.push('/image-search')" class="start-search-btn">Recherche par image</button>
          </div>

          <div v-if="imageReports.length > 0" class="reports-list">
            <div
              v-for="(report, idx) in sortedImageReports"
              :key="report.id"
              class="image-report-card"
              @click="toggleImageReportDetails(idx)"
            >
              <div class="image-report-header">
                <div class="image-report-thumb">
                  <img :src="report.image" class="thumb-img" alt="Produit" />
                </div>
                <div class="image-report-info">
                  <div class="image-report-name">{{ report.productName }}</div>
                  <p class="image-report-desc">{{ report.description }}</p>
                  <div v-if="report.priceRange" class="image-report-price-tag">
                    💰 {{ report.priceRange.min.toFixed(3) }} DT — {{ report.priceRange.max.toFixed(3) }} DT
                  </div>
                  <div class="image-report-meta">
                    <span>🗓 {{ formatDate(report.savedAt) }}</span>
                    &nbsp;·&nbsp;
                    <span>📦 {{ report.totalResults }} résultats</span>
                  </div>
                </div>
                <div class="report-summary">
                  <div class="expand-icon" :class="{ expanded: expandedImageReports.includes(idx) }">
                    <span>▼</span>
                  </div>
                </div>
              </div>
              <div v-if="expandedImageReports.includes(idx)" class="report-details">
                <div class="results-grid">
                  <div v-for="(result, ri) in report.results.slice(0, 10)" :key="ri" class="result-item">
                    <div class="result-header">
                      <img :src="getSiteLogo(result.site_name || result.site)" :alt="result.site_name" class="site-logo" @error="handleLogoError" />
                      <div class="result-info">
                        <div class="result-name">{{ result.nom || t.nameNotAvailable }}</div>
                        <div class="result-price">{{ formatPrice(result.prix) }}</div>
                      </div>
                    </div>
                    <div class="result-actions">
                      <a :href="result.lien || result.link" target="_blank" class="view-offer-btn" @click.stop>
                        <span class="btn-text">{{ t.viewOffer }}</span>
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none"><path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                      </a>
                    </div>
                  </div>
                </div>
                <div class="report-actions">
                  <button @click.stop="deleteImageReport(idx)" class="delete-btn">🗑 Supprimer</button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="imageReports.length > 0" class="clear-all-section">
            <button @click="clearAllImageReports" class="clear-all-btn">Supprimer tous les rapports image</button>
          </div>
        </div>
      </div>
    </main>
    </div>
  </div>
</template>

<script>
import Navigation from './Navigation.vue';
import { getCurrentTranslations } from '@/locales';
import { ref, computed } from 'vue';

export default {
  name: 'Reports',
  components: {
    Navigation
  },
  data() {
    return {
      reports: [],
      expandedReports: [],
      currentLanguage: 'fr',
      loading: false,
      error: '',
      activeTab: 'barcode',
      imageReports: [],
      expandedImageReports: []
    };
  },
  created() {
    // Detect current language from localStorage or default to French
    const savedLanguage = localStorage.getItem('language') || 'fr';
    this.currentLanguage = savedLanguage;
  },
  computed: {
    t() {
      return getCurrentTranslations(this.currentLanguage);
    },
    sortedReports() {
      return [...this.reports].sort((a, b) => new Date(b.searchDate) - new Date(a.searchDate));
    },
    totalSearches() {
      return this.reports.length;
    },
    totalResults() {
      return this.reports.reduce((total, report) => {
        const results = report.totalResults || report.total_results || 0;
        return total + (isNaN(results) ? 0 : results);
      }, 0);
    },
    sortedImageReports() {
      return [...this.imageReports].sort((a, b) => new Date(b.savedAt) - new Date(a.savedAt));
    }
  },
  mounted() {
    this.loadReports();
    this.loadImageReports();
  },
  methods: {
    handleLanguageChange(lang) {
      // Handle language change from navigation component
      console.log('Language changed to:', lang);
      this.currentLanguage = lang;
      localStorage.setItem('language', lang);
    },
    async loadReports() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch('http://localhost:8000/api/reports', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Reports API response:', data);
          this.reports = data.reports || [];
          console.log('Parsed reports:', this.reports);
          

          
          // Parse the results JSON string for each report
          this.reports.forEach(report => {
            if (report.results && typeof report.results === 'string') {
              try {
                report.results = JSON.parse(report.results);
              } catch (e) {
                console.error('Error parsing results for report:', report.id, e);
                report.results = [];
              }
            }
          });
        } else {
          console.error('Failed to load reports:', response.status);
          this.error = 'Failed to load reports from database';
        }
      } catch (error) {
        console.error('Error loading reports:', error);
        this.error = 'Network error while loading reports';
      } finally {
        this.loading = false;
      }
    },
    toggleReportDetails(index) {
      const expandedIndex = this.expandedReports.indexOf(index);
      if (expandedIndex > -1) {
        this.expandedReports.splice(expandedIndex, 1);
      } else {
        this.expandedReports.push(index);
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const language = this.currentLanguage || 'fr';
      return date.toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    formatPrice(price) {
      if (!price) return this.t.priceNotAvailable;
      if (typeof price === 'string' && (price.includes('DT') || price.includes('TND'))) {
        return price;
      }
      return `${price} DT`;
    },
    getSiteLogo(siteName) {
      if (!siteName) return '';
      
      // Try to get logo from search results first (from database)
      const result = this.reports.find(r => r.site_name === siteName);
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
        return 'https://www.cleopatre.tn/img/logo.png';
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
      event.target.style.display = 'none';
    },
    exportReport(report) {
      const dataStr = JSON.stringify(report, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `rapport-${report.barcode}-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
    },
    async deleteReport(index) {
      if (confirm(this.t.deleteReportConfirm)) {
        const report = this.reports[index];
        
        try {
          const response = await fetch(`http://localhost:8000/api/reports/${report.id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            this.reports.splice(index, 1);
            this.expandedReports = this.expandedReports.filter(i => i !== index);
          } else {
            console.error('Failed to delete report:', response.status);
            this.error = 'Failed to delete report from database';
          }
        } catch (error) {
          console.error('Error deleting report:', error);
          this.error = 'Network error while deleting report';
        }
      }
    },
    
    async clearAllReports() {
      if (confirm(this.t.deleteAllConfirm)) {
        try {
          const response = await fetch('http://localhost:8000/api/reports', {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            this.reports = [];
            this.expandedReports = [];
          } else {
            console.error('Failed to clear all reports:', response.status);
            this.error = 'Failed to clear all reports from database';
          }
        } catch (error) {
          console.error('Error clearing all reports:', error);
          this.error = 'Network error while clearing all reports';
        }
      }
    },
    loadImageReports() {
      try {
        this.imageReports = JSON.parse(localStorage.getItem('image_search_reports') || '[]');
      } catch (e) { this.imageReports = []; }
    },
    deleteImageReport(index) {
      if (confirm('Supprimer ce rapport image ?')) {
        this.imageReports.splice(index, 1);
        localStorage.setItem('image_search_reports', JSON.stringify(this.imageReports));
      }
    },
    clearAllImageReports() {
      if (confirm('Supprimer tous les rapports image ?')) {
        this.imageReports = [];
        localStorage.removeItem('image_search_reports');
      }
    },
    switchTab(tab) {
      this.activeTab = tab;
      if (tab === 'image') this.loadImageReports();
    },
    toggleImageReportDetails(index) {
      const i = this.expandedImageReports.indexOf(index);
      if (i > -1) this.expandedImageReports.splice(i, 1);
      else this.expandedImageReports.push(index);
    }
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

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  max-width: 100vw;
  background-color: #F7F9F8;
  overflow-x: hidden;
}

/* Navigation component is now used instead of custom navbar */

/* Content Wrapper */
.content-wrapper {
  display: flex;
  flex: 1;
  margin-top: 70px;
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

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  margin-left: 280px;
  background-color: #F7F9F8;
  min-height: calc(100vh - 70px);
}

.reports-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid rgba(26,127,90,0.1);
}

.page-header {
  padding: 2.5rem;
  background: white;
  color: #2d3748;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
}

.page-header h1 {
  font-size: 2.8rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
  color: #2d3748;
}

.page-header p {
  font-size: 1.2rem;
  color: #718096;
  margin: 0;
  font-weight: 400;
}

/* Loading State */
.loading-container {
  text-align: center;
  padding: 4rem 2rem;
  color: #718096;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
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

/* Error State */
.error-container {
  text-align: center;
  padding: 4rem 2rem;
  color: #ef4444;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-message {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  background: #1A7F5A;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-button:hover {
  background: #155c41;
}

/* Reports Stats */
.reports-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 2.5rem;
  color: #1A7F5A;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  color: #718096;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* No Reports Message */
.no-reports-message {
  text-align: center;
  padding: 4rem 2rem;
  color: #718096;
}

.no-reports-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-reports-message h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #4a5568;
}

.no-reports-message p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.start-search-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.start-search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(26,127,90,0.3);
}

/* Reports List */
.reports-list {
  padding: 1.5rem;
}

.report-card {
  background: white;
  border: 1px solid rgba(26,127,90,0.1);
  border-radius: 16px;
  margin-bottom: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.report-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
}

.report-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  transform: translateY(-3px);
  border-color: rgba(26,127,90,0.2);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.report-info {
  flex: 1;
}

.report-barcode {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.report-product {
  font-size: 1rem;
  color: #4a5568;
  margin-bottom: 0.25rem;
}

.report-date {
  font-size: 0.9rem;
  color: #718096;
}

.search-date {
  font-weight: 500;
  color: #4a5568;
}

.save-date {
  font-size: 0.85rem;
  color: #718096;
  margin-top: 0.2rem;
  font-style: italic;
}

.report-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.results-count {
  text-align: center;
}

.count-number {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  color: #667eea;
  text-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
}

.count-label {
  font-size: 0.9rem;
  color: #718096;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.expand-icon {
  font-size: 0.8rem;
  color: #718096;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

/* Report Details */
.report-details {
  border-top: 1px solid #e2e8f0;
  padding: 1.5rem;
  background: #f7fafc;
}

.results-grid {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.site-logo {
  width: 60px;
  height: 30px;
  object-fit: contain;
  border-radius: 4px;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.result-price {
  font-size: 0.9rem;
  color: #1A7F5A;
  font-weight: 600;
}

.result-actions {
  display: flex;
  gap: 0.5rem;
}

.view-offer-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(26,127,90,0.2);
  position: relative;
  overflow: hidden;
  border: none;
  cursor: pointer;
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
  box-shadow: 0 6px 16px rgba(26,127,90,0.3);
  background: linear-gradient(135deg, #155c41 0%, #0f2219 100%);
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
  box-shadow: 0 2px 8px rgba(26,127,90,0.2);
}

/* Report Actions */
.report-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.export-btn, .delete-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.export-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.export-btn:active, .delete-btn:active {
  transform: translateY(0);
}

/* Clear All Section */
.clear-all-section {
  padding: 1.5rem;
  text-align: center;
  border-top: 1px solid #e2e8f0;
}

.clear-all-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem 1.8rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
  position: relative;
  overflow: hidden;
}

.clear-all-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.clear-all-btn:hover::before {
  left: 100%;
}

.clear-all-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.clear-all-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: relative;
    height: auto;
    top: 0;
    margin-top: 60px;
  }
  
  .main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .page-header {
    padding: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .reports-stats {
    grid-template-columns: 1fr;
  }
  
  .report-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .result-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .report-actions {
    flex-direction: column;
  }
}
/* Tab Chips */
.tab-chips-container {
  display: flex;
  gap: 1rem;
  padding: 1.25rem 2rem;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
  justify-content: center;
  flex-wrap: wrap;
}
.tab-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.6rem;
  border: 2px solid #e2e8f0;
  border-radius: 50px;
  background: white;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.tab-chip:hover {
  border-color: #1A7F5A;
  color: #1A7F5A;
  transform: translateY(-1px);
}
.tab-chip.active {
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(26, 127, 90, 0.35);
}
/* Image Report Cards */
.image-tab-section { padding: 0; }
.image-report-card {
  background: white;
  border: 1px solid rgba(26, 127, 90, 0.1);
  border-radius: 16px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}
.image-report-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
}
.image-report-card:hover {
  box-shadow: 0 12px 32px rgba(0,0,0,0.12);
  transform: translateY(-3px);
}
.image-report-header {
  display: flex;
  gap: 1.25rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  align-items: flex-start;
}
.image-report-thumb {
  flex-shrink: 0;
  width: 100px;
  height: 100px;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  background: #f7fafc;
}
.thumb-img { width: 100%; height: 100%; object-fit: cover; }
.image-report-info { flex: 1; min-width: 0; }
.image-report-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.35rem;
  line-height: 1.3;
}
.image-report-desc {
  font-size: 0.85rem;
  color: #718096;
  line-height: 1.65;
  margin: 0 0 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.image-report-price-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: linear-gradient(135deg, #f0fff4, #e6fffa);
  border: 1px solid #9ae6b4;
  color: #276749;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.image-report-meta { font-size: 0.8rem; color: #a0aec0; }
</style>