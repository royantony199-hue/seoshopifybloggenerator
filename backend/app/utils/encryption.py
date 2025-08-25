#!/usr/bin/env python3
"""
Encryption utilities for sensitive data storage
"""

from cryptography.fernet import Fernet
from typing import Optional
import base64
import os

class EncryptionManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize encryption manager with key"""
        if encryption_key:
            # Use provided key
            self.encryption_key = encryption_key.encode()
        else:
            # Generate or load key from environment
            key_env = os.getenv('ENCRYPTION_KEY')
            if key_env:
                self.encryption_key = key_env.encode()
            else:
                # Generate new key (for development only)
                self.encryption_key = base64.urlsafe_b64encode(os.urandom(32))
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string"""
        if not plaintext:
            return ""
        
        encrypted_data = self.cipher_suite.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string"""
        if not ciphertext:
            return ""
        
        try:
            encrypted_data = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()

# Global encryption manager instance
encryption_manager = EncryptionManager()

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure storage"""
    return encryption_manager.encrypt(api_key)

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage"""
    return encryption_manager.decrypt(encrypted_key)