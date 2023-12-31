from enum import IntEnum, auto
from dataclasses import dataclass


class RPCs(IntEnum):
    Subscribe = auto()
    KillSession = auto()
    CloseSession = auto()
    Unsupported = auto()


@dataclass
class RPC:
    type: RPCs
    data: object
    message_id: str = ""
