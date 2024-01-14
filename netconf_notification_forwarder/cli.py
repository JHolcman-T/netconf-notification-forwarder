import argparse
import dataclasses
from enum import StrEnum, auto, unique
from ipaddress import ip_address
from . import version


parser = argparse.ArgumentParser(
    description="Simple NETCONF notifications forwarder that re-sends NETCONF notifications on another stream.",
    epilog="jakub-holcman.com",
)


@unique
class ArgNames(StrEnum):
    CONFIG_FILE = auto()
    LOG_LEVEL = auto()
    LOG_STYLE = auto()
    IP_ADDRESS = auto()
    PORT = auto()


@dataclasses.dataclass
class Args:
    """
    Substitute-class for Namespace class.
    Easier access to attributes (autocomplete).
    """

    config_file: str
    log_level: str
    log_style: str
    ip_address: str
    port: int


parser.add_argument(
    *[
        "-v",
        "--version",
    ],
    action="version",
    version=f"%(prog)s {version.__version__}",
)

parser.add_argument(
    *[
        "-c",
        "--config-file",
    ],
    dest=ArgNames.CONFIG_FILE,
    type=str,
    required=True,
    metavar="PATH",
    help="config file (json)",
)

parser.add_argument(
    *[
        "-ll",
        "--log-level",
    ],
    dest=ArgNames.LOG_LEVEL,
    type=str,
    choices=(
        "info",
        "debug",
    ),
    default="info",
)

parser.add_argument(
    *[
        "-ls",
        "--log-style",
    ],
    dest=ArgNames.LOG_STYLE,
    type=str,
    choices=(
        "raw",
        "pretty_raw",
        "xml",
        "pretty_xml",
        "json",
        "pretty_json",
    ),
    default="pretty_raw",
)

parser.add_argument(
    *[
        "-ip",
        "--ip-address",
    ],
    dest=ArgNames.IP_ADDRESS,
    type=ip_address,
    default="127.0.0.1",
)

parser.add_argument(
    *[
        "-p",
        "--port",
    ],
    dest=ArgNames.PORT,
    type=int,
    default=3333,
)


def get_arguments() -> Args:
    args = parser.parse_args()
    constructor_args = {arg.value: getattr(args, arg.value) for arg in ArgNames}
    return Args(**constructor_args)
