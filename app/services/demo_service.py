import uuid
from datetime import datetime

from app.services.crypto_service import crypto_service
from app.mesh.mesh_packet import MeshPacket


class DemoService:
    def create_payment_packet(
        self,
        sender_id: str,
        receiver_id: str,
        amount: float,
    ):
        # The actual payment information
        payment_data = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount,
            "nonce": str(uuid.uuid4()),
            "signed_at": datetime.utcnow().isoformat(),
        }

        # Encrypt the payment
        encrypted = crypto_service.encrypt_payment(payment_data)

        # Wrap it inside a mesh packet
        packet = MeshPacket(
            packet_id=str(uuid.uuid4()),
            ttl=5,
            created_at=datetime.utcnow().isoformat(),
            ciphertext=encrypted,
        )

        return packet


demo_service = DemoService()