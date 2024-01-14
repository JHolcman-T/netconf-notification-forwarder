from netconf_notification_forwarder.server import Server
from netconf_notification_forwarder.settings import Settings
from netconf_notification_forwarder.logger import logger
import asyncio, sys, asyncssh
from ipaddress import IPv4Address, IPv6Address
from typing import Union


def start(
    ip_address: Union[str, IPv4Address, IPv6Address] = "127.0.0.1",
    port: int = 3333,
    logging_level=None,
    logging_style=None,
    settings_file_path=None,
):
    # Loop stuff
    loop = asyncio.get_event_loop()

    # Launch stuff
    if settings_file_path:
        settings = Settings.from_file(settings_file_path)
    else:
        settings = None
    if logging_style:
        logger.set_style(logging_style)
    if logging_level:
        logger.set_level(logging_level)
    server = Server(
        str(ip_address),  # ip address must be cast to string type!
        port,
        settings,
    )

    # Loop stuff
    try:
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
