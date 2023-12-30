from enum import IntEnum, auto


class Status(IntEnum):
    OK = auto()
    WARN = auto()
    ERR = auto()


class SubscriptionManager:
    def __init__(self):
        self._streams = set()
        self._subscriptions = dict()
        self.register_stream("NETCONF")

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
            print(f"[ERR]: {stream=} is not registered! Can't create subscription for {client=} on {stream=}!")
            return Status.ERR
        elif client in self._subscriptions[stream]:
            print(f"[WARN]: {client=} is already subscribing to {stream=}!")
            return Status.WARN
        else:
            self._subscriptions[stream].append(client)
            return Status.OK

    def unsubscribe(self, stream: str, client) -> Status:
        print(f"[INFO]: Removing subscription on {stream=} for {client=}")
        self._subscriptions[stream].remove(client)
        return Status.OK

    def register_stream(self, stream: str) -> Status:
        if stream in self._streams:
            print(f"[WRAN]: {stream=} already registered!")
            return Status.WARN
        else:
            self._streams.add(stream)
            self._subscriptions[stream] = list()
            print(f"[INFO]: Registered {stream=}")
            return Status.OK

    def unregister_stream(self, stream: str) -> Status:
        if stream not in self._streams:
            print(f"[WARN]: {stream=} is not registered!")
            return Status.WARN
        else:
            self._streams.remove(stream)
            print(
                f"[WARN]: Removing subscriptions for {self._subscriptions[stream]} due to unregistering a stream,"
                f" {stream=}!"
            )
            for client in self.get_subscriptions(stream):
                self.unsubscribe(stream, client)
            self._subscriptions.pop(stream)
            print(f"[INFO]: Unregistered {stream=}")
            return Status.OK
