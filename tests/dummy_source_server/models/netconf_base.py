from dataclasses import dataclass
from .rpc import RPC, RPCs
import xml.etree.ElementTree as ET


@dataclass
class KillSession:
    session_id: int

    @staticmethod
    def from_message(message: str) -> RPC:
        xml = ET.fromstring(message)
        session_id_element = xml.find(".//{urn:ietf:params:xml:ns:netconf:base:1.0}session-id")
        if session_id_element is not None:
            session_id = int(session_id_element.text)
            kill = KillSession(session_id)
            message_id = xml.attrib.get("message-id")
            return RPC(RPCs.KillSession, kill, message_id)
        raise Exception("F")


@dataclass
class CloseSession:
    pass

    @staticmethod
    def from_message(message: str) -> RPC:
        xml = ET.fromstring(message)
        message_id = xml.attrib.get("message-id")
        return RPC(RPCs.CloseSession, CloseSession(), message_id)
