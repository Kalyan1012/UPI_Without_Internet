import json
import base64

from app.crypto.rsa_crypto import rsa_crypto
from app.crypto.aes_crypto import aes_crypto


class CryptoService:
    def __init__(self):
        self.aes = aes_crypto

    def encrypt_payment(self, payment_data: dict) -> str:
        # Convert dictionary to JSON bytes
        plaintext = json.dumps(payment_data).encode("utf-8")

        # Generate a random AES-256 key
        aes_key = self.aes.generate_key()

        # Encrypt the payment using AES-GCM
        nonce, ciphertext = self.aes.encrypt(plaintext, aes_key)

        # Encrypt the AES key using RSA
        encrypted_key = rsa_crypto.encrypt(aes_key)

        # Combine everything into one byte string
        final_data = encrypted_key + nonce + ciphertext

        # Return as Base64 text so it can be sent over HTTP/JSON
        return base64.b64encode(final_data).decode("utf-8")

    def decrypt_payment(self, encrypted_text: str) -> dict:
        # Convert Base64 back to bytes
        data = base64.b64decode(encrypted_text)

        # RSA-2048 encrypted key is 256 bytes long
        encrypted_key = data[:256]

        # AES-GCM nonce is 12 bytes
        nonce = data[256:268]

        # Remaining bytes are the ciphertext
        ciphertext = data[268:]

        # Recover the AES key using RSA
        aes_key = rsa_crypto.decrypt(encrypted_key)

        # Decrypt the original JSON
        plaintext = self.aes.decrypt(nonce, ciphertext, aes_key)

        # Convert JSON bytes back to a Python dictionary
        return json.loads(plaintext.decode("utf-8"))


crypto_service = CryptoService()