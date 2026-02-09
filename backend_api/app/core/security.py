"""
Security utilities - Password hashing and JWT tokens
"""
import base64
from datetime import datetime, timedelta
from typing import Optional, Any

import bcrypt
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify a token and return the subject (user_id)"""
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != token_type:
        return None
    
    return payload.get("sub")


def get_encryption_key() -> bytes:
    """Get or derive encryption key from settings"""
    # Use PBKDF2 to derive a proper 32-byte key from the encryption key setting
    # Note: Using a static salt here since we're deriving the master key from a secret
    # The actual per-token security comes from Fernet's random IV/nonce
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'masidy_github_token_salt',  # Static salt for master key derivation
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.GITHUB_TOKEN_ENCRYPTION_KEY.encode()))
    return key


def encrypt_token(token: str) -> str:
    """
    Encrypt a GitHub token for secure storage.
    
    Uses Fernet encryption which provides authenticated encryption with
    a random 128-bit IV for each encryption operation, ensuring unique
    ciphertexts even for identical plaintexts.
    """
    if not token:
        return ""
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        # Fernet automatically generates a random IV/nonce for each encryption
        encrypted = f.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        # Log error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Token encryption failed: {e}")
        raise ValueError("Failed to encrypt token")


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a GitHub token from storage.
    
    Verifies the authentication tag and decrypts the token.
    """
    if not encrypted_token:
        return ""
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
        # Fernet automatically verifies the authentication tag
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        # Log error but don't expose details
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Token decryption failed: {e}")
        raise ValueError("Failed to decrypt token")

