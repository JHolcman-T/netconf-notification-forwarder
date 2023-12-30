from dataclasses import dataclass
from .rpc import RPC, RPCs
import xml.etree.ElementTree as ET


@dataclass
class Subscription:
    stream: str

    @staticmethod
    def from_message(message: str) -> RPC:
        xml = ET.fromstring(message)
        stream_element = xml.find(".//{urn:ietf:params:xml:ns:netconf:notification:1.0}stream")
        if stream_element is not None:
            stream = stream_element.text
            subscription = Subscription(stream)
            message_id = xml.attrib.get("message-id")
            return RPC(RPCs.Subscribe, subscription, message_id)
        raise Exception("F")
