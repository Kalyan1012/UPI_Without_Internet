from app.mesh.virtual_device import VirtualDevice
from app.mesh.mesh_packet import MeshPacket


class MeshSimulator:
    def __init__(self):
        self.devices = [
            VirtualDevice("phone-alice"),
            VirtualDevice("phone-bob"),
            VirtualDevice("phone-charlie"),
            VirtualDevice("phone-bridge", has_internet=True),
        ]

    def inject_packet(self, packet: MeshPacket):
        # Put the packet into Alice's phone
        self.devices[0].receive_packet(packet)

    def gossip_round(self):
        # Take a snapshot so we don't modify the list while iterating
        current_packets = {
            device.device_id: list(device.packets)
            for device in self.devices
        }

        for sender in self.devices:
            for packet in current_packets[sender.device_id]:

                # Don't forward expired packets
                if packet.ttl <= 0:
                    continue

                # Create a copy with one less TTL
                forwarded_packet = MeshPacket(
                    packet_id=packet.packet_id,
                    ttl=packet.ttl - 1,
                    created_at=packet.created_at,
                    ciphertext=packet.ciphertext,
                )

                # Send to every other device
                for receiver in self.devices:
                    if receiver.device_id != sender.device_id:
                        receiver.receive_packet(forwarded_packet)

    def get_state(self):
        return {
            device.device_id: [
                packet.packet_id for packet in device.packets
            ]
            for device in self.devices
        }


mesh_simulator = MeshSimulator()