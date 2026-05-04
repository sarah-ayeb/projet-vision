<template>
  <nav class="navbar">
         <div class="navbar-brand">
       <slot name="logo">
         <img src="@/assets/1x/barcode.png" alt="Barcode Logo" class="logo-barcode-icon" />
       </slot>
       <span class="brand-text">{{ t.seoTools }}</span>
     </div>
    
    <div class="navbar-actions">
      <!-- Dark Mode Switcher -->
      <div class="action-item">
        <button @click="toggleDarkMode" class="darkmode-switcher-circle" :class="{ night: isDarkMode }" :aria-label="isDarkMode ? 'Switch to day mode' : 'Switch to night mode'">
          <span class="switch-track-circle">
            <span class="switch-thumb-circle" :class="{ right: isDarkMode }">
              <img :src="isDarkMode ? moonIcon : sunIcon" class="switch-icon-img" alt="mode icon" />
            </span>
          </span>
        </button>
      </div>
      <!-- Translation Toggle -->
      <div class="action-item">
        <button @click="toggleLanguageDropdown" class="action-btn language-btn">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12.87 15.07L10.33 12.56L10.36 12.53C12.1 10.59 13.34 8.36 14.07 6H17V4H10V2H8V4H1V6H12.17C11.5 7.92 10.44 9.75 9 11.35C8.07 10.32 7.3 9.19 6.69 8H4.69C5.42 9.63 6.42 11.17 7.67 12.56L2.58 17.58L4 19L9 14L12.11 17.11L12.87 15.07ZM18.5 10H16.5L12 22H14L15.12 19H19.87L21 22H23L18.5 10ZM15.88 17L17.5 12.67L19.12 17H15.88Z" fill="currentColor"/>
          </svg>
        </button>
        <div v-if="showLanguageDropdown" class="dropdown language-dropdown">
          <div @click="selectLanguage('en')" class="dropdown-item">
            <span class="flag">🇺🇸</span>
            <span>{{ t.english }}</span>
          </div>
          <div @click="selectLanguage('fr')" class="dropdown-item">
            <span class="flag">🇫🇷</span>
            <span>{{ t.francais }}</span>
          </div>
        </div>
      </div>
      <!-- Conditional Navigation: House Button for Admin Panel, User Icon for Others -->
      <div class="action-item" v-if="$route.path === '/admin'">
        <button @click="goToBarcodeSearch" class="action-btn home-btn" :title="t.barcodeSearch">
          <svg viewBox="0 0 24 24" fill="none" class="home-icon-img">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="currentColor"/>
          </svg>
        </button>
      </div>
      
      <!-- Profile Toggle for Other Pages -->
      <div class="action-item" v-else>
        <button @click="toggleProfileDropdown" class="action-btn profile-btn">
          <img :src="userIcon" class="profile-icon-img" alt="profile icon" />
        </button>
        <div v-if="showProfileDropdown" class="dropdown profile-dropdown">
          <div @click="goToProfile" class="dropdown-item">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
            </svg>
            <span>{{ t.profile }}</span>
          </div>
          <div @click="goToAdminPanel" class="dropdown-item">
            <svg viewBox="0 0 24 24" fill="none" style="width: 20px; height: 20px;">
              <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" fill="currentColor"/>
            </svg>
            <span>{{ t.adminPanel }}</span>
          </div>
          <div class="dropdown-divider"></div>
          <div @click="signOut" class="dropdown-item sign-out">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M17 7L15.59 8.41L18.17 11H8V13H18.17L15.59 15.59L17 17L22 12L17 7ZM4 5H12V3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H12V19H4V5Z" fill="currentColor"/>
            </svg>
            <span>{{ t.signOut }}</span>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentTranslations } from '@/locales';
import moonIcon from '@/assets/1x/moon.png';
import sunIcon from '@/assets/1x/sun.png';
import userIcon from '@/assets/1x/user (1).png';

const router = useRouter();
const showLanguageDropdown = ref(false);
const showProfileDropdown = ref(false);
const currentLanguage = ref('fr');
const isDarkMode = ref(false);

// Define emit
const emit = defineEmits(['language-changed']);

// Translation computed property
const t = computed(() => {
  return getCurrentTranslations(currentLanguage.value);
});

const toggleLanguageDropdown = () => {
  showLanguageDropdown.value = !showLanguageDropdown.value;
  showProfileDropdown.value = false; // Close other dropdown
};

const toggleProfileDropdown = () => {
  showProfileDropdown.value = !showProfileDropdown.value;
  showLanguageDropdown.value = false; // Close other dropdown
};

const selectLanguage = (lang) => {
  currentLanguage.value = lang;
  showLanguageDropdown.value = false;
  // Emit event to parent component to update language
  emit('language-changed', lang);
};

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark-mode');
    localStorage.setItem('nightMode', 'true');
  } else {
    document.documentElement.classList.remove('dark-mode');
    localStorage.setItem('nightMode', 'false');
  }
};

// Define closeDropdowns at top level so it is in scope for both add/remove
const closeDropdowns = (e) => {
  if (!e.target.closest('.action-item')) {
    showLanguageDropdown.value = false;
    showProfileDropdown.value = false;
  }
};

onMounted(() => {
  // Restore dark mode from localStorage
  if (localStorage.getItem('nightMode') === 'true') {
    isDarkMode.value = true;
    document.documentElement.classList.add('dark-mode');
  }
  document.addEventListener('click', closeDropdowns);
});

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns);
});

const goToBarcodeSearch = () => {
  router.push('/barcode-search');
};

const goToProfile = () => {
  showProfileDropdown.value = false;
  // Navigate to profile page or show profile modal
  console.log('Navigate to profile');
};

const goToAdminPanel = () => {
  showProfileDropdown.value = false;
  // Navigate to admin panel page
  router.push('/admin');
};

const signOut = () => {
  showProfileDropdown.value = false;
  localStorage.removeItem('authToken');
  router.push('/login');
};
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 70px;
  background: linear-gradient(135deg, #1A7F5A 0%, #1A2E26 100%);
  border-bottom: 1px solid rgba(232, 247, 242, 0.15);
  box-shadow: 0 2px 8px rgba(26, 46, 38, 0.25);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.brand-icon {
  width: 40px;
  height: 40px;
  color: white;
}

 .brand-icon svg {
   width: 100%;
   height: 100%;
 }

 .logo-barcode-icon {
   width: 40px !important;
   height: 2rem !important;
   object-fit: fill;
   filter: brightness(0) invert(1);
   vertical-align: middle;
   margin-right: 10px;
 }

.brand-text {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  letter-spacing: -0.5px;
  text-transform: uppercase;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.action-item {
  position: relative;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.action-btn svg {
  width: 28px;
  height: 28px;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 1000;
  min-width: 160px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
}

.dropdown-item:hover {
  background: rgba(26, 127, 90, 0.1);
  color: #1A7F5A;
}

.dropdown-item svg {
  width: 16px;
  height: 16px;
}

.dropdown-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 0.25rem 0;
}

.sign-out {
  color: #e53e3e;
}

.sign-out:hover {
  background: rgba(229, 62, 62, 0.1);
  color: #e53e3e;
}

.flag {
  font-size: 1.2rem;
}

.darkmode-switcher,
.darkmode-switcher.night {
  display: none;
}
.darkmode-switcher-circle {
  width: 68px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 16px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}
.switch-track-circle {
  width: 68px;
  height: 32px;
  background: #e2e8f0;
  border-radius: 16px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  transition: background 0.2s;
}
.darkmode-switcher-circle.night .switch-track-circle {
  background: #333;
}
.switch-thumb-circle {
  width: 28px;
  height: 28px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  left: 2px;
  top: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  transition: left 0.22s cubic-bezier(.4,1.6,.6,1), background 0.2s;
}
.switch-thumb-circle.right {
  left: 38px;
  background: #ffd700;
}
.switch-icon-img {
  width: 18px;
  height: 18px;
  display: block;
}
.darkmode-switcher-circle.night .switch-thumb-circle {
  background: #ffd700;
}
.darkmode-switcher-circle.night .switch-icon-img {
  filter: brightness(1.8) invert(1);
}
.home-icon-img {
  width: 24px;
  height: 24px;
  color: white;
  display: block;
}

.profile-icon-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}
:global(.dark-mode) {
  background: #181a1b !important;
  color: #f1f1f1 !important;
}
:global(.dark-mode) .navbar {
  background: linear-gradient(135deg, #232526 0%, #414345 100%) !important;
  color: #f1f1f1 !important;
}
:global(.dark-mode) .dropdown {
  background: #232526 !important;
  color: #f1f1f1 !important;
  border-color: #333 !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.7) !important;
}
:global(.dark-mode) .dropdown-item {
  color: #f1f1f1 !important;
}
:global(.dark-mode) .dropdown-item:hover {
  background: #333 !important;
  color: #ffd700 !important;
}
:global(.dark-mode) .action-btn {
  color: #ffd700 !important;
}
:global(.dark-mode) .brand-text {
  color: #ffd700 !important;
}
</style> 