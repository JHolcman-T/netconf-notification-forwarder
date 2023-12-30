import asyncssh, sys, asyncio
from typing import Optional
import xml.etree.ElementTree as ET
from .client_handler import ClientHandler
from .subscribtion_manager import SubscriptionManager, Status
from . import models
from . import util
from . import notifications_subscriber
from . import router
from . import settings


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
    def __init__(self, ipaddress: str, port: int, settings: settings.settings = None):
        self.ipaddress = ipaddress
        self.port = port
        self.host_keys = ["host_key"]
        self.authorized_keys = []
        self.clients = []
        self.subscription_manager = SubscriptionManager()
        self.notifications_subscriber = notifications_subscriber.Subscriber()
        self.settings = settings
        if self.settings is not None:
            self._init_settings()
        else:
            self.router = router.Router(dict())

    def _init_settings(self):
        streams = self.settings.get_streams()
        # TODO: Don't expose source streams to client if not defined in configuration file
        self.register_streams(streams)
        for rule in self.settings.rules:  # type: settings.Rule
            for host in rule.hosts:
                for stream in rule.get_source_streams():
                    self.notifications_subscriber.subscribe(host, rule.port, stream)
            router_map = dict()
            for stream_route in rule.streams:
                for stream in stream_route.source:
                    map_entry = router_map.get(stream, False)
                    if map_entry:
                        router_map[stream].update(set(stream_route.destination))
                    else:
                        router_map[stream] = set(stream_route.destination)
            self.router = router.Router(router_map)

    def register_stream(self, stream: str):
        self.subscription_manager.register_stream(stream)
        self.notifications_subscriber.register_stream(stream)

    def register_streams(self, streams: list):
        for stream in streams:
            self.register_stream(stream)

    # @staticmethod
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
                                # "<error-tag>bad-element</error-tag>"
                                "<error-severity>error</error-severity>"
                                # "<error-app-tag>43</error-app-tag>"
                                '<error-message xml:lang="en">Could not subscribe</error-message>'
                                "<error-info>"
                                # "<bad-element>vrfAny</bad-element>"
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
                print("END")
            except Exception as exc:
                print(f"EXC: {exc}")
                break
        self.clients.remove(client_handler)
        self.subscription_manager.disconnect_client(client_handler)
        process.exit(0)

    async def send(self):
        notifi = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + '<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">\n'
            + "    <eventTime>2011-01-04T12:30:46</eventTime>\n"
            + '    <event xmlns="http://www.hp.com/netconf/event:1.0">\n'
            + "        <Group>DEV</Group>\n"
            + "        <Code>FAN_DIRECTION_NOT_PREFERRED</Code>\n"
            + "        <Slot>6</Slot>\n"
            + "        <Severity>Alert</Severity>\n"
            + "        <context>Fan 1 airflow direction is not preferred on slot 6, please check it.</context>\n"
            + "    </event>\n"
            + "</notification>]]>]]>\n"
        )
        while True:
            await asyncio.sleep(10)
            for stream, clients in self.subscription_manager.get_subscriptions().items():
                for client in clients:
                    print(f"Stream: {stream} Client: {client}")
                    client.send(notifi)

    async def send2(self):
        async for notification in self.notifications_subscriber.notifications():
            destinations = self.router.get(notification.stream)
            for destination_stream in destinations:
                for client in self.subscription_manager.get_subscriptions(destination_stream):
                    print(f"Re-sending {notification} to client={client}")
                    client.send(util.to_message(notification.payload))

    async def start(self):
        await asyncssh.create_server(
            _ServerCallbacks,
            self.ipaddress,
            self.port,
            server_host_keys=self.host_keys,
            # authorized_client_keys=self.authorized_keys,
            process_factory=self.handle_client,
        )
