# backend/security.py
from cryptography.fernet import Fernet

# PASTE THE KEY YOU GENERATED HERE. KEEP THIS KEY SAFE!
# It must be the bytes object, e.g., b'27x_SecretKey_Goes_Here...='
ENCRYPTION_KEY = b'Hlgbs9JmghF3S4ohJiuYdHWw5CkOoyDDM8eQKZxRJzU='

fernet = Fernet(ENCRYPTION_KEY)

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()