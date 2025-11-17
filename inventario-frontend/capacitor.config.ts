import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.lagranmanzana.inventario',
  appName: 'Inventario La Gran Manzana',
  webDir: 'dist',
  server: {
    // Para desarrollo en red local
    // androidScheme: 'https',
    // cleartext: true
  },
  android: {
    backgroundColor: '#2E8B57',
    allowMixedContent: true,
    captureInput: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#2E8B57',
      showSpinner: false,
      androidSpinnerStyle: 'large',
      spinnerColor: '#ffffff'
    }
  }
};

export default config;
