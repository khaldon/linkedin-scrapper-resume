"""
Encryption module for securely storing LinkedIn credentials
Uses AES-256 encryption with user-specific keys
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from typing import Dict, Optional

class CredentialEncryption:
    """Handle encryption and decryption of LinkedIn credentials"""
    
    def __init__(self, user_email: str):
        """
        Initialize encryption with user-specific key
        
        Args:
            user_email: User's email to generate unique encryption key
        """
        self.user_email = user_email
        self.master_key = os.getenv("ENCRYPTION_MASTER_KEY", "default-master-key-change-in-production")
        self.cipher = self._create_cipher()
    
    def _create_cipher(self) -> Fernet:
        """Create a Fernet cipher with user-specific key"""
        # Derive key from master key + user email
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.user_email.encode(),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt_credentials(self, email: str, password: str) -> str:
        """
        Encrypt LinkedIn credentials
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            
        Returns:
            Encrypted credentials as base64 string
        """
        credentials = {
            "email": email,
            "password": password
        }
        
        # Convert to JSON and encrypt
        json_data = json.dumps(credentials)
        encrypted_data = self.cipher.encrypt(json_data.encode())
        
        # Return as base64 string
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Optional[Dict[str, str]]:
        """
        Decrypt LinkedIn credentials
        
        Args:
            encrypted_data: Base64 encoded encrypted credentials
            
        Returns:
            Dictionary with email and password, or None if decryption fails
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            
            # Parse JSON
            credentials = json.loads(decrypted_data.decode())
            
            return credentials
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    @staticmethod
    def generate_master_key() -> str:
        """Generate a new master encryption key"""
        return Fernet.generate_key().decode()


def encrypt_linkedin_credentials(user_email: str, linkedin_email: str, linkedin_password: str) -> str:
    """
    Convenience function to encrypt LinkedIn credentials
    
    Args:
        user_email: User's account email
        linkedin_email: LinkedIn email
        linkedin_password: LinkedIn password
        
    Returns:
        Encrypted credentials string
    """
    encryptor = CredentialEncryption(user_email)
    return encryptor.encrypt_credentials(linkedin_email, linkedin_password)


def decrypt_linkedin_credentials(user_email: str, encrypted_data: str) -> Optional[Dict[str, str]]:
    """
    Convenience function to decrypt LinkedIn credentials
    
    Args:
        user_email: User's account email
        encrypted_data: Encrypted credentials string
        
    Returns:
        Dictionary with email and password, or None if decryption fails
    """
    encryptor = CredentialEncryption(user_email)
    return encryptor.decrypt_credentials(encrypted_data)
