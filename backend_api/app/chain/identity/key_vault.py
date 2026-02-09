"""
Key vault service for encryption and key management
"""
import os
import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from app.core.config import settings


class KeyVault:
    """Key vault for managing encryption keys"""
    
    def __init__(self):
        """Initialize the key vault with master encryption key"""
        # Use SECRET_KEY from settings as master key for encrypting stored keys
        self._master_key = self._derive_master_key(settings.SECRET_KEY)
        self._cipher = Fernet(self._master_key)
    
    def _derive_master_key(self, secret: str) -> bytes:
        """Derive a Fernet-compatible key from the secret"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'masidy_chain_salt',  # Fixed salt for deterministic key derivation
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key
    
    def generate_root_key(self) -> tuple[str, str]:
        """
        Generate a new root key
        
        Returns:
            tuple: (raw_key, encrypted_key) - raw key for immediate use, encrypted for storage
        """
        # Generate a random 256-bit key
        raw_key = secrets.token_urlsafe(32)
        
        # Encrypt the key for storage
        encrypted_key = self._cipher.encrypt(raw_key.encode()).decode()
        
        return raw_key, encrypted_key
    
    def decrypt_root_key(self, encrypted_key: str) -> str:
        """
        Decrypt a stored root key
        
        Args:
            encrypted_key: The encrypted key from database
            
        Returns:
            The decrypted raw key
        """
        return self._cipher.decrypt(encrypted_key.encode()).decode()
    
    def derive_key(self, root_key: str, scope: str, scope_id: Optional[str] = None) -> tuple[str, str]:
        """
        Derive a scoped key from root key using deterministic derivation
        
        Args:
            root_key: The decrypted root key
            scope: The scope (e.g., 'project', 'integration')
            scope_id: Optional ID within the scope
            
        Returns:
            tuple: (derived_key, encrypted_derived_key)
        """
        # Create deterministic derivation input
        derivation_input = f"{root_key}:{scope}"
        if scope_id:
            derivation_input += f":{scope_id}"
        
        # Use PBKDF2 for deterministic key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=scope.encode(),  # Use scope as salt for deterministic derivation
            iterations=100000,
        )
        
        derived_bytes = kdf.derive(derivation_input.encode())
        derived_key = base64.urlsafe_b64encode(derived_bytes).decode()
        
        # Encrypt the derived key for storage
        encrypted_derived_key = self._cipher.encrypt(derived_key.encode()).decode()
        
        return derived_key, encrypted_derived_key
    
    def decrypt_derived_key(self, encrypted_key: str) -> str:
        """
        Decrypt a stored derived key
        
        Args:
            encrypted_key: The encrypted derived key from database
            
        Returns:
            The decrypted derived key
        """
        return self._cipher.decrypt(encrypted_key.encode()).decode()
    
    @staticmethod
    def generate_key_id(prefix: str = "key") -> str:
        """
        Generate a unique key ID
        
        Args:
            prefix: Prefix for the key ID (e.g., 'root', 'derived')
            
        Returns:
            Unique key ID
        """
        random_suffix = secrets.token_urlsafe(16)
        return f"{prefix}_{random_suffix}"
    
    @staticmethod
    def hash_data(data: str) -> str:
        """
        Hash data using SHA256
        
        Args:
            data: Data to hash
            
        Returns:
            Hex digest of the hash
        """
        return hashlib.sha256(data.encode()).hexdigest()


# Singleton instance
key_vault = KeyVault()
