import hashlib
from datetime import datetime, timedelta

from app.services.crypto_service import crypto_service
from app.services.account_service import AccountService


class BridgeIngestionService:
    def __init__(self):
        self.account_service = AccountService()
        self.processed_hashes = set()

    def ingest(self, mesh_packet):
        # Create a unique hash of the ciphertext
        packet_hash = hashlib.sha256(
            mesh_packet.ciphertext.encode("utf-8")
        ).hexdigest()

        # Ignore duplicate packets
        if packet_hash in self.processed_hashes:
            return {
                "outcome": "DUPLICATE_DROPPED"
            }

        self.processed_hashes.add(packet_hash)

        # Decrypt the payment
        payment = crypto_service.decrypt_payment(
            mesh_packet.ciphertext
        )

        # Check if packet is older than 24 hours
        signed_at = datetime.fromisoformat(payment["signed_at"])

        if datetime.utcnow() - signed_at > timedelta(hours=24):
            return {
                "outcome": "INVALID",
                "reason": "Packet expired"
            }

        # Perform settlement
        self.account_service.transfer(
            transaction_id=payment["nonce"],
            sender_id=payment["sender_id"],
            receiver_id=payment["receiver_id"],
            amount=payment["amount"]
        )

        return {
            "outcome": "SETTLED"
        }


bridge_ingestion_service = BridgeIngestionService()