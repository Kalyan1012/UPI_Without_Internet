from pydantic import BaseModel


class MeshPacket(BaseModel):
    packet_id: str
    ttl: int
    created_at: str
    ciphertext: str