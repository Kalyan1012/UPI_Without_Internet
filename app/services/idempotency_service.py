class IdempotencyService:
    def __init__(self):
        # Stores hashes or IDs of packets we've already processed
        self.seen_packets = set()

    def claim(self, packet_hash: str) -> bool:
        """
        Returns True if this is the first time we've seen the packet.
        Returns False if it's a duplicate.
        """
        if packet_hash in self.seen_packets:
            return False

        self.seen_packets.add(packet_hash)
        return True


# Singleton instance used throughout the app
idempotency_service = IdempotencyService()