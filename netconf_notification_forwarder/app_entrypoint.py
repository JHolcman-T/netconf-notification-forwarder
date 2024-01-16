from netconf_notification_forwarder.server import Server
from netconf_notification_forwarder.settings import Settings
from netconf_notification_forwarder.logger import logger
import asyncio, sys, asyncssh
from ipaddress import IPv4Address, IPv6Address
from typing import Union
from pathlib import Path


def start(
    ip_address: Union[str, IPv4Address, IPv6Address] = "127.0.0.1",
    port: int = 3333,
    logging_level=None,
    logging_style=None,
    settings_file_path=None,
    host_key: Path = None,
):
    # Loop stuff
    loop = asyncio.get_event_loop()

    # Validate stuff
    if host_key:
        if host_key.is_file() is False:
            print(f"Host key path={host_key} is not a file!", file=sys.stderr)
            exit(-1)
    else:
        print(f"Host key is not set!", file=sys.stderr)
        exit(-1)

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
        ipaddress=str(ip_address),  # ip address must be cast to string type!
        port=port,
        settings=settings,
        host_key=host_key,
    )

    # Loop stuff
    try:
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
