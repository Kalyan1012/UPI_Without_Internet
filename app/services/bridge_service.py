from app.services.crypto_service import crypto_service
from app.services.account_service import AccountService

service = AccountService()


class BridgeService:

    def process_bridge_packet(self, packet):
        try:
            data = crypto_service.decrypt_payment(packet.ciphertext)

            sender = data["sender_id"]
            receiver = data["receiver_id"]
            amount = data["amount"]
            transaction_id = data.get("transaction_id", packet.packet_id)

            result = service.transfer(
                transaction_id,
                sender,
                receiver,
                amount
            )

            return {
                "packet_id": packet.packet_id,
                "status": "SETTLED",
                "result": result
            }

        except Exception as e:
            return {
                "packet_id": packet.packet_id,
                "status": "FAILED",
                "error": str(e)
            }