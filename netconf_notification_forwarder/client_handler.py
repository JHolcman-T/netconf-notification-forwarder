from asyncssh.process import SSHServerProcess
from . import models


class ClientHandler:
    def __init__(self, process: SSHServerProcess):
        self.process = process

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
