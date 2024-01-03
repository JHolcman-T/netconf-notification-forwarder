from enum import IntEnum, auto
from . import get_logger


class Status(IntEnum):
    OK = auto()
    WARN = auto()
    ERR = auto()


class SubscriptionManager:
    def __init__(self):
        self._streams = set()
        self._subscriptions = dict()
        self.log = get_logger("subscription-manager")

    def get_subscriptions(self, stream: str = None, copy: bool = True):
        if copy:
            return self._subscriptions[stream].copy() if stream else self._subscriptions.copy()
        return self._subscriptions[stream] if stream else self._subscriptions

    def get_streams(self):
        return self._streams

    def disconnect_client(self, client):
        for stream in self.get_streams():
            if client in self._subscriptions[stream]:
                self.unsubscribe(stream, client)

    def subscribe(self, stream: str, client) -> Status:
        if stream not in self._streams:
            self.log.error(f"{stream=} is not registered! Can't create subscription for {client=} on {stream=}!")
            return Status.ERR
        elif client in self._subscriptions[stream]:
            self.log.warning(f"{client=} is already subscribing to {stream=}!")
            return Status.WARN
        else:
            self._subscriptions[stream].append(client)
            self.log.info(f"Created subscription for {client=} on {stream=}")
            return Status.OK

    def unsubscribe(self, stream: str, client) -> Status:
        self.log.info(f"Removing subscription on {stream=} for {client=}")
        self._subscriptions[stream].remove(client)
        return Status.OK

    def register_stream(self, stream: str) -> Status:
        if stream in self._streams:
            self.log.warning(f"{stream=} already registered!")
            return Status.WARN
        else:
            self._streams.add(stream)
            self._subscriptions[stream] = list()
            self.log.debug(f"Registered {stream=}")
            return Status.OK

    def unregister_stream(self, stream: str) -> Status:
        if stream not in self._streams:
            self.log.warning(f"{stream=} is not registered!")
            return Status.WARN
        else:
            self._streams.remove(stream)
            self.log.warning(
                f"Removing subscriptions for {self._subscriptions[stream]} due to unregistering a stream, {stream=}!"
            )
            for client in self.get_subscriptions(stream):
                self.unsubscribe(stream, client)
            self._subscriptions.pop(stream)
            self.log.info(f"Unregistered {stream=}")
            return Status.OK
