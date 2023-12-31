from asyncssh.process import SSHServerProcess
from . import models


class ClientHandler:
    def __init__(self, process: SSHServerProcess):
        self.process = process
        self._addr = self.process.channel.get_connection()._peer_addr
        self._port = self.process.channel.get_connection()._peer_port

    def __str__(self):
        return f"ClientHandler(address={self._addr}, port={self._port})"

    def __repr__(self):
        return self.__str__()

    async def read(self) -> models.RPC or None:
        data = await self.process.stdin.readuntil("]]>]]>")
        data = data.removesuffix("]]>]]>")
        out = None
        print(data)
        if "create-subscription" in data:
            out = models.Subscription.from_message(data)
        elif "kill-session" in data:
            out = models.KillSession.from_message(data)
        elif "close-session" in data:
            out = models.CloseSession.from_message(data)
        elif "hello" in data:
            pass
        else:
            out = models.Unsupported.from_message(data)
        return out

    def send(self, data: str):
        self.process.stdout.write(data)
