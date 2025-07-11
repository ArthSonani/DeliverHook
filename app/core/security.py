from cryptography.fernet import Fernet
import os

# Generate a key for Fernet encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_secret(secret: str) -> str:
    """Encrypt a secret key before storage."""
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt a stored secret key."""
    return fernet.decrypt(encrypted_secret.encode()).decode()