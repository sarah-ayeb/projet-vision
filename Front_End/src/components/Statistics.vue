<template>
  <div class="app-container">
    <!-- Navigation Bar -->
    <Navigation @language-changed="handleLanguageChange" />

    <div class="content-wrapper">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>Outils de Recherche</h3>
        </div>
        <div class="sidebar-menu">
          <div class="menu-section">
            <h4>Recherche Produits</h4>
            <ul>
              <li class="menu-item" @click="$router.push('/barcode-search')">
                <svg viewBox="0 0 24 24">
                  <path d="M2 6H4V18H2V6ZM5 6H6V18H5V6ZM7 6H10V18H7V6ZM11 6H12V18H11V6ZM13 6H14V18H13V6ZM16 6H17V18H16V6ZM18 6H19V18H18V6ZM20 6H22V18H20V6Z" fill="currentColor"/>
                </svg>
                Code-Barres
              </li>
              <li class="menu-item" @click="$router.push('/image-search')">
                <svg viewBox="0 0 24 24">
                  <path d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z" fill="currentColor"/>
                </svg>
                Recherche Image
              </li>
            </ul>
          </div>
          <div class="menu-section">
            <h4>Analyses</h4>
            <ul>
              <li class="menu-item" @click="$router.push('/reports')">
                <svg viewBox="0 0 24 24">
                  <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19ZM17 12H7V10H17V12ZM13 16H7V14H13V16ZM17 8H7V6H17V8Z" fill="currentColor"/>
                </svg>
                Rapports
              </li>
              <li class="menu-item active">
                <svg viewBox="0 0 24 24">
                  <path d="M16 6L18.29 8.29L13.41 13.17L9.41 9.17L2 16.59L3.41 18L9.41 12L13.41 16L19.71 9.71L22 12V6H16Z" fill="currentColor"/>
                </svg>
                Statistiques
              </li>
            </ul>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <div class="statistics-container">
          <div class="page-header">
            <h1>{{ t.statistics }}</h1>
            <p>{{ t.statisticsDescription }}</p>
          </div>

          <!-- Period Selector -->
          <div class="period-selector">
            <div class="date-picker">
              <label>{{ t.selectPeriod }}</label>
              <select v-model="selectedPeriod" @change="updateStatistics">
                <option value="7">{{ t.last7Days }}</option>
                <option value="30">{{ t.last30Days }}</option>
                <option value="90">{{ t.last90Days }}</option>
                <option value="365">{{ t.lastYear }}</option>
              </select>
            </div>
          </div>

          <!-- Key Metrics Cards -->
          <div class="metrics-section">
            <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M2 6H4V18H2V6ZM5 6H6V18H5V6ZM7 6H10V18H7V6ZM11 6H12V18H11V6ZM13 6H14V18H13V6ZM16 6H17V18H16V6ZM18 6H19V18H18V6ZM20 6H22V18H20V6Z" fill="currentColor"/>
                </svg>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ totalBarcodeSearches }}</h3>
                <p class="metric-label">{{ t.totalBarcodeSearches }}</p>
                <div class="metric-change positive">
                  <span>+{{ barcodeGrowth }}%</span>
                  <span>{{ t.fromLastPeriod }}</span>
                </div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
                  <path d="M12 6C8.69 6 6 8.69 6 12C6 15.31 8.69 18 12 18C15.31 18 18 15.31 18 12C18 8.69 15.31 6 12 6Z" fill="currentColor"/>
                </svg>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ totalWebsites }}</h3>
                <p class="metric-label">{{ t.totalWebsites }}</p>
                <div class="metric-change positive">
                  <span>+{{ websiteGrowth }}%</span>
                  <span>{{ t.fromLastPeriod }}</span>
                </div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
                </svg>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">€{{ averageSavings }}</h3>
                <p class="metric-label">{{ t.averageSavings }}</p>
                <div class="metric-change positive">
                  <span>+{{ savingsGrowth }}%</span>
                  <span>{{ t.fromLastPeriod }}</span>
                </div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M9 11H7C5.9 11 5 11.9 5 13V19C5 20.1 5.9 21 7 21H9C10.1 21 11 20.1 11 19V13C11 11.9 10.1 11 9 11Z" fill="currentColor"/>
                  <path d="M17 3H15C13.9 3 13 3.9 13 5V19C13 20.1 13.9 21 15 21H17C18.1 21 19 20.1 19 19V5C19 3.9 18.1 3 17 3Z" fill="currentColor"/>
                </svg>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ successRate }}%</h3>
                <p class="metric-label">{{ t.successRate }}</p>
                <div class="metric-change positive">
                  <span>+{{ successGrowth }}%</span>
                  <span>{{ t.fromLastPeriod }}</span>
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- Website Performance Analysis -->
          <div class="analysis-section">
            <div class="section-header">
              <h2>{{ t.websitePerformance }}</h2>
              <p>{{ t.websitePerformanceDescription }}</p>
            </div>
            
            <div class="website-grid">
              <div class="website-card" v-for="website in topWebsites" :key="website.id">
                <div class="website-header">
                  <div class="website-info">
                    <h3>{{ website.name }}</h3>
                    <span class="website-url">{{ website.url }}</span>
                  </div>
                  <div class="website-status" :class="website.status">
                    {{ getStatusText(website.status) }}
                  </div>
                </div>
                
                <div class="website-metrics">
                  <div class="metric-row">
                    <span>{{ t.productsFound }}</span>
                    <span class="metric-value">{{ website.productsFound }}</span>
                  </div>
                  <div class="metric-row">
                    <span>{{ t.averagePrice }}</span>
                    <span class="metric-value">€{{ website.averagePrice }}</span>
                  </div>
                  <div class="metric-row">
                    <span>{{ t.successRate }}</span>
                    <span class="metric-value">{{ website.successRate }}%</span>
                  </div>
                  <div class="metric-row">
                    <span>{{ t.lastScraped }}</span>
                    <span class="metric-value">{{ formatDate(website.lastScraped) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Price Analysis -->
          <div class="pricing-section">
            <div class="section-header">
              <h2>{{ t.pricingAnalysis }}</h2>
              <p>{{ t.pricingAnalysisDescription }}</p>
            </div>
            
            <div class="pricing-grid">
              <div class="pricing-card cheapest">
                <div class="pricing-header">
                  <h3>{{ t.cheapestWebsite }}</h3>
                  <div class="price-badge">€{{ cheapestWebsite.averagePrice }}</div>
                </div>
                <div class="pricing-details">
                  <p><strong>{{ cheapestWebsite.name }}</strong></p>
                  <p>{{ t.averagePrice }}: €{{ cheapestWebsite.averagePrice }}</p>
                  <p>{{ t.productsFound }}: {{ cheapestWebsite.productsFound }}</p>
                  <p>{{ t.successRate }}: {{ cheapestWebsite.successRate }}%</p>
                </div>
              </div>
              
              <div class="pricing-card most-expensive">
                <div class="pricing-header">
                  <h3>{{ t.mostExpensiveWebsite }}</h3>
                  <div class="price-badge">€{{ mostExpensiveWebsite.averagePrice }}</div>
                </div>
                <div class="pricing-details">
                  <p><strong>{{ mostExpensiveWebsite.name }}</strong></p>
                  <p>{{ t.averagePrice }}: €{{ mostExpensiveWebsite.averagePrice }}</p>
                  <p>{{ t.productsFound }}: {{ mostExpensiveWebsite.productsFound }}</p>
                  <p>{{ t.successRate }}: {{ mostExpensiveWebsite.successRate }}%</p>
                </div>
              </div>
              
              <div class="pricing-card savings">
                <div class="pricing-header">
                  <h3>{{ t.totalSavings }}</h3>
                  <div class="savings-badge">€{{ totalSavings }}</div>
                </div>
                <div class="savings-details">
                  <p>{{ t.moneySaved }}: <strong>€{{ totalSavings }}</strong></p>
                  <p>{{ t.averageSavingsPerProduct }}: <strong>€{{ averageSavingsPerProduct }}</strong></p>
                  <p>{{ t.bestDealsFound }}: <strong>{{ bestDealsFound }}</strong></p>
                </div>
              </div>
            </div>
          </div>

          <!-- Barcode Search Results -->
          <div class="barcode-results-section">
            <div class="section-header">
              <h2>{{ t.barcodeSearchResults }}</h2>
              <p>{{ t.barcodeSearchDescription }}</p>
            </div>
            
            <div class="results-grid">
              <div class="result-card">
                <div class="result-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M2 6H4V18H2V6ZM5 6H6V18H5V6ZM7 6H10V18H7V6ZM11 6H12V18H11V6ZM13 6H14V18H13V6ZM16 6H17V18H16V6ZM18 6H19V18H18V6ZM20 6H22V18H20V6Z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="result-content">
                  <h3>{{ t.successfulSearches }}</h3>
                  <p class="result-value">{{ successfulSearches }}</p>
                  <p class="result-percentage">{{ (successfulSearches / totalBarcodeSearches * 100).toFixed(1) }}%</p>
                </div>
              </div>
              
              <div class="result-card">
                <div class="result-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="result-content">
                  <h3>{{ t.failedSearches }}</h3>
                  <p class="result-value">{{ failedSearches }}</p>
                  <p class="result-percentage">{{ (failedSearches / totalBarcodeSearches * 100).toFixed(1) }}%</p>
                </div>
              </div>
              
              <div class="result-card">
                <div class="result-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
                    <path d="M2 17L12 22L22 17" fill="currentColor"/>
                    <path d="M2 12L12 17L22 12" fill="currentColor"/>
                  </svg>
                </div>
                <div class="result-content">
                  <h3>{{ t.uniqueProducts }}</h3>
                  <p class="result-value">{{ uniqueProductsFound }}</p>
                  <p class="result-percentage">{{ (uniqueProductsFound / totalBarcodeSearches * 100).toFixed(1) }}%</p>
                </div>
              </div>
              
              <div class="result-card">
                <div class="result-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor"/>
                    <path d="M12 6C8.69 6 6 8.69 6 12C6 15.31 8.69 18 12 18C15.31 18 18 15.31 18 12C18 8.69 15.31 6 12 6Z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="result-content">
                  <h3>{{ t.averagePriceFound }}</h3>
                  <p class="result-value">€{{ averagePriceFound }}</p>
                  <p class="result-percentage">{{ t.perProduct }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Charts Section -->
          <div class="charts-section">
            <div class="chart-container">
              <div class="chart-header">
                <h3>{{ t.scrapingTrends }}</h3>
                <div class="chart-controls">
                  <button 
                    v-for="period in chartPeriods" 
                    :key="period.value"
                    @click="changeChartPeriod(period.value)"
                    :class="['chart-btn', { active: currentChartPeriod === period.value }]"
                  >
                    {{ period.label }}
                  </button>
                </div>
              </div>
              <div class="chart-content">
                <canvas ref="scrapingChart" width="400" height="200"></canvas>
              </div>
            </div>

            <div class="chart-container">
              <div class="chart-header">
                <h3>{{ t.successRateByDay }}</h3>
              </div>
              <div class="chart-content">
                <canvas ref="successChart" width="400" height="200"></canvas>
              </div>
            </div>
          </div>

          <!-- Detailed Statistics Table -->
          <div class="table-section">
            <div class="table-header">
              <h3>{{ t.detailedStatistics }}</h3>
              <div class="table-controls">
                <input 
                  v-model="searchTerm" 
                  :placeholder="t.searchProducts" 
                  class="search-input"
                />
                <select v-model="sortBy" @change="sortTable">
                  <option value="date">{{ t.sortByDate }}</option>
                  <option value="success">{{ t.sortBySuccess }}</option>
                  <option value="time">{{ t.sortByTime }}</option>
                </select>
              </div>
            </div>
            
            <div class="table-container">
              <table class="statistics-table">
                <thead>
                  <tr>
                    <th>{{ t.date }}</th>
                    <th>{{ t.productName }}</th>
                    <th>{{ t.barcode }}</th>
                    <th>{{ t.status }}</th>
                    <th>{{ t.duration }}</th>
                    <th>{{ t.dataExtracted }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in filteredTableData" :key="item.id">
                    <td>{{ formatDate(item.date) }}</td>
                    <td>{{ item.productName }}</td>
                    <td>{{ item.barcode }}</td>
                    <td>
                      <span :class="['status-badge', item.status]">
                        {{ getStatusText(item.status) }}
                      </span>
                    </td>
                    <td>{{ item.duration }}s</td>
                    <td>{{ item.dataExtracted }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Export Section -->
          <div class="export-section">
            <div class="export-content">
              <h3>{{ t.exportData }}</h3>
              <p>{{ t.exportDescription }}</p>
              <div class="export-buttons">
                <button @click="exportToCSV" class="export-btn csv">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="currentColor"/>
                  </svg>
                  {{ t.exportCSV }}
                </button>
                <button @click="exportToPDF" class="export-btn pdf">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M20 2H8C6.9 2 6 2.9 6 4V16C6 17.1 6.9 18 8 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H8V4H20V16Z" fill="currentColor"/>
                  </svg>
                  {{ t.exportPDF }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentTranslations } from '@/locales';
import Navigation from './Navigation.vue';

const router = useRouter();

// Translation setup
const currentLanguage = ref('fr');
const t = computed(() => {
  return getCurrentTranslations(currentLanguage.value);
});

// Reactive data
const selectedPeriod = ref('30');
const currentChartPeriod = ref('week');
const searchTerm = ref('');
const sortBy = ref('date');

// Chart references
const scrapingChart = ref(null);
const successChart = ref(null);

// Mock data - replace with actual API calls
const totalBarcodeSearches = ref(1500);
const barcodeGrowth = ref(10.5);
const totalWebsites = ref(120);
const websiteGrowth = ref(8.2);
const averageSavings = ref(15.7);
const savingsGrowth = ref(12.1);
const successRate = ref(94.2);
const successGrowth = ref(3.2);
const successfulSearches = ref(1350);
const failedSearches = ref(150);
const uniqueProductsFound = ref(1200);
const averagePriceFound = ref(12.5);

// Website performance data
const topWebsites = ref([
  {
    id: 1,
    name: 'Amazon',
    url: 'amazon.com',
    status: 'success',
    productsFound: 456,
    averagePrice: 45.20,
    successRate: 98.5,
    lastScraped: '2024-01-15'
  },
  {
    id: 2,
    name: 'eBay',
    url: 'ebay.com',
    status: 'success',
    productsFound: 234,
    averagePrice: 32.15,
    successRate: 92.3,
    lastScraped: '2024-01-14'
  },
  {
    id: 3,
    name: 'Walmart',
    url: 'walmart.com',
    status: 'success',
    productsFound: 189,
    averagePrice: 28.90,
    successRate: 95.7,
    lastScraped: '2024-01-13'
  },
  {
    id: 4,
    name: 'Target',
    url: 'target.com',
    status: 'error',
    productsFound: 123,
    averagePrice: 35.60,
    successRate: 87.2,
    lastScraped: '2024-01-10'
  }
]);

// Pricing analysis data
const cheapestWebsite = computed(() => {
  return topWebsites.value.reduce((min, website) => 
    website.averagePrice < min.averagePrice ? website : min
  );
});

const mostExpensiveWebsite = computed(() => {
  return topWebsites.value.reduce((max, website) => 
    website.averagePrice > max.averagePrice ? website : max
  );
});

// Economic data
const totalSavings = ref(1800);
const averageSavingsPerProduct = ref(1.2);
const bestDealsFound = ref(50);

// Chart periods
const chartPeriods = [
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
  { value: 'quarter', label: 'Quarter' }
];

// Mock table data
const tableData = ref([
  {
    id: 1,
    date: '2024-01-15',
    productName: 'Product A',
    barcode: '1234567890123',
    status: 'success',
    duration: 2.1,
    dataExtracted: 'Name, Price, Image'
  },
  {
    id: 2,
    date: '2024-01-14',
    productName: 'Product B',
    barcode: '9876543210987',
    status: 'error',
    duration: 5.2,
    dataExtracted: 'Name only'
  },
  // Add more mock data as needed
]);

// Computed properties
const filteredTableData = computed(() => {
  let filtered = tableData.value;
  
  if (searchTerm.value) {
    filtered = filtered.filter(item => 
      item.productName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      item.barcode.includes(searchTerm.value)
    );
  }
  
  return filtered;
});

// Methods
const handleLanguageChange = (lang) => {
  // Handle language change from navigation component
  currentLanguage.value = lang;
  console.log('Language changed to:', lang);
  // You can add any language-specific logic here
};

const updateStatistics = () => {
  // Update statistics based on selected period
  console.log('Updating statistics for period:', selectedPeriod.value);
  // Add API call here
};

const changeChartPeriod = (period) => {
  currentChartPeriod.value = period;
  updateCharts();
};

const updateCharts = () => {
  // Update charts with new data
  console.log('Updating charts for period:', currentChartPeriod.value);
  // Add chart update logic here
};

const sortTable = () => {
  // Sort table data based on selected criteria
  console.log('Sorting table by:', sortBy.value);
  // Add sorting logic here
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const getStatusText = (status) => {
  const statusMap = {
    success: 'Success',
    error: 'Error',
    pending: 'Pending'
  };
  return statusMap[status] || status;
};

const exportToCSV = () => {
  // Export data to CSV
  console.log('Exporting to CSV');
  // Add CSV export logic here
};

const exportToPDF = () => {
  // Export data to PDF
  console.log('Exporting to PDF');
  // Add PDF export logic here
};

// Lifecycle
onMounted(() => {
  // Initialize charts and load data
  updateStatistics();
  updateCharts();
});

// Watchers
watch(selectedPeriod, () => {
  updateStatistics();
});

watch(currentChartPeriod, () => {
  updateCharts();
});
</script>

<style scoped>
/* App Container */
.app-container {
  min-height: 100vh;
  background-color: #F7F9F8;
  overflow-x: hidden;
}

/* Navigation component is now used instead of custom navbar */

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

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem;
  margin-left: 280px;
  background-color: #F7F9F8;
  min-height: calc(100vh - 70px);
}

.statistics-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.page-header {
  padding: 2rem;
  background: white;
  color: #2d3748;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.page-header p {
  font-size: 1.1rem;
  color: #718096;
}

/* Period Selector */
.period-selector {
  padding: 1.5rem;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.date-picker label {
  font-weight: 600;
  color: #2d3748;
}

.date-picker select {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  min-width: 150px;
}

.metrics-section {
  padding: 1.5rem;
  background: #f7fafc;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.metric-icon svg {
  width: 32px;
  height: 32px;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.metric-label {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
}

.metric-change.positive {
  color: #38a169;
}

.metric-change.negative {
  color: #e53e3e;
}

.charts-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.chart-container {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.chart-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.chart-content {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7fafc;
  border-radius: 8px;
}

.table-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
}

.table-controls {
  display: flex;
  gap: 1rem;
}

.search-input {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 200px;
}

.table-controls select {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
}

.statistics-table {
  width: 100%;
  border-collapse: collapse;
}

.statistics-table th,
.statistics-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.statistics-table th {
  background: #f7fafc;
  font-weight: 600;
  color: #2d3748;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.success {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.error {
  background: #fed7d7;
  color: #c53030;
}

.status-badge.pending {
  background: #fef5e7;
  color: #c05621;
}

.export-section {
  padding: 1.5rem;
}

.export-content h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.export-content p {
  color: #718096;
  margin-bottom: 1.5rem;
}

.export-buttons {
  display: flex;
  gap: 1rem;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn.csv {
  background: #38a169;
  color: white;
}

.export-btn.csv:hover {
  background: #2f855a;
}

.export-btn.pdf {
  background: #e53e3e;
  color: white;
}

.export-btn.pdf:hover {
  background: #c53030;
}

.export-btn svg {
  width: 20px;
  height: 20px;
}

/* Analysis Sections */
.analysis-section, .pricing-section, .barcode-results-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
}

.section-header p {
  color: #718096;
  font-size: 1rem;
}

.website-grid, .pricing-grid, .results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.website-card, .pricing-card, .result-card {
  background: #f7fafc;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid #e2e8f0;
}

.website-header, .pricing-header, .result-icon {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.website-info, .pricing-details, .savings-details {
  display: flex;
  flex-direction: column;
}

.website-url, .price-badge, .savings-badge {
  font-size: 0.9rem;
  color: #718096;
  margin-top: 0.25rem;
}

.website-status {
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
}

.website-status.success {
  background: #c6f6d5;
  color: #22543d;
}

.website-status.error {
  background: #fed7d7;
  color: #c53030;
}

.website-metrics, .website-details, .pricing-details, .savings-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #4a5568;
}

.metric-value {
  font-weight: 600;
  color: #1a202c;
}

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.result-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.result-percentage {
  font-size: 0.9rem;
  color: #718096;
}

/* Responsive Design */
@media (max-width: 768px) {

  .content-wrapper {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .main-content {
    padding: 1rem;
    margin-left: 0;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .table-header {
    flex-direction: column;
    gap: 1rem;
  }

  .table-controls {
    flex-direction: column;
    width: 100%;
  }

  .export-buttons {
    flex-direction: column;
  }

  .analysis-section, .pricing-section, .barcode-results-section {
    padding: 1rem;
  }

  .website-grid, .pricing-grid, .results-grid {
    grid-template-columns: 1fr;
  }
}
</style> 