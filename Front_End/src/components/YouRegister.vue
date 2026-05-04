<template>
  <div class="login-container">
    <!-- Background with soft gradient -->
    <div class="login-background">
      <div class="background-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- Main login content -->
    <div class="login-content">
      <!-- Top section - Illustration -->
      <div class="illustration-section">
        <!-- Header with logo and login text -->
        <div class="illustration-header">
          <div class="logo">{{ t.seoTools }}</div>
          <div class="language-selector">
            <button @click="toggleLanguageDropdown" class="language-btn">
              <img src="@/assets/translate.png" alt="Translate" class="language-img" />
            </button>
            <div v-if="showLanguageDropdown" class="language-dropdown">
              <div @click="selectLanguage('en')" class="language-option">
                <span class="flag">🇺🇸</span>
                <span>{{ t.english }}</span>
              </div>
              <div @click="selectLanguage('fr')" class="language-option">
                <span class="flag">🇫🇷</span>
                <span>{{ t.francais }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="illustration-container">
          <!-- User Avatar -->
          <div class="user-avatar">
            <img src="@/assets/1x/Asset 1.png" alt="User Avatar" class="avatar-image" />
          </div>
        </div>

        <div class="illustration-text">
          <h1>{{ t.welcomeToSeoTools }}</h1>
          <p>{{ t.createAccountSecurely }}</p>
        </div>
      </div>

      <!-- Bottom section - Login form -->
      <div class="login-form-section">
        <div class="login-card">
          
          <form @submit.prevent="submitForm" class="login-form">
            <div class="form-group">
              <label for="email">{{ t.emailAddress }}</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M20 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" fill="currentColor"/>
                  </svg>
                </div>
                <input
                  id="email"
            v-model="email"
                  type="email"
                  :placeholder="t.emailPlaceholder"
            required
                  class="form-input"
                  :class="{ 'error': registerError }"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="password">{{ t.password }}</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15C14 16.1 13.1 17 12 17ZM15.1 8H8.9V6C8.9 4.29 10.29 2.9 12 2.9C13.71 2.9 15.1 4.29 15.1 6V8Z" fill="currentColor"/>
                  </svg>
                </div>
                <input
                  id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
                  :placeholder="t.passwordPlaceholder"
            required
                  class="form-input"
                  :class="{ 'error': registerError }"
                />
                <button
                  type="button"
                  @click="togglePasswordVisibility"
                  class="password-toggle"
                >
                  <svg v-if="showPassword" viewBox="0 0 24 24" fill="none">
                    <path d="M12 7C14.76 7 17 9.24 17 12C17 12.65 16.87 13.26 16.64 13.83L19.56 16.75C21.07 15.49 22.26 13.86 22.99 12C21.26 7.61 16.99 4.5 12 4.5C10.59 4.5 9.25 4.75 8 5.2L10.17 7.37C10.74 7.13 11.35 7 12 7ZM2 4.27L3.28 3L20.72 20.44L19.44 21.72L17.46 19.74C15.87 20.52 13.98 21 12 21C7.01 21 2.74 17.89 1.01 13.5C1.99 11.17 3.35 9.15 5.07 7.53L2 4.27ZM7.53 9.8C7.37 10.21 7.27 10.65 7.27 11.12C7.27 13.1 8.9 14.73 10.88 14.73C11.35 14.73 11.79 14.63 12.2 14.47L7.53 9.8ZM12 17C9.24 17 7 14.76 7 12C7 11.12 7.27 10.29 7.75 9.57L9.32 11.14C9.11 11.7 9 12.34 9 13C9 15.21 10.79 17 13 17C13.66 17 14.3 16.89 14.86 16.68L16.43 18.25C15.71 18.73 14.88 19 14 19H12Z" fill="currentColor"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="currentColor"/>
                  </svg>
                </button>
              </div>
            </div>

            <button
              type="submit"
              :disabled="!valid || loading"
              class="login-button"
              :class="{ 'loading': loading }"
            >
              <span v-if="!loading">{{ t.createAccount }}</span>
              <div v-else class="loading-spinner"></div>
            </button>
          </form>

                      <div class="login-footer">
              <p>{{ t.alreadyHaveAccount }} 
                <router-link :to="{ name: 'login' }" class="register-link" @click="goToLogin">{{ t.signIn }}</router-link>
              </p>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { getCurrentTranslations } from '@/locales';

const router = useRouter();
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const registerError = ref(false);
const loading = ref(false);
const showLanguageDropdown = ref(false);
const currentLanguage = ref('fr');

// Translation computed property
const t = computed(() => {
  return getCurrentTranslations(currentLanguage.value);
});

const valid = computed(() => {
  return email.value && password.value && email.value.includes('@') && password.value.length >= 6;
});

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

const toggleLanguageDropdown = () => {
  showLanguageDropdown.value = !showLanguageDropdown.value;
};

const selectLanguage = (lang) => {
  currentLanguage.value = lang;
  showLanguageDropdown.value = false;
};

const goToLogin = () => {
  router.push({ name: 'login' });
};

const submitForm = async () => {
  if (!valid.value) return;
  
  loading.value = true;
  registerError.value = false;
  
  try {
    const response = await axios.post('http://127.0.0.1:8000/signup', {
      username: email.value,
      password: password.value,
    });

    console.log(response.data);
    // Automatically log the user in after successful registration
    const loginResponse = await axios.post('http://127.0.0.1:8000/login', {
      username: email.value,
      password: password.value,
    });
    if (loginResponse.status === 200) {
      localStorage.setItem('authToken', loginResponse.data.access_token);
      router.push({ name: 'home' });
    }
  } catch (error) {
    if (error.response) {
      console.error(t.value.registrationError, error.response.data.detail);
      registerError.value = true;
    } else {
      console.error(t.value.registrationErrorDetail);
      registerError.value = true;
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.background-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  animation: float 8s ease-in-out infinite;
  filter: blur(1px);
}

.shape-1 {
  width: 250px;
  height: 250px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  top: 8%;
  left: 8%;
  animation-delay: 0s;
}

.shape-2 {
  width: 180px;
  height: 180px;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  top: 65%;
  right: 12%;
  animation-delay: 2s;
}

.shape-3 {
  width: 120px;
  height: 120px;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  bottom: 15%;
  left: 15%;
  animation-delay: 4s;
}

.shape-4 {
  width: 150px;
  height: 150px;
  background: linear-gradient(45deg, #a8edea, #fed6e3);
  top: 35%;
  right: 25%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
  50% { transform: translateY(-25px) rotate(180deg) scale(1.05); }
}

.login-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 650px;
  background: white;
  border-radius: 28px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  margin: 2rem;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.illustration-section {
  background: rgba(255, 255, 255, 0.3);
  color: #333;
  padding: 0.25rem 2rem;
  position: relative;
  z-index: 1;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.illustration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 3rem;
  margin-top: 0.5rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: #667eea;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
}

.language-selector {
  position: relative;
}

.language-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.language-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.language-icon {
  width: 20px;
  height: 20px;
  color: white;
}

.language-dropdown {
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
  min-width: 140px;
}

.language-option {
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

.language-option:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.language-option:first-child {
  border-bottom: 1px solid #e2e8f0;
}

.flag {
  font-size: 1.2rem;
}

.login-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #4a5568;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.illustration-container {
  position: relative;
  width: 350px;
  height: 80px;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

/* User Avatar */
.user-avatar {
  position: relative;
  width: 250px;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: -7rem auto 0.1rem;
  margin-left: calc(50% + 45px);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.illustration-text {
  text-align: center;
  position: relative;
  z-index: 1;
}

.illustration-text h1 {
  font-size: 1.2rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
  color: #1a202c;
  letter-spacing: -0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.illustration-text p {
  font-size: 0.9rem;
  opacity: 0.85;
  color: #4a5568;
  font-weight: 500;
  line-height: 1.3;
}

.login-form-section {
  background: white;
  padding: 0.5rem 2rem;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.login-card {
  width: 100%;
}

.login-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-header h2 {
  font-size: 1.4rem;
  font-weight: 800;
  color: #1a202c;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.login-header p {
  color: #718096;
  font-size: 0.9rem;
  font-weight: 500;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
  color: #c53030;
  padding: 1rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  border: 1px solid #feb2b2;
  box-shadow: 0 2px 8px rgba(197, 48, 48, 0.1);
}

.error-icon {
  width: 20px;
  height: 20px;
  color: #c53030;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group label {
  font-weight: 700;
  color: #2d3748;
  font-size: 0.9rem;
  letter-spacing: -0.2px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
  z-index: 1;
}

.input-icon svg {
  width: 18px;
  height: 18px;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.form-input.error {
  border-color: #e53e3e;
  box-shadow: 0 0 0 4px rgba(229, 62, 62, 0.1);
}

.form-input::placeholder {
  color: #a0aec0;
  font-weight: 400;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  color: #718096;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.password-toggle:hover {
  color: #4a5568;
  background: rgba(113, 128, 150, 0.1);
}

.password-toggle svg {
  width: 20px;
  height: 20px;
}

.remember-me {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
  user-select: none;
  position: relative;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  height: 18px;
  width: 18px;
  background-color: white;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  margin-right: 0.75rem;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-label:hover .checkmark {
  border-color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
}

.checkbox-input:checked ~ .checkmark {
  background-color: #667eea;
  border-color: #667eea;
}

.checkmark:after {
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

.checkbox-input:checked ~ .checkmark:after {
  display: block;
}

.login-button {
  width: 100%;
  padding: 0.6rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  letter-spacing: -0.2px;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.login-button.loading {
  cursor: wait;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.login-footer p {
  color: #718096;
  font-size: 0.9rem;
  font-weight: 500;
  margin-top: -1rem;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.3s ease;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  margin-left: 0.25rem;
}

.register-link:hover {
  color: #764ba2;
  background: rgba(102, 126, 234, 0.1);
  text-decoration: none; 
}

.language-img {
  width: 20px !important;
  height: 20px !important;
  object-fit: contain;
  display: block;
  filter: brightness(0) invert(1) drop-shadow(0 2px 4px rgba(102,126,234,0.15));
  margin: 0 auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-content {
    margin: 1rem;
    border-radius: 20px;
  }

  .illustration-section {
    padding: 1.5rem 2rem 1rem;
  }

  .illustration-container {
    width: 180px;
    height: 120px;
  }

  .illustration-text h1 {
    font-size: 1.2rem;
  }

  .login-form-section {
    padding: 1.5rem 2rem;
  }

  .login-header h2 {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .illustration-section {
    padding: 1rem 1.5rem 0.75rem;
  }

  .login-form-section {
    padding: 1.25rem 1.5rem;
  }

  .illustration-text h1 {
    font-size: 1.1rem;
  }

  .login-header h2 {
    font-size: 1.1rem;
  }

  .illustration-container {
    width: 160px;
    height: 100px;
  }
}
</style>
