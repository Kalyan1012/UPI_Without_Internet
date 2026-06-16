from app.mesh.mesh_packet import MeshPacket


class VirtualDevice:
    def __init__(self, device_id: str, has_internet: bool = False):
        self.device_id = device_id
        self.has_internet = has_internet
        self.packets: list[MeshPacket] = []

    def receive_packet(self, packet: MeshPacket):
        # Avoid storing the same packet twice
        if not any(p.packet_id == packet.packet_id for p in self.packets):
            self.packets.append(packet)