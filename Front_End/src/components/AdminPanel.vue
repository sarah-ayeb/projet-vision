<template>
  <div class="admin-layout">
    <!-- Navigation Bar -->
    <Navigation @language-changed="handleLanguageChange" />
    
    <div class="admin-container">
      <!-- Sidebar -->
      <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <div class="sidebar-header">
          <h3>{{ t.adminPanel }}</h3>
        </div>
        
        <div class="sidebar-menu">
          <ul>
            <li class="menu-item" @click="goToProfile">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
              </svg>
              <span v-show="!sidebarCollapsed">{{ t.profile }}</span>
              <div class="menu-tooltip" v-show="sidebarCollapsed">{{ t.profile }}</div>
            </li>
            
            <li class="menu-item active" @click="goToAdminPanel">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" fill="currentColor"/>
              </svg>
              <span v-show="!sidebarCollapsed">{{ t.adminPanel }}</span>
              <div class="menu-tooltip" v-show="sidebarCollapsed">{{ t.adminPanel }}</div>
            </li>
            
            <li class="menu-separator" v-show="!sidebarCollapsed"></li>
            
            <li class="menu-item sign-out" @click="signOut">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M17 7L15.59 8.41L18.17 11H8V13H18.17L15.59 15.59L17 17L22 12L17 7ZM4 5H12V3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H12V19H4V5Z" fill="currentColor"/>
              </svg>
              <span v-show="!sidebarCollapsed">{{ t.signOut }}</span>
              <div class="menu-tooltip" v-show="sidebarCollapsed">{{ t.signOut }}</div>
            </li>
          </ul>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content" :class="{ 'main-content-expanded': sidebarCollapsed }">
        <div class="content-header" style="border-bottom:1px solid var(--color-border, #e2e8f0); margin-bottom: 2rem; padding-bottom: 0; display:flex; gap:2.5rem;">
          <div 
            @click="activeSection = 'sites'"
            :style="activeSection === 'sites' ? 'color:#667eea; border-bottom:3px solid #667eea; padding-bottom:1rem; cursor:pointer; font-weight:bold; font-size:1.5rem;' : 'color:#a0aec0; border-bottom:3px solid transparent; padding-bottom:1rem; cursor:pointer; font-size:1.5rem;'"
          >
            {{ t.siteManagement || 'Gestion des Sites' }}
          </div>
          <div 
            @click="activeSection = 'settings'"
            :style="activeSection === 'settings' ? 'color:#667eea; border-bottom:3px solid #667eea; padding-bottom:1rem; cursor:pointer; font-weight:bold; font-size:1.5rem;' : 'color:#a0aec0; border-bottom:3px solid transparent; padding-bottom:1rem; cursor:pointer; font-size:1.5rem;'"
          >
            {{ t.settings || 'Paramètres' }}
          </div>
        </div>

        <!-- Site Management Section -->
        <div v-if="activeSection === 'sites'" class="content-section">
          <!-- Add New Site Form -->
          <div class="form-card">
            <div class="card-header">
              <h3>{{ isEditMode ? t.editSite : t.addNewSite }}</h3>
              <p>{{ isEditMode ? t.editSiteDesc : t.addNewSiteDesc }}</p>
              <div v-if="isEditMode" class="edit-mode-indicator">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                </svg>
                {{ t.editModeActive }}
              </div>
            </div>
            
            <form @submit.prevent="isEditMode ? saveChanges() : addNewSite()" class="site-form">
              <div class="form-grid">
                <div class="form-group">
                  <label for="siteName">{{ t.siteName }}</label>
                  <input 
                    id="siteName"
                    v-model="newSite.site_name" 
                    type="text" 
                    required 
                    :placeholder="t.siteNamePlaceholder"
                  />
                </div>
                
                <div class="form-group">
                  <label for="searchUrl">{{ t.searchUrl }}</label>
                  <div class="input-with-buttons">
                    <input 
                      id="searchUrl"
                      v-model="newSite.search_url" 
                      type="url" 
                      required 
                      :placeholder="t.searchUrlPlaceholder"
                    />
                    <div class="input-buttons">
                      <button 
                        type="button" 
                        @click="discoverSelectors" 
                        class="btn-discover"
                        :disabled="discoveringSelectors || !newSite.search_url"
                        title="Discover selectors automatically"
                      >
                        <svg v-if="discoveringSelectors" viewBox="0 0 24 24" fill="none" class="loading-spinner">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" class="btn-icon">
                          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="currentColor"/>
                        </svg>
                        {{ discoveringSelectors ? 'Discovering...' : 'Discover' }}
                      </button>
                      <button 
                        type="button" 
                        @click="testCurrentSelectors" 
                        class="btn-test"
                        :disabled="testingSelectors || !newSite.search_url"
                        title="Test current selectors"
                      >
                        <svg v-if="testingSelectors" viewBox="0 0 24 24" fill="none" class="loading-spinner">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" class="btn-icon">
                          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/>
                        </svg>
                        {{ testingSelectors ? 'Testing...' : 'Test' }}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="productLinks">{{ t.productLinksSelector }}</label>
                  <input 
                    id="productLinks"
                    v-model="newSite.selectors.product_links" 
                    type="text" 
                    required 
                    :placeholder="t.productLinksPlaceholder"
                  />
                </div>
                
                <div class="form-group">
                  <label for="productName">{{ t.productNameSelector }}</label>
                  <input 
                    id="productName"
                    v-model="newSite.selectors.product_name" 
                    type="text" 
                    required 
                    :placeholder="t.productNamePlaceholder"
                  />
                </div>
                
                <div class="form-group">
                  <label for="productPrice">{{ t.productPriceSelector }}</label>
                  <input 
                    id="productPrice"
                    v-model="newSite.selectors.product_price" 
                    type="text" 
                    required 
                    :placeholder="t.productPricePlaceholder"
                  />
                </div>
                
                <div class="form-group">
                  <label for="productImage">{{ t.productImageSelector }}</label>
                  <input 
                    id="productImage"
                    v-model="newSite.selectors.product_image" 
                    type="text" 
                    :placeholder="t.productImagePlaceholder"
                  />
                </div>
                
                <div class="form-group">
                  <label for="productReference">{{ t.productReferenceSelector }}</label>
                  <input 
                    id="productReference"
                    v-model="newSite.selectors.product_reference" 
                    type="text" 
                    :placeholder="t.productReferencePlaceholder"
                  />
                </div>
              </div>
              
              <div class="form-actions">
                <div class="button-group">
                  <button type="submit" class="btn-primary" :disabled="saving">
                    <svg v-if="saving" viewBox="0 0 24 24" fill="none" class="loading-spinner">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                    </svg>
                    <svg v-else-if="isEditMode" viewBox="0 0 24 24" fill="none" class="btn-icon">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" class="btn-icon">
                      <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/>
                    </svg>
                    {{ saving ? t.saving : (isEditMode ? t.saveChanges : t.addSite) }}
                  </button>
                  <button type="button" @click="resetForm" class="btn-secondary">
                    <svg v-if="isEditMode" viewBox="0 0 24 24" fill="none" class="btn-icon">
                      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" class="btn-icon">
                      <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z" fill="currentColor"/>
                    </svg>
                    {{ isEditMode ? t.cancel : t.reset }}
                  </button>
                </div>
              </div>
            </form>
          </div>

          <!-- Existing Sites List -->
          <div class="sites-card">
            <div class="card-header">
              <h3>{{ t.existingSites }}</h3>
              <p>{{ t.existingSitesDesc }}</p>
            </div>
            
            <div class="sites-list">
              <div v-for="site in existingSites" :key="site.site_name" class="site-item">
                <div class="site-info">
                  <div class="site-header">
                    <h4>{{ site.site_name }}</h4>
                    <span class="site-status" :class="{ active: site.is_active }" @click="toggleSiteStatus(site.id)">
                      {{ site.is_active ? t.active : t.inactive }}
                    </span>
                  </div>
                  <p class="site-url">{{ site.search_url }}</p>
                  <div class="site-meta">
                    <span class="meta-item">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                      </svg>
                      {{ t.selectors }}: {{ Object.keys(site.selectors).length }}
                    </span>
                  </div>
                </div>
                <div class="site-actions">
                  <button @click="editSite(site)" class="btn-edit" :title="t.edit">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button @click="deleteSite(site.id)" class="btn-delete" :title="t.delete">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </div>
              
              <div v-if="existingSites.length === 0" class="empty-state">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                </svg>
                <h4>{{ t.noSitesYet }}</h4>
                <p>{{ t.noSitesDesc }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Section -->
        <div v-if="activeSection === 'settings'" class="content-section">
          <div class="settings-card">
            <div class="card-header">
              <h3>{{ t.generalSettings }}</h3>
              <p>{{ t.generalSettingsDesc }}</p>
            </div>
            
            <div class="settings-form">
              <div class="setting-item">
                <div class="setting-info">
                  <h4>{{ t.autoScraping }}</h4>
                  <p>{{ t.autoScrapingDesc }}</p>
                </div>
                <div class="setting-control">
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.autoScraping" />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>
              
              <div class="setting-item">
                <div class="setting-info">
                  <h4>{{ t.notifications }}</h4>
                  <p>{{ t.notificationsDesc }}</p>
                </div>
                <div class="setting-control">
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.notifications" />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>
              
              <div class="setting-item">
                <div class="setting-info">
                  <h4>{{ t.scrapingInterval }}</h4>
                  <p>{{ t.scrapingIntervalDesc }}</p>
                </div>
                <div class="setting-control">
                  <select v-model="settings.scrapingInterval" class="form-select">
                    <option value="30">{{ t.every30Minutes }}</option>
                    <option value="60">{{ t.everyHour }}</option>
                    <option value="120">{{ t.every2Hours }}</option>
                    <option value="360">{{ t.every6Hours }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- ═══ Paramètres de Recherche Image ═══ -->
          <div class="settings-card" style="margin-top:1.5rem;">
            <div class="card-header">
              <h3>🔍 Paramètres de Recherche Image</h3>
              <p>Configurez le pipeline YOLO + FAISS utilisé pour la recherche par image.</p>
            </div>
            <div class="settings-form">

              <!-- Similarity threshold -->
              <div class="setting-item" style="flex-direction:column;align-items:flex-start;gap:.75rem;">
                <div class="setting-info">
                  <h4>Seuil de Similarité (min_faiss_score)</h4>
                  <p>Score FAISS minimum pour qu'un résultat soit inclus. Valeur actuelle&nbsp;: <strong>{{ (imageSearchSettings.similarityThreshold * 100).toFixed(0) }}%</strong></p>
                </div>
                <div style="width:100%;display:flex;align-items:center;gap:1rem;">
                  <input type="range" v-model.number="imageSearchSettings.similarityThreshold"
                    min="0.50" max="0.99" step="0.01"
                    style="flex:1;accent-color:#667eea;"
                    @input="saveImageSearchSettings" />
                  <span style="min-width:48px;font-weight:700;color:#667eea;">{{ (imageSearchSettings.similarityThreshold*100).toFixed(0) }}%</span>
                </div>
                <div style="display:flex;gap:.5rem;flex-wrap:wrap;">
                  <button v-for="v in [0.80,0.85,0.88,0.90,0.95]" :key="v"
                    @click="imageSearchSettings.similarityThreshold=v;saveImageSearchSettings()"
                    :style="imageSearchSettings.similarityThreshold===v
                      ?'background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;'
                      :'background:#f1f5f9;color:#4a5568;border:1px solid #e2e8f0;'"
                    style="padding:.3rem .8rem;border-radius:20px;cursor:pointer;font-size:.82rem;font-weight:600;transition:all .2s;">
                    {{ (v*100).toFixed(0) }}%
                  </button>
                </div>
              </div>

              <!-- Brand filter -->
              <div class="setting-item">
                <div class="setting-info">
                  <h4>Filtrage par Marque</h4>
                  <p>N'afficher que les résultats dont le nom contient la même marque que le produit détecté (ex: ACM, Uriage…).</p>
                </div>
                <div class="setting-control">
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="imageSearchSettings.brandFilter" @change="saveImageSearchSettings" />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <!-- Max results -->
              <div class="setting-item">
                <div class="setting-info">
                  <h4>Nombre Maximum de Résultats</h4>
                  <p>Limite le nombre de résultats affichés après filtrage.</p>
                </div>
                <div class="setting-control">
                  <select v-model.number="imageSearchSettings.maxResults" class="form-select" @change="saveImageSearchSettings">
                    <option :value="10">10 résultats</option>
                    <option :value="20">20 résultats</option>
                    <option :value="30">30 résultats</option>
                    <option :value="50">50 résultats (tous)</option>
                  </select>
                </div>
              </div>

              <!-- Cache -->
              <div class="setting-item" style="display:flex; justify-content:space-between; align-items:center;">
                <div class="setting-info" style="flex:1;">
                  <h4>Cache des Résultats</h4>
                  <p>Mémorise les résultats 24h pour éviter de relancer le pipeline sur la même image.</p>
                </div>
                <div class="setting-control" style="display:flex; align-items:center; gap:1.5rem;">
                  <button @click="clearImageCache" class="btn-secondary" style="font-size:0.875rem; padding:0.4rem 0.8rem; display:flex; align-items:center; gap:0.4rem;">
                    <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
                      <path d="M15 16h4v2h-4v-2zm0-8h7v2h-7V8zm0 4h6v2h-6v-2zM3 18c0 1.1.9 2 2 2h6c1.1 0 2-.9 2-2V8H3v10zM14 5h-3l-1-1H6L5 5H2v2h12V5z" fill="currentColor"/>
                    </svg>
                    Vider le Cache
                  </button>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="imageSearchSettings.cacheEnabled" @change="saveImageSearchSettings" />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <!-- Stock filter -->
              <div class="setting-item">
                <div class="setting-info">
                  <h4>Afficher uniquement les produits en stock</h4>
                  <p>Masque par défaut les produits en rupture de stock.</p>
                </div>
                <div class="setting-control">
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="imageSearchSettings.filterInStock" @change="saveImageSearchSettings" />
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div style="margin-top:.5rem;">
                <button @click="saveImageSearchSettings" class="btn-primary">
                  <svg viewBox="0 0 24 24" fill="none" class="btn-icon"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z" fill="currentColor"/></svg>
                  Sauvegarder les paramètres
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', messageType]">
      <svg v-if="messageType === 'success'" viewBox="0 0 24 24" fill="none">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/>
      </svg>
      <svg v-else-if="messageType === 'error'" viewBox="0 0 24 24" fill="none">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
      </svg>
      {{ message }}
    </div>

    <!-- Selector Discovery Modal -->
    <div v-if="showSelectorDiscovery" class="modal-overlay" @click="closeSelectorDiscovery">
      <div class="modal-content discovery-modal" @click.stop>
        <div class="modal-header">
          <h3>🔍 Découvrir la Structure de Données</h3>
          <button @click="closeSelectorDiscovery" class="modal-close">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Discovery Form -->
          <div class="discovery-form">
            <div class="form-group">
              <label for="discoveryUrl">URL du Site Web:</label>
              <div class="url-input-group">
                <input 
                  id="discoveryUrl"
                  v-model="discoveryUrl" 
                  type="url" 
                  placeholder="https://example.com" 
                  class="url-input" 
                  required 
                />
                <button 
                  @click="analyzeWebsiteForSelectors" 
                  :disabled="isAnalyzing || !discoveryUrl"
                  class="analyze-btn"
                >
                  <span v-if="isAnalyzing" class="loading-spinner"></span>
                  {{ isAnalyzing ? 'Analyse en cours...' : 'Analyser le Site' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Analysis Results -->
          <div v-if="analysisResults" class="analysis-results">
            <div class="analysis-header">
              <h3>Résultats d'Analyse</h3>
              <div class="confidence-score">
                <span class="score-label">Score de Confiance:</span>
                <span class="score-value" :class="getConfidenceClass(displayConfidenceScore)">
                  {{ displayConfidenceScore }}%
                </span>
              </div>
            </div>

            <div class="analysis-grid">
              <!-- Detected Selectors -->
              <div class="analysis-card full-width detected-selectors-card">
                <h4>Sélecteurs Détectés</h4>
                <div class="selectors-list">
                  <div v-for="(selector, key) in analysisResults.detected_selectors" :key="key" class="selector-item">
                    <span class="selector-label">{{ getSelectorLabel(key) }}:</span>
                    <code class="selector-value">{{ selector }}</code>
                    <span class="validation-status" :class="getValidationClass(key)">
                      {{ getValidationStatus(key) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Sample Products Preview -->
              <div class="analysis-card full-width" v-if="analysisResults.sample_products?.length">
                <h4>Échantillons de Produits</h4>
                <div class="sample-products">
                  <div v-for="(product, index) in analysisResults.sample_products" :key="index" class="sample-product">
                    <div class="sample-product-image">
                      <img v-if="(product.image_url || product.image || product.photo) && !isPlaceholderImage(product.image_url || product.image || product.photo)" :src="product.image_url || product.image || product.photo" :alt="product.name || product.title" />
                      <div v-else class="no-image">Pas d'image</div>
                    </div>
                    <div class="sample-product-info">
                      <h5>{{ product.name || product.title || 'Pas de nom' }}</h5>
                      <p class="sample-price">{{ product.price || product.cost || 'Pas de prix' }}</p>
                      <div class="sample-link" v-if="product.product_url || product.link || product.url">
                        <a :href="product.product_url || product.link || product.url" target="_blank" class="view-link">Voir le Produit</a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="discovery-actions">
              <button @click="applyDetectedSelectors" class="apply-btn">
                Appliquer les Sélecteurs
              </button>
              <button @click="closeSelectorDiscovery" class="close-btn">
                Fermer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selector Test Results Modal -->
    <div v-if="Object.keys(selectorTestResults).length > 0" class="modal-overlay" @click="selectorTestResults = {}">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3> Selector Test Results</h3>
          <button @click="selectorTestResults = {}" class="modal-close">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="test-results">
            <div v-for="(result, selectorType) in selectorTestResults" :key="selectorType" class="test-result">
              <div class="result-header">
                <h4>{{ selectorType.replace('_', ' ').toUpperCase() }}</h4>
                <span :class="['result-status', result.success && result.count > 0 ? 'success' : 'error']">
                  {{ result.success && result.count > 0 ? '✅ Working' : '❌ Not working' }}
                </span>
              </div>
              <div class="result-details">
                <p><strong>Elements found:</strong> {{ result.count }}</p>
                <div v-if="result.sample_data && result.sample_data.length > 0" class="sample-data">
                  <strong>Sample data:</strong>
                  <div v-for="(sample, index) in result.sample_data" :key="index" class="sample-item">
                    <pre>{{ JSON.stringify(sample, null, 2) }}</pre>
                  </div>
                </div>
                <div v-if="result.error" class="error-message">
                  <strong>Error:</strong> {{ result.error }}
                </div>
                <div v-if="result.warning" class="warning-message">
                  <strong>Warning:</strong> {{ result.warning }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="selectorTestResults = {}" class="btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentTranslations } from '@/locales';
import Navigation from './Navigation.vue';

const router = useRouter();
const currentLanguage = ref('fr');
const saving = ref(false);
const message = ref('');
const messageType = ref('success');
const isMounted = ref(false);

// Selector discovery state
const showSelectorDiscovery = ref(false);
const discoveringSelectors = ref(false);
const testingSelectors = ref(false);
const discoveredSelectors = ref({
  product_links: [],
  product_name: [],
  product_price: [],
  product_image: [],
  product_reference: []
});
const selectorTestResults = ref({});

// Advanced discovery state (like TextSearch.vue)
const discoveryUrl = ref('');
const isAnalyzing = ref(false);
const analysisResults = ref(null);
const displayConfidenceScore = ref(0);


const activeSection = ref('sites');
const sidebarCollapsed = ref(false);
const isEditMode = ref(false);
const editingSiteId = ref(null);

// Settings data
const settings = ref({
  autoScraping: true,
  notifications: true,
  scrapingInterval: 60
});

// Image search pipeline settings (persisted in localStorage)
const DEFAULT_IMAGE_SETTINGS = {
  similarityThreshold: 0.88,
  brandFilter: true,
  maxResults: 20,
  cacheEnabled: true,
  filterInStock: false,
};

const imageSearchSettings = ref({ ...DEFAULT_IMAGE_SETTINGS });

const loadImageSearchSettings = () => {
  try {
    const saved = JSON.parse(localStorage.getItem('image_search_settings') || 'null');
    if (saved) imageSearchSettings.value = { ...DEFAULT_IMAGE_SETTINGS, ...saved };
  } catch (_) {}
};

const saveImageSearchSettings = () => {
  try {
    localStorage.setItem('image_search_settings', JSON.stringify(imageSearchSettings.value));
    showMessage('Paramètres de recherche image sauvegardés.', 'success');
  } catch (e) {
    showMessage('Impossible de sauvegarder les paramètres.', 'error');
  }
};

const clearImageCache = () => {
  try {
    let keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      let key = localStorage.key(i);
      if (key && key.startsWith('image_search_') && key !== 'image_search_settings') {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
    showMessage(`Le cache (${keysToRemove.length} éléments) a été vidé avec succès.`, 'success');
  } catch (e) {
    showMessage('Erreur lors du vidage du cache.', 'error');
  }
};

// New site form data
const newSite = ref({
  site_name: '',
  search_url: '',
  selectors: {
    product_links: '',
    product_name: '',
    product_price: '',
    product_image: '',
    product_reference: ''
  }
});

// Existing sites (this would come from backend)
const existingSites = ref([]);

// Translation computed property
const t = computed(() => {
  return getCurrentTranslations(currentLanguage.value);
});

const handleLanguageChange = (lang) => {
  currentLanguage.value = lang;
};

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value.toString());
};

const goToProfile = () => {
  // Navigate to profile page
  router.push('/profile');
};

const goToAdminPanel = () => {
  // Navigate to admin panel (current page)
  router.push('/admin');
};

const goToBarcodeSearch = () => {
  // Navigate to barcode search page
  router.push('/barcode-search');
};

const goToHome = () => {
  // Navigate to home page
  router.push('/home');
};

const signOut = () => {
  // Handle sign out logic
  if (confirm(t.value.confirmSignOut)) {
    // Clear user session, redirect to login, etc.
    router.push('/login');
  }
};

// Fetch sites from database
const fetchSites = async () => {
  try {
    console.log('Fetching sites...');
    const response = await fetch('http://localhost:8000/api/sites');
    const data = await response.json();
    
    if (data.success) {
      existingSites.value = data.sites;
      console.log('Sites fetched successfully:', data.sites.length);
    } else {
      console.error('Error fetching sites:', data.message);
      showMessage('Error fetching sites: ' + data.message, 'error');
    }
  } catch (error) {
    console.error('Error fetching sites:', error);
    if (error.name !== 'TypeError' || !error.message.includes('fetch')) {
      showMessage('Error fetching sites: ' + error.message, 'error');
    }
  }
};

const addNewSite = async () => {
  saving.value = true;
  message.value = '';
  
  try {
    const response = await fetch('http://localhost:8000/api/sites', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newSite.value)
    });
    
    const data = await response.json();
    
    if (data.success) {
      showMessage(t.value.siteAddedSuccessfully, 'success');
      resetForm();
      await fetchSites(); // Refresh the sites list
    } else {
      showMessage('Error adding site: ' + data.message, 'error');
    }
  } catch (error) {
    showMessage('Error adding site: ' + error.message, 'error');
  } finally {
    saving.value = false;
  }
};

const editSite = (site) => {
  console.log('Edit site called:', site);
  console.log('Current isEditMode:', isEditMode.value);
  
  // Populate form with site data for editing
  newSite.value = { ...site };
  isEditMode.value = true;
  editingSiteId.value = site.id;
  
  console.log('After setting edit mode - isEditMode:', isEditMode.value);
  console.log('editingSiteId:', editingSiteId.value);
  console.log('newSite value:', newSite.value);
  
  showMessage(t.value.editModeEnabled, 'info');
};

const saveChanges = async () => {
  saving.value = true;
  message.value = '';
  
  try {
    const response = await fetch(`http://localhost:8000/api/sites/${editingSiteId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newSite.value)
    });
    
    const data = await response.json();
    
    if (data.success) {
      showMessage(t.value.siteUpdatedSuccessfully, 'success');
      resetForm();
      await fetchSites(); // Refresh the sites list
    } else {
      showMessage('Error updating site: ' + data.message, 'error');
    }
  } catch (error) {
    showMessage('Error updating site: ' + error.message, 'error');
  } finally {
    saving.value = false;
  }
};

const deleteSite = async (siteId) => {
  if (confirm(t.value.confirmDeleteSite)) {
    try {
      const response = await fetch(`http://localhost:8000/api/sites/${siteId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage(t.value.siteDeletedSuccessfully, 'success');
        await fetchSites(); // Refresh the sites list
      } else {
        showMessage('Error deleting site: ' + data.message, 'error');
      }
    } catch (error) {
      showMessage('Error deleting site: ' + error.message, 'error');
    }
  }
};

const toggleSiteStatus = async (siteId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/sites/${siteId}/toggle`, {
      method: 'PUT'
    });
    
    const data = await response.json();
    
    if (data.success) {
      showMessage('Site status updated successfully', 'success');
      await fetchSites(); // Refresh the sites list
    } else {
      showMessage('Error updating site status: ' + data.message, 'error');
    }
  } catch (error) {
    showMessage('Error updating site status: ' + error.message, 'error');
  }
};

const resetForm = () => {
  newSite.value = {
    site_name: '',
    search_url: '',
    selectors: {
      product_links: '',
      product_name: '',
      product_price: '',
      product_image: '',
      product_reference: ''
    }
  };
  isEditMode.value = false;
  editingSiteId.value = null;
};

// Selector discovery methods
const discoverSelectors = async () => {
  if (!newSite.value.search_url) {
    showMessage('Please enter a website URL first', 'error');
    return;
  }
  
  // Set the discovery URL and show the modal
  discoveryUrl.value = newSite.value.search_url;
  showSelectorDiscovery.value = true;
};

// Advanced discovery method (like TextSearch.vue)
const analyzeWebsiteForSelectors = async () => {
  if (!discoveryUrl.value) {
    showMessage('Please enter a website URL first', 'error');
    return;
  }
  
  isAnalyzing.value = true;
  message.value = '';
  
  try {
    const response = await fetch('http://localhost:8000/api/analyze-website', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: discoveryUrl.value,
        selectors: {} // Empty selectors object as required by the API
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      analysisResults.value = data;
      displayConfidenceScore.value = data.analysis?.confidence_score || 0;
      
      // Populate discoveredSelectors with the analysis results
      if (data.discovered_selectors) {
        discoveredSelectors.value = {
          product_links: data.discovered_selectors.product_links || [],
          product_name: data.discovered_selectors.product_name || [],
          product_price: data.discovered_selectors.product_price || [],
          product_image: data.discovered_selectors.product_image || [],
          product_reference: data.discovered_selectors.product_reference || []
        };
      }
      
      showMessage(`Analysis completed with ${displayConfidenceScore.value}% confidence`, 'success');
      
      // Debug: Log sample products data
      console.log('Sample products data:', data.sample_products);
      if (data.sample_products && data.sample_products.length > 0) {
        data.sample_products.forEach((product, index) => {
          console.log(`Product ${index + 1}:`, {
            name: product.name || product.title,
            image_url: product.image_url,
            image: product.image,
            photo: product.photo,
            hasImage: !!(product.image_url || product.image || product.photo)
          });
        });
      }
    } else {
      showMessage('Error analyzing website: ' + data.message, 'error');
    }
  } catch (error) {
    console.error('Analysis error:', error);
    showMessage('Error analyzing website: ' + error.message, 'error');
  } finally {
    isAnalyzing.value = false;
  }
};

const testCurrentSelectors = async () => {
  if (!newSite.value.search_url) {
    showMessage('Please enter a website URL first', 'error');
    return;
  }
  
  testingSelectors.value = true;
  message.value = '';
  
  try {
    const response = await fetch('http://localhost:8000/api/sites/test-selectors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: newSite.value.search_url,
        selectors: newSite.value.selectors
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      selectorTestResults.value = data.test_results;
      showMessage(`Test completed: ${data.total_successful} selectors working`, 'success');
    } else {
      showMessage('Error testing selectors: ' + data.message, 'error');
    }
  } catch (error) {
    showMessage('Error testing selectors: ' + error.message, 'error');
  } finally {
    testingSelectors.value = false;
  }
};

const applyDetectedSelectors = () => {
  if (!analysisResults.value || !analysisResults.value.detected_selectors) {
    showMessage('Aucun sélecteur à appliquer', 'error');
    return;
  }

  // Map the detected selectors to the admin panel format
  const detected = analysisResults.value.detected_selectors;
  newSite.value.selectors = {
    product_links: detected.productContainer || detected.product_links || '',
    product_name: detected.name || detected.product_name || '',
    product_price: detected.price || detected.product_price || '',
    product_image: detected.image || detected.product_image || '',
    product_reference: detected.link || detected.product_reference || ''
  };
  
  showSelectorDiscovery.value = false;
  showMessage('Sélecteurs appliqués avec succès', 'success');
};

const applyDiscoveredSelector = (selectorType, selector) => {
  newSite.value.selectors[selectorType] = selector;
  showMessage(`Applied selector: ${selector}`, 'success');
};

const closeSelectorDiscovery = () => {
  showSelectorDiscovery.value = false;
  discoveredSelectors.value = {
    product_links: [],
    product_name: [],
    product_price: [],
    product_image: [],
    product_reference: []
  };
  analysisResults.value = null;
  discoveryUrl.value = '';
};

// Helper methods from TextSearch component
const getSelectorLabel = (key) => {
  switch (key) {
    case 'productContainer':
      return 'Conteneur de Produit';
    case 'product_links':
      return 'Liens de Produits';
    case 'name':
      return 'Nom du Produit';
    case 'product_name':
      return 'Nom du Produit';
    case 'price':
      return 'Prix';
    case 'product_price':
      return 'Prix';
    case 'image':
      return 'Image';
    case 'product_image':
      return 'Image';
    case 'link':
      return 'Lien';
    case 'product_reference':
      return 'Référence';
    default:
      return key;
  }
};

const getValidationClass = (key) => {
  if (!analysisResults.value || !analysisResults.value.detected_selectors) {
    return '';
  }
  const selector = analysisResults.value.detected_selectors[key];
  if (!selector) {
    return 'invalid';
  }
  return 'valid';
};

const getValidationStatus = (key) => {
  if (!analysisResults.value || !analysisResults.value.detected_selectors) {
    return 'Pas de validation';
  }
  const selector = analysisResults.value.detected_selectors[key];
  if (!selector) {
    return 'Sélecteur invalide';
  }
  return 'Sélecteur valide';
};

const getConfidenceClass = (score) => {
  if (score >= 80) {
    return 'high';
  } else if (score >= 50) {
    return 'medium';
  } else {
    return 'low';
  }
};

const isPlaceholderImage = (imageUrl) => {
  if (!imageUrl) return true;
  const placeholderPatterns = [
    'placeholder',
    'no-image',
    'default',
    'missing',
    'null',
    'undefined',
    'empty'
  ];
  return placeholderPatterns.some(pattern => 
    imageUrl.toLowerCase().includes(pattern)
  );
};

const showMessage = (msg, type = 'success') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 3000);
};

onMounted(async () => {
  console.log('AdminPanel component mounted');
  isMounted.value = true;
  loadImageSearchSettings();
  try {
    await nextTick();
    const savedSidebarState = localStorage.getItem('sidebarCollapsed');
    if (savedSidebarState) {
      sidebarCollapsed.value = savedSidebarState === 'true';
    }
    if (isMounted.value) {
      await fetchSites();
    }
  } catch (error) {
    console.error('Error in onMounted:', error);
    if (isMounted.value) {
      showMessage('Error initializing component: ' + error.message, 'error');
    }
  }
});

onUnmounted(() => {
  console.log('AdminPanel component unmounted');
  isMounted.value = false;
});
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
}

.admin-container {
  display: flex;
  min-height: calc(100vh - 50px);
  margin-top: 50px;
}

/* Sidebar Styles - Updated to match BarcodeSearch design */
.sidebar {
  width: 280px;
  background: #1A2E26 !important;
  border-right: 1px solid rgba(26,127,90,0.3);
  padding: 1.5rem;
  box-shadow: 2px 0 12px rgba(26,46,38,0.15);
  position: fixed;
  top: 50px;
  left: 0;
  height: calc(100vh - 50px);
  overflow-y: auto;
  z-index: 50;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 70px;
  padding: 1rem 0.5rem;
}

.sidebar-header {
  margin-bottom: 2rem;
  margin-top: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
}

.sidebar-collapsed .header-content {
  align-items: center;
}

.sidebar-header h3 {
  color: #E8F7F2 !important;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.back-arrow-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-bottom: 0.5rem;
}

.back-arrow-btn:hover {
  background: #1d4ed8;
  transform: scale(1.05);
}

.back-arrow-btn svg {
  width: 20px;
  height: 20px;
}

.admin-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  padding: 0 0.5rem;
}

.menu-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
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
  position: relative;
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

.menu-item.sign-out {
  color: #ef4444;
}

.menu-item.sign-out:hover {
  background: #fef2f2;
  color: #dc2626;
}

.menu-item.forward-button {
  color: #3b82f6;
}

.menu-item.forward-button:hover {
  background: #eff6ff;
  color: #1d4ed8;
}

.menu-separator {
  height: 1px;
  background-color: #e2e8f0;
  margin: 1rem 0;
  width: 100%;
  list-style: none;
}

.menu-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.menu-item span {
  font-size: 0.9rem;
  white-space: nowrap;
}

.menu-tooltip {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  color: #2d3748;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  z-index: 1000;
  margin-left: 0.5rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.menu-item:hover .menu-tooltip {
  opacity: 1;
}

.menu-tooltip::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
  border-right: 4px solid white;
}

.sidebar-toggle {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  border: none;
  background: #f7fafc;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4a5568;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.sidebar-toggle:hover {
  background: #e2e8f0;
  transform: scale(1.05);
}

.sidebar-toggle svg {
  width: 18px;
  height: 18px;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  margin-left: 280px;
  padding: 1.5rem 2rem;
  background: white;
  transition: margin-left 0.3s ease;
  margin-top: 0;
}

.main-content-expanded {
  margin-left: 70px;
}

.content-header {
  margin-bottom: 1.5rem;
  margin-top: 0;
}

.content-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.content-header p {
  color: #4a5568;
  font-size: 1rem;
  line-height: 1.6;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Card Styles */
.form-card,
.sites-card,
.settings-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  background: white;
}

.card-header h3 {
  color: #2d3748;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.edit-mode-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fef3c7;
  color: #92400e;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-top: 0.75rem;
}

.edit-mode-indicator svg {
  width: 16px;
  height: 16px;
}

.card-header p {
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Form Styles */
.site-form {
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-size: 1rem;
}

.form-group input,
.form-select {
  display: block;
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s;
  background: white;
  color: #2d3748;
}

.form-group input:focus,
.form-select:focus {
  border-color: #1A7F5A;
  box-shadow: 0 0 0 3px rgba(26,127,90,0.15);
  outline: none;
}

.form-group input::placeholder {
  color: #718096;
  opacity: 0.6;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  min-width: 120px;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
  color: white;
  box-shadow: 0 4px 6px rgba(26,127,90,0.25);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(26,127,90,0.35);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  background: #f8fafc;
  color: #475569;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Edit and Delete Button Styles */
.btn-edit,
.btn-delete {
  padding: 0.5rem;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-edit {
  background: #f59e0b;
  color: white;
}

.btn-edit:hover {
  background: #d97706;
  transform: translateY(-1px);
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.btn-edit svg,
.btn-delete svg {
  width: 18px;
  height: 18px;
}

/* Selector Discovery Buttons */
.btn-discover,
.btn-test {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-discover {
  background: #8b5cf6;
  color: white;
}

.btn-discover:hover:not(:disabled) {
  background: #7c3aed;
  transform: translateY(-1px);
}

.btn-test {
  background: #06b6d4;
  color: white;
}

.btn-test:hover:not(:disabled) {
  background: #0891b2;
  transform: translateY(-1px);
}

.btn-discover:disabled,
.btn-test:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-with-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.input-with-buttons input {
  flex: 1;
}

.input-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Sites List Styles */
.sites-list {
  padding: 2rem;
}

.site-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.site-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.site-info {
  flex: 1;
}

.site-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.site-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.site-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.2s ease;
}

.site-status:hover {
  transform: scale(1.05);
}

.site-status.active {
  background: #10b981;
  color: white;
}

.site-status:not(.active) {
  background: #6b7280;
  color: white;
}

.site-url {
  color: #4a5568;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  word-break: break-all;
}

.site-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #718096;
  opacity: 0.7;
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.site-actions {
  display: flex;
  gap: 0.5rem;
}

/* Settings Styles */
.settings-form {
  padding: 2rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.setting-info p {
  font-size: 0.9rem;
  color: #4a5568;
  opacity: 0.7;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.modal-close:hover {
  background: #f7fafc;
}

.modal-close svg {
  width: 24px;
  height: 24px;
  color: #4a5568;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  gap: 0.75rem;
}

/* Discovery Form Styles */
.discovery-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.discovery-form .form-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.discovery-form .form-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  min-width: 120px;
}

.url-input-group {
  display: flex;
  gap: 0.5rem;
  flex: 1;
}

.url-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.url-input:focus {
  outline: none;
  border-color: #667eea;
}

.analyze-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.analyze-btn:hover:not(:disabled) {
  background: #0056b3;
}

.analyze-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Analysis Results Styles */
.analysis-results {
  background: #f8f9fa;
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e1e5e9;
}

.analysis-header h3 {
  color: #333;
  font-size: 1.1rem;
  margin: 0;
}

.confidence-score {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.score-label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.score-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #28a745; /* Green for high confidence */
}

.score-value.medium {
  color: #ffc107; /* Yellow for medium confidence */
}

.score-value.low {
  color: #dc3545; /* Red for low confidence */
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.analysis-card {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.analysis-card.full-width {
  grid-column: 1 / -1;
}

.analysis-card h4 {
  color: #333;
  font-size: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e1e5e9;
}

.selectors-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.selector-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.selector-item:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.selector-label {
  font-weight: 600;
  color: #4a5568;
  min-width: 120px;
  font-size: 0.9rem;
}

.selector-value {
  flex: 1;
  background: #1a202c;
  color: #e2e8f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  word-break: break-all;
}

.validation-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.validation-status.valid {
  background: #d4edda;
  color: #155724;
}

.validation-status.invalid {
  background: #f8d7da;
  color: #721c24;
}

/* Sample Products Styles */
.sample-products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.sample-product {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.sample-product:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.sample-product-image {
  width: 100%;
  height: 120px;
  margin-bottom: 0.75rem;
  border-radius: 6px;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sample-product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #6c757d;
  font-size: 0.875rem;
  text-align: center;
}

.sample-product-info h5 {
  color: #333;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;  /* ✅ Added standard property */
  -webkit-box-orient: vertical;
  overflow: hidden;
}


.sample-price {
  color: #28a745;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.view-link {
  color: #007bff;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
}

.view-link:hover {
  text-decoration: underline;
}

/* Discovery Actions */
.discovery-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e1e5e9;
}

.apply-btn,
.close-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.apply-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.apply-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a67d8 0%, #9f7aea 100%);
}

.close-btn {
  background: #dc3545;
  color: white;
}

.close-btn:hover:not(:disabled) {
  background: #c82333;
}

/* Test Results Styles */
.test-results {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.test-result {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.result-header h4 {
  color: #2d3748;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.result-status.success {
  color: #48bb78;
  font-weight: 600;
}

.result-status.error {
  color: #f56565;
  font-weight: 600;
}

.result-details {
  color: #4a5568;
}

.sample-data {
  margin-top: 1rem;
}

.sample-item {
  margin-top: 0.5rem;
}

.sample-item pre {
  background: #1a202c;
  color: #e2e8f0;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  overflow-x: auto;
  margin: 0;
}

.error-message, .warning-message {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.error-message {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.warning-message {
  background: #fef5e7;
  color: #b7791f;
  border: 1px solid #fbd38d;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-border);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #667eea;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* Message Styles */
.message {
  position: fixed;
  top: 90px;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 400px;
}

.message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.message.success {
  background: #10b981;
}

.message.error {
  background: #ef4444;
}

.message.info {
  background: #3b82f6;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Loading Spinner */
.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .sidebar-collapsed {
    width: 60px;
  }
  
  .main-content {
    margin-left: 240px;
  }
  
  .main-content-expanded {
    margin-left: 60px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }
  
  .sidebar {
    position: static;
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  
  .main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .site-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .site-actions {
    align-self: flex-end;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

/* Dark Mode Enhancements */
:global(.dark-mode) .admin-layout {
  background: #181a1b;
  color: #f1f1f1;
}

:global(.dark-mode) .sidebar {
  background: #232526;
  border-right-color: #333;
}

:global(.dark-mode) .sidebar-header {
  background: #232526;
  border-bottom-color: #333;
}

:global(.dark-mode) .sidebar-header h3 {
  color: #f1f1f1;
}

:global(.dark-mode) .back-arrow-btn {
  background: #60a5fa;
}

:global(.dark-mode) .back-arrow-btn:hover {
  background: #3b82f6;
}

:global(.dark-mode) .menu-section h4 {
  color: #a0aec0;
}

:global(.dark-mode) .menu-item {
  color: #a0aec0;
}

:global(.dark-mode) .menu-item:hover {
  background: #2d3748;
  color: #f1f1f1;
}

:global(.dark-mode) .menu-item.sign-out:hover {
  background: #2d1b1b;
  color: #fca5a5;
}

:global(.dark-mode) .menu-item.forward-button {
  color: #60a5fa;
}

:global(.dark-mode) .menu-item.forward-button:hover {
  background: #1e3a8a;
  color: #93c5fd;
}

:global(.dark-mode) .sidebar-toggle {
  background: #2d3748;
  color: #a0aec0;
}

:global(.dark-mode) .sidebar-toggle:hover {
  background: #4a5568;
}

:global(.dark-mode) .main-content {
  background: #181a1b;
}

:global(.dark-mode) .form-card,
:global(.dark-mode) .sites-card,
:global(.dark-mode) .settings-card {
  background: #232526;
  border-color: #333;
}

:global(.dark-mode) .card-header {
  background: #232526;
  border-bottom-color: #333;
}

:global(.dark-mode) .site-item {
  background: #232526;
  border-color: #333;
}

:global(.dark-mode) .form-group input,
:global(.dark-mode) .form-select {
  background: #232526;
  border-color: #444;
  color: #f1f1f1;
}

:global(.dark-mode) .form-group input:focus,
:global(.dark-mode) .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

:global(.dark-mode) .btn-secondary {
  background: #333;
  border-color: #444;
  color: #f1f1f1;
}

:global(.dark-mode) .btn-secondary:hover {
  background: #444;
}

:global(.dark-mode) .toggle-slider {
  background-color: #444;
}

:global(.dark-mode) .toggle-slider:before {
  background-color: #f1f1f1;
}

:global(.dark-mode) .menu-tooltip {
  background: #2d3748;
  color: #f1f1f1;
}

:global(.dark-mode) .menu-tooltip::before {
  border-right-color: #2d3748;
}



/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: #4a5568;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  opacity: 0.3;
  margin-bottom: 1rem;
}

.empty-state h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.empty-state p {
  font-size: 0.9rem;
  opacity: 0.7;
  color: #718096;
}

/* Settings Styles */
</style>