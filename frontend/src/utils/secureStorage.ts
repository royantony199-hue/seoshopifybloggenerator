/**
 * Secure storage utility for handling sensitive data like authentication tokens
 * Provides fallbacks and security enhancements over basic localStorage
 */

interface StorageOptions {
  encrypt?: boolean;
  ttl?: number; // Time to live in milliseconds
}

interface StoredData {
  value: any;
  encrypted?: boolean;
  timestamp: number;
  ttl?: number;
}

class SecureStorage {
  private static instance: SecureStorage;
  private encryptionKey: string = '';

  private constructor() {
    // Generate or retrieve encryption key
    this.initializeEncryption();
  }

  public static getInstance(): SecureStorage {
    if (!SecureStorage.instance) {
      SecureStorage.instance = new SecureStorage();
    }
    return SecureStorage.instance;
  }

  private initializeEncryption(): void {
    // In a real application, you'd want to use a more secure method
    // For now, we'll use a session-based key
    let key = sessionStorage.getItem('_encryption_key');
    if (!key) {
      key = this.generateEncryptionKey();
      sessionStorage.setItem('_encryption_key', key);
    }
    this.encryptionKey = key;
  }

  private generateEncryptionKey(): string {
    // Simple key generation - in production, use proper crypto libraries
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  private simpleEncrypt(text: string): string {
    // Simple XOR encryption - in production, use proper encryption
    let result = '';
    for (let i = 0; i < text.length; i++) {
      const keyChar = this.encryptionKey[i % this.encryptionKey.length];
      result += String.fromCharCode(text.charCodeAt(i) ^ keyChar.charCodeAt(0));
    }
    return btoa(result);
  }

  private simpleDecrypt(encryptedText: string): string {
    try {
      const text = atob(encryptedText);
      let result = '';
      for (let i = 0; i < text.length; i++) {
        const keyChar = this.encryptionKey[i % this.encryptionKey.length];
        result += String.fromCharCode(text.charCodeAt(i) ^ keyChar.charCodeAt(0));
      }
      return result;
    } catch {
      return '';
    }
  }

  public setItem(key: string, value: any, options: StorageOptions = {}): boolean {
    try {
      const data: StoredData = {
        value: options.encrypt ? this.simpleEncrypt(JSON.stringify(value)) : value,
        encrypted: options.encrypt || false,
        timestamp: Date.now(),
        ttl: options.ttl
      };

      // Try sessionStorage first for sensitive data, fallback to localStorage
      try {
        sessionStorage.setItem(key, JSON.stringify(data));
        return true;
      } catch {
        // SessionStorage failed, try localStorage
        localStorage.setItem(key, JSON.stringify(data));
        return true;
      }
    } catch (error) {
      console.error('Failed to store data:', error);
      return false;
    }
  }

  public getItem(key: string): any {
    try {
      // Try sessionStorage first, then localStorage
      let item = sessionStorage.getItem(key) || localStorage.getItem(key);
      
      if (!item) {
        return null;
      }

      const data: StoredData = JSON.parse(item);

      // Check if item has expired
      if (data.ttl && (Date.now() - data.timestamp) > data.ttl) {
        this.removeItem(key);
        return null;
      }

      // Decrypt if needed
      if (data.encrypted) {
        const decrypted = this.simpleDecrypt(data.value);
        if (!decrypted) return null;
        try {
          return JSON.parse(decrypted);
        } catch (e) {
          console.error('Failed to parse decrypted data:', e);
          return null;
        }
      }

      return data.value;
    } catch (error) {
      console.error('Failed to retrieve data:', error);
      return null;
    }
  }

  public removeItem(key: string): void {
    try {
      sessionStorage.removeItem(key);
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove data:', error);
    }
  }

  public clear(): void {
    try {
      sessionStorage.clear();
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }

  public hasItem(key: string): boolean {
    return this.getItem(key) !== null;
  }

  // Secure methods for authentication tokens
  public setAuthToken(token: string, ttl: number = 24 * 60 * 60 * 1000): boolean {
    return this.setItem('auth_token', token, { 
      encrypt: true, 
      ttl: ttl 
    });
  }

  public getAuthToken(): string | null {
    return this.getItem('auth_token');
  }

  public removeAuthToken(): void {
    this.removeItem('auth_token');
  }

  public setUserData(userData: any, ttl: number = 24 * 60 * 60 * 1000): boolean {
    return this.setItem('auth_user', userData, { 
      encrypt: true, 
      ttl: ttl 
    });
  }

  public getUserData(): any {
    return this.getItem('auth_user');
  }

  public removeUserData(): void {
    this.removeItem('auth_user');
  }

  // Clear all auth-related data
  public clearAuthData(): void {
    this.removeAuthToken();
    this.removeUserData();
  }
}

// Export singleton instance
export const secureStorage = SecureStorage.getInstance();

// Backward compatibility helpers
export const setSecureItem = (key: string, value: any, options?: StorageOptions) => 
  secureStorage.setItem(key, value, options);

export const getSecureItem = (key: string) => 
  secureStorage.getItem(key);

export const removeSecureItem = (key: string) => 
  secureStorage.removeItem(key);

export default secureStorage;