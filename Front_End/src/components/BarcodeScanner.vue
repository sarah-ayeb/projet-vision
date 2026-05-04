<template>
  <div class="barcode-scanner-container">
    <!-- Scanner Modal -->
    <div v-if="showScanner" class="scanner-modal">
      <div class="scanner-content">
        <div class="scanner-header">
          <h3>{{ t.barcodeScanner }}</h3>
          <button @click="closeScanner" class="close-btn">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        
        <div class="camera-selector">
          <label for="camera-select">{{ t.camera }}</label>
          <select id="camera-select" v-model="selectedCamera" @change="switchCamera">
            <option v-if="cameras.length === 0" value="">{{ t.noCameraDetected }}</option>
            <option v-for="camera in cameras" :key="camera.deviceId" :value="camera.deviceId">
              {{ camera.label || t.cameraLabel.replace('{id}', camera.deviceId.slice(0, 8)) }}
            </option>
          </select>
          <button v-if="cameras.length === 0" @click="refreshCameras" class="refresh-btn">
             {{ t.refreshCameras }}
          </button>
        </div>
        
        <div class="scanner-body">
          
          <!-- Video Container -->
          <div class="video-container">
            <video 
              ref="videoElement" 
              :class="{ 'scanning': isScanning }"
              autoplay 
              playsinline
            ></video>
            
            <!-- Scanning Overlay -->
            <div class="scanning-overlay">
              <div class="scanning-frame">
                <div class="corner top-left"></div>
                <div class="corner top-right"></div>
                <div class="corner bottom-left"></div>
                <div class="corner bottom-right"></div>
                <div class="scanning-line"></div>
              </div>
              <p class="scanning-text">{{ t.placeBarcodeInFrame }}</p>
            </div>
          </div>
          
          <!-- Status Messages -->
          <div class="scanner-status">
            <div v-if="isLoading" class="status-message loading">
              <div class="spinner"></div>
              <span>{{ t.initializingCamera }}</span>
            </div>
            <div v-else-if="error" class="status-message error">
              <span>⚠️ {{ error }}</span>
            </div>
            <div v-else-if="lastScannedCode" class="status-message success">
              <span>{{ t.codeDetected.replace('{code}', lastScannedCode) }}</span>
            </div>
            <div v-else class="status-message info">
              <span>{{ t.readyToScan }}</span>
            </div>
          </div>
          
          <!-- Manual Input Fallback -->
          <div class="manual-input">
            <p>{{ t.orEnterManually }}</p>
            <input 
              v-model="manualBarcode" 
              type="text" 
              :placeholder="t.barcodePlaceholder"
              maxlength="13"
              @keyup.enter="useManualBarcode"
            />
            <button @click="useManualBarcode" class="manual-btn">{{ t.use }}</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Scanner Button -->
    <button @click="openScanner" class="scanner-btn">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M3 7V5C3 3.9 3.9 3 5 3H7M7 21H5C3.9 21 3 20.1 3 19V17M21 7V5C21 3.9 20.1 3 19 3H17M17 21H19C20.1 21 21 20.1 21 19V17M7 12H17M12 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ t.scanWithCamera }}
    </button>
  </div>
</template>

<script>
import { BrowserMultiFormatReader } from '@zxing/library';
import { getCurrentTranslations } from '@/locales';

export default {
  name: 'BarcodeScanner',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      showScanner: false,
      isScanning: false,
      isLoading: false,
      error: '',
      lastScannedCode: '',
      manualBarcode: '',
      selectedCamera: '',
      cameras: [],
      codeReader: null,
      stream: null,
      isProcessingScan: false, // Flag to prevent multiple rapid scans
      currentLanguage: 'fr'
    };
  },
  computed: {
    t() {
      return getCurrentTranslations(this.currentLanguage);
    }
  },
  mounted() {
    this.initializeScanner();
  },
  beforeUnmount() {
    this.cleanup();
  },
  methods: {
    async initializeScanner() {
      try {
        this.codeReader = new BrowserMultiFormatReader();
        await this.getAvailableCameras();
      } catch (error) {
        console.error('Error initializing scanner:', error);
        this.error = this.t.scannerNotInitialized;
      }
    },
    
         async getAvailableCameras() {
       try {
         // First, request camera permission to get labeled devices
         await navigator.mediaDevices.getUserMedia({ video: true });
         
         const devices = await navigator.mediaDevices.enumerateDevices();
         this.cameras = devices.filter(device => device.kind === 'videoinput');
         
         console.log('Available cameras:', this.cameras);
         
         if (this.cameras.length > 0) {
           this.selectedCamera = this.cameras[0].deviceId;
         } else {
           this.error = this.t.noCameraDetected;
         }
       } catch (error) {
         console.error('Error getting cameras:', error);
         if (error.name === 'NotAllowedError') {
           this.error = this.t.cameraPermissionDenied;
         } else {
           this.error = this.t.cannotAccessCameras + error.message;
         }
       }
     },
    
         async openScanner() {
       this.showScanner = true;
       this.error = '';
       this.lastScannedCode = '';
       this.manualBarcode = '';
       this.isProcessingScan = false; // Reset processing flag
       
       // Wait for DOM to update
       await this.$nextTick();
       
       // Refresh camera list when opening scanner
       await this.getAvailableCameras();
       await this.startScanning();
     },
    
         async startScanning() {
       if (!this.codeReader) {
         this.error = this.t.scannerNotInitialized;
         return;
       }
       
       this.isLoading = true;
       this.error = '';
       
       try {
         // Start video stream with more flexible constraints
         const constraints = {
           video: {
             width: { ideal: 1280, min: 640 },
             height: { ideal: 720, min: 480 },
             facingMode: 'environment' // Prefer back camera on mobile
           }
         };
         
         // If specific camera is selected, use it
         if (this.selectedCamera) {
           constraints.video.deviceId = { exact: this.selectedCamera };
         }
         
         console.log('Starting video stream with constraints:', constraints);
         
         this.stream = await navigator.mediaDevices.getUserMedia(constraints);
         
         const videoElement = this.$refs.videoElement;
         videoElement.srcObject = this.stream;
         
         // Wait for video to be ready
         await new Promise((resolve) => {
           videoElement.onloadedmetadata = resolve;
         });
         
         console.log('Video stream started successfully');
         this.isLoading = false;
         this.isScanning = true;
         
         // Start barcode detection
         this.codeReader.decodeFromVideoDevice(
           this.selectedCamera || 'default',
           videoElement,
           (result, error) => {
             if (result && !this.isProcessingScan) {
               console.log('Barcode detected:', result.text);
               this.onBarcodeDetected(result.text);
             }
             if (error && error.name !== 'NotFoundException') {
               console.error('Scanning error:', error);
             }
           }
         );
         
       } catch (error) {
         console.error('Error starting scanner:', error);
         this.isLoading = false;
         
         if (error.name === 'NotAllowedError') {
           this.error = this.t.cameraAccessDenied;
         } else if (error.name === 'NotFoundError') {
           this.error = this.t.noCameraFound;
         } else if (error.name === 'NotReadableError') {
           this.error = this.t.cameraInUse;
         } else {
           this.error = this.t.errorStartingScanner + error.message;
         }
       }
     },
    
         async switchCamera() {
       if (this.isScanning) {
         await this.stopScanning();
         await this.startScanning();
       }
     },
     
     async refreshCameras() {
       this.error = '';
       await this.getAvailableCameras();
       if (this.cameras.length > 0) {
         await this.startScanning();
       }
     },
    
    async stopScanning() {
      this.isScanning = false;
      
      if (this.codeReader) {
        this.codeReader.reset();
      }
      
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    },
    
    onBarcodeDetected(code) {
      // Prevent multiple rapid scans of the same barcode
      if (this.isProcessingScan) {
        return;
      }
      
      // Validate barcode format (13 digits for EAN-13)
      if (/^\d{13}$/.test(code)) {
        this.isProcessingScan = true;
        
        // Immediately stop scanning to prevent multiple detections
        this.stopScanning();
        
        this.lastScannedCode = code;
        this.$emit('update:modelValue', code);
        // Remove the barcode-scanned event emission to prevent automatic search
        // this.$emit('barcode-scanned', code);
        
        // Auto-close scanner after successful scan
        setTimeout(() => {
          this.closeScanner();
        }, 1500);
      } else {
        this.error = this.t.invalidBarcode;
      }
    },
    
    useManualBarcode() {
      if (this.manualBarcode && /^\d{13}$/.test(this.manualBarcode)) {
        this.$emit('update:modelValue', this.manualBarcode);
        // Remove the barcode-scanned event emission to prevent automatic search
        // this.$emit('barcode-scanned', this.manualBarcode);
        this.closeScanner();
      } else {
        this.error = this.t.pleaseEnterValidBarcode13;
      }
    },
    
               async closeScanner() {
             await this.stopScanning();
             this.showScanner = false;
             this.error = '';
             this.lastScannedCode = '';
             this.manualBarcode = '';
             this.isProcessingScan = false; // Reset processing flag
           },
    
    cleanup() {
      this.stopScanning();
      if (this.codeReader) {
        this.codeReader.reset();
      }
    },
    
    // Method to handle language changes from parent component
    handleLanguageChange(lang) {
      this.currentLanguage = lang;
    }
  }
};
</script>

<style scoped>
.barcode-scanner-container {
  position: relative;
}

.scanner-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
  margin-bottom: 0;
}

.scanner-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.scanner-modal {
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

.scanner-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.scanner-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f7fafc;
  color: #2d3748;
}

.scanner-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(90vh - 120px); /* Account for header height */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.scanner-body::-webkit-scrollbar {
  width: 8px;
}

.scanner-body::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 4px;
}

.scanner-body::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

.scanner-body::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.camera-selector {
  padding: 1rem 1.5rem;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 0;
}

.camera-selector label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
}

 .camera-selector select {
   width: 100%;
   padding: 0.75rem;
   border: 1px solid #e2e8f0;
   border-radius: 6px;
   font-size: 1rem;
   margin-bottom: 0.5rem;
 }
 
 .refresh-btn {
   width: 100%;
   padding: 0.75rem;
   background: #667eea;
   color: white;
   border: none;
   border-radius: 6px;
   font-size: 1rem;
   cursor: pointer;
   transition: background 0.2s;
 }
 
 .refresh-btn:hover {
   background: #5a67d8;
 }

.video-container {
  position: relative;
  width: 100%;
  height: 300px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-container video.scanning {
  filter: brightness(1.1) contrast(1.1);
}

.scanning-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.scanning-frame {
  position: relative;
  width: 250px;
  height: 150px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}

.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #667eea;
}

.top-left {
  top: -3px;
  left: -3px;
  border-right: none;
  border-bottom: none;
  border-radius: 8px 0 0 0;
}

.top-right {
  top: -3px;
  right: -3px;
  border-left: none;
  border-bottom: none;
  border-radius: 0 8px 0 0;
}

.bottom-left {
  bottom: -3px;
  left: -3px;
  border-right: none;
  border-top: none;
  border-radius: 0 0 0 8px;
}

.bottom-right {
  bottom: -3px;
  right: -3px;
  border-left: none;
  border-top: none;
  border-radius: 0 0 8px 0;
}

.scanning-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #667eea, transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(0); }
  100% { transform: translateY(150px); }
}

.scanning-text {
  margin-top: 1rem;
  color: white;
  font-size: 1rem;
  text-align: center;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.scanner-status {
  margin-bottom: 1rem;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.95rem;
}

.status-message.loading {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.status-message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-message.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-message.info {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.manual-input {
  border-top: 1px solid #e2e8f0;
  padding-top: 1rem;
}

.manual-input p {
  margin: 0 0 0.5rem 0;
  color: #4a5568;
  font-size: 0.9rem;
}

.manual-input input {
  width: calc(100% - 80px);
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px 0 0 6px;
  font-size: 1rem;
  border-right: none;
}

.manual-btn {
  width: 80px;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0 6px 6px 0;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.manual-btn:hover {
  background: #5a67d8;
}

@media (max-width: 768px) {
  .scanner-content {
    width: 95%;
    margin: 1rem;
  }
  
  .video-container {
    height: 250px;
  }
  
  .scanning-frame {
    width: 200px;
    height: 120px;
  }
  
  .manual-input input {
    width: calc(100% - 70px);
  }
  
  .manual-btn {
    width: 70px;
  }
}
</style> 