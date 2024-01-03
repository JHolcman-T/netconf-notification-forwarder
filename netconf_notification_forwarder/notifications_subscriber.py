from . import util
from uuid import uuid4
import asyncio, asyncssh
from dataclasses import dataclass
from typing import Tuple
from . import get_logger


@dataclass
class Connection:
    ip_address: str
    port: int
    ssh_connection: asyncssh.SSHClientConnection
    reader: asyncssh.SSHReader
    writer: asyncssh.SSHWriter
    errs: asyncssh.SSHReader

    @staticmethod
    def create(ip_address: str, port: int):
        connection = asyncio.get_event_loop().run_until_complete(
            asyncssh.connect(
                ip_address,
                port,
                username="kubih",
                password="lab123",
                known_hosts=None,
            )
        )
        writer, reader, errs = asyncio.get_event_loop().run_until_complete(
            connection.open_session(),
        )
        return Connection(ip_address, port, connection, reader, writer, errs)

    def send(self, msg):
        self.writer.write(msg)


@dataclass
class Notification:
    source: Tuple[str, int]
    stream: str
    payload: str


class Subscriber:
    def __init__(self):
        self.subscribtions = dict()
        self.register_stream("NETCONF")
        self._queue = asyncio.Queue()
        self.log = get_logger("notifications-subscriber")

    def register_stream(self, stream: str):
        self.subscribtions[stream] = list()
        self.log.debug(f"Registered {stream=}")

    def _establish_connection(self, ip_address: str, port: int):
        connection = Connection.create(ip_address, port)
        self._send_hello(connection)
        return connection

    def _send_hello(self, connection: Connection):
        hello = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            + '<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
            + "<nc:capabilities>"
            + "<nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability>"
            + "<nc:capability>urn:ietf:params:netconf:base:1.1</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:writable-running:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:candidate:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:startup:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:validate:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:xpath:1.0</nc:capability>"
            + "<nc:capability>urn:ietf:params:netconf:capability:notification:1.0</nc:capability>"
            # + "<nc:capability>urn:liberouter:params:netconf:capability:power-control:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:interleave:1.0</nc:capability>"
            # + "<nc:capability>urn:ietf:params:netconf:capability:with-defaults:1.0</nc:capability>"
            + "</nc:capabilities>"
            + "</nc:hello>"
        )
        hello_msg = util.to_message(hello)
        connection.send(hello_msg)

    def _send_create_subscription(self, connection: Connection, stream: str):
        uuid = uuid4()

        create_subscription = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            + f'<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:{uuid}">'
            + '<ns0:create-subscription xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0">'
            + f"<ns0:stream>{stream}</ns0:stream>"
            + "</ns0:create-subscription>"
            + "</nc:rpc>"
        )

        create_subscription_msg = util.to_message(create_subscription)
        connection.send(create_subscription_msg)

    def _send_close_session(self, connection: Connection):
        uuid = uuid4()
        close_session = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            + f'<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:{uuid}">'
            + "  <nc:close-session/>"
            + "</nc:rpc>"
        )
        close_session_msg = util.to_message(close_session)
        connection.send(close_session_msg)

    async def listen(self, stream: str, connection: Connection):
        while True:
            notification = await connection.reader.readuntil("]]>]]>")
            notification = Notification(
                (connection.ip_address, connection.port),
                stream,
                notification.removesuffix("]]>]]>"),
            )
            await self._queue.put(notification)

    async def notifications(self):
        while True:
            notification = await self._queue.get()
            self._queue.task_done()
            yield notification

    async def print_notifi(self):
        async for ele in self.notifications():
            self.log.debug(ele)

    def subscribe(self, ip_address, port, stream):
        if stream not in self.subscribtions:
            self.log.error(f"Stream={stream} is not registered!")
            return None
        connection = self._establish_connection(ip_address, port)
        self._send_create_subscription(connection, stream)

        self.subscribtions[stream].append(connection)
        self.log.info(f"Created subscription for {stream=} from source={(ip_address, port)}")
        loop = asyncio.get_event_loop()
        loop.create_task(self.listen(stream, connection))

    def unsubscribe(self, ip_address, port, stream):
        connections = self.subscribtions.get(stream, [])
        connections = list(
            filter(
                lambda x: x.ip_address == ip_address and x.port == port,
                connections[0],
            ),
        )
        if len(connections) >= 1:
            connection = connections[0]
            connection.ssh_connection.close()
        else:
            self.log.error("No such connection!")
