# ops/secrets.py
import os, base64
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv("FERNET_KEY")  # stocké dans KMS/Vault

def encrypt(b: bytes) -> str:
    return Fernet(FERNET_KEY).encrypt(b).decode()

def decrypt(s: str) -> bytes:
    return Fernet(FERNET_KEY).decrypt(s.encode())
