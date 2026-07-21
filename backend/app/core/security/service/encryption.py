import base64
import secrets
from typing import Protocol

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecretEncryptionPort(Protocol):
    def encrypt(self, plaintext: str) -> tuple[str, str]: ...

    def decrypt(self, ciphertext: str, nonce: str) -> str: ...


class AesGcmSecretEncryption:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 bytes")
        self._cipher = AESGCM(key)

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii")

    @staticmethod
    def _decode(value: str) -> bytes:
        return base64.urlsafe_b64decode(value.encode("ascii"))

    def encrypt(self, plaintext: str) -> tuple[str, str]:
        nonce = secrets.token_bytes(12)
        ciphertext = self._cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
        return self._encode(ciphertext), self._encode(nonce)

    def decrypt(self, ciphertext: str, nonce: str) -> str:
        return self._cipher.decrypt(self._decode(nonce), self._decode(ciphertext), None).decode("utf-8")
