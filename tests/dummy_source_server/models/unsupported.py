from dataclasses import dataclass
from .rpc import RPC, RPCs
import xml.etree.ElementTree as ET


@dataclass
class Unsupported:
    message: str

    @staticmethod
    def from_message(message: str) -> RPC:
        xml = ET.fromstring(message)
        message_id = xml.attrib.get("message-id")
        return RPC(RPCs.Unsupported, Unsupported(message), message_id)
