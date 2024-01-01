import asyncssh, sys, asyncio, datetime
from typing import Optional, List
from .client_handler import ClientHandler
from .subscribtion_manager import SubscriptionManager, Status
from . import models
from . import util


class _ServerCallbacks(asyncssh.SSHServer):
    passwords = {"kubih": "lab123", "admin": ""}

    def connection_made(self, conn: asyncssh.SSHServerConnection) -> None:
        print("SSH connection received from %s." % conn.get_extra_info("peername")[0])

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            print("SSH connection error: " + str(exc), file=sys.stderr)
        else:
            print("SSH connection closed.")

    def begin_auth(self, username: str) -> bool:
        # If the user's password is the empty string, no auth is required
        return self.passwords.get(username) != ""

    def password_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:
        pw = self.passwords.get(username, False)
        return pw == password


class Server(asyncssh.SSHServer):
    def __init__(self, ipaddress: str, port: int):
        self.ipaddress = ipaddress
        self.port = port
        self.host_keys = ["host_key"]
        self.authorized_keys = []
        self.clients = []
        self.subscription_manager = SubscriptionManager()

    def register_stream(self, stream: str):
        self.subscription_manager.register_stream(stream)

    def register_streams(self, streams: List[str]):
        for stream in streams:
            self.register_stream(stream)

    async def handle_client(self, process: asyncssh.SSHServerProcess) -> None:
        client_handler = ClientHandler(process)
        self.clients.append(client_handler)
        capability = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            + '<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
            + "  <nc:capabilities>"
            + "    <nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability>"
            # + "    <nc:capability>urn:ietf:params:netconf:base:1.1</nc:capability>" TODO: Implement support for chunking
            + "    <nc:capability>urn:ietf:params:netconf:capability:notification:1.0</nc:capability>"
            + "  </nc:capabilities>"
            + "  <nc:session-id>1</nc:session-id>"
            + "</nc:hello>"
        )
        capability_msg = util.to_message(capability)
        process.stdout.write(capability_msg)

        # TODO: implement reading NETCONF xml RPCs
        while True:
            try:
                rpc = await client_handler.read()
                if rpc:
                    if rpc.type == models.RPCs.Subscribe:
                        message_id = rpc.message_id
                        status = self.subscription_manager.subscribe(rpc.data.stream, client_handler)

                        if status == Status.OK:
                            ok = (
                                '<?xml version="1.0" encoding="UTF-8"?><rpc-reply'
                                ' xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"'
                                f' message-id="{message_id}"><ok/></rpc-reply>]]>]]>'
                            )
                            print(ok)
                            client_handler.send(ok)
                        else:
                            err = (
                                '<?xml version="1.0" encoding="utf-8"?>'
                                f'<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{message_id}">'
                                "<rpc-error>"
                                "<error-type>application</error-type>"
                                "<error-severity>error</error-severity>"
                                '<error-message xml:lang="en">Could not subscribe</error-message>'
                                "<error-info>"
                                "</error-info>"
                                "</rpc-error>"
                                "</rpc-reply>]]>]]>"
                            )
                            print(err)
                            client_handler.send(err)
                    elif rpc.type == models.RPCs.KillSession:
                        message_id = rpc.message_id
                        ok = (
                            '<?xml version="1.0" encoding="UTF-8"?><rpc-reply'
                            ' xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"'
                            f' message-id="{message_id}"><ok/></rpc-reply>]]>]]>'
                        )
                        print(ok)
                        client_handler.send(ok)
                        break
                    elif rpc.type == models.RPCs.CloseSession:
                        message_id = rpc.message_id
                        ok = (
                            '<?xml version="1.0" encoding="UTF-8"?><rpc-reply'
                            ' xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"'
                            f' message-id="{message_id}"><ok/></rpc-reply>]]>]]>'
                        )
                        print(ok)
                        client_handler.send(ok)
                        break
                    elif rpc.type == models.RPCs.Unsupported:
                        err = (
                            '<?xml version="1.0" encoding="utf-8"?>'
                            f'<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{rpc.message_id}">'
                            "<rpc-error>"
                            "<error-type>application</error-type>"
                            "<error-severity>error</error-severity>"
                            '<error-message xml:lang="en">Unsupported action!</error-message>'
                            "<error-info>"
                            "</error-info>"
                            "</rpc-error>"
                            "</rpc-reply>]]>]]>"
                        )
                        print(err)
                        client_handler.send(err)
                        raise SystemError(f"Unsupported: {rpc.data}")
            except Exception as exc:
                print(f"EXC: {exc}")
                break
        self.clients.remove(client_handler)
        self.subscription_manager.disconnect_client(client_handler)
        process.exit(0)

    async def send(self):
        while True:
            await asyncio.sleep(10)
            for stream, clients in self.subscription_manager.get_subscriptions().items():
                iso_date = datetime.datetime.now().isoformat().split(".")[0]
                for client in clients:
                    print(f"Stream: {stream} Client: {client}")
                    notification_content = (
                        '<?xml version="1.0" encoding="UTF-8"?>\n'
                        '<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">\n'
                        f"  <eventTime>{iso_date}</eventTime>\n"
                        '  <event xmlns="http://www.jakub-holcman.com/netconf/event:1.0">\n'
                        f"    <server-address>{self.ipaddress}</server-address>\n"
                        f"    <server-port>{self.port}</server-port>\n"
                        f"    <stream-name>{stream}</stream-name>\n"
                        "  </event>\n"
                        "</notification>]]>]]>\n"
                    )
                    client.send(notification_content)

    async def start(self):
        asyncio.get_event_loop().create_task(self.send())
        await asyncssh.create_server(
            _ServerCallbacks,
            self.ipaddress,
            self.port,
            server_host_keys=self.host_keys,
            # authorized_client_keys=self.authorized_keys,
            process_factory=self.handle_client,
        )
