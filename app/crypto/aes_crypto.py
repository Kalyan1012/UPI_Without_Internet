import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESCrypto:
    def generate_key(self) -> bytes:
        """
        Generates a random 256-bit (32-byte) AES key.
        """
        return AESGCM.generate_key(bit_length=256)

    def encrypt(self, plaintext: bytes, key: bytes):
        """
        Encrypts plaintext using AES-GCM.

        Returns:
            nonce: Random value used for encryption
            ciphertext: Encrypted data (includes authentication tag)
        """
        nonce = os.urandom(12)  # 96-bit nonce recommended for AES-GCM
        aesgcm = AESGCM(key)

        ciphertext = aesgcm.encrypt(
            nonce=nonce,
            data=plaintext,
            associated_data=None
        )

        return nonce, ciphertext

    def decrypt(self, nonce: bytes, ciphertext: bytes, key: bytes):
        """
        Decrypts AES-GCM encrypted data.
        """
        aesgcm = AESGCM(key)

        plaintext = aesgcm.decrypt(
            nonce=nonce,
            data=ciphertext,
            associated_data=None
        )

        return plaintext
aes_crypto = AESCrypto()    