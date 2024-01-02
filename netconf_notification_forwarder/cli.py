import argparse
import dataclasses
from enum import StrEnum, auto, unique
from . import version


parser = argparse.ArgumentParser(
    description="Simple NETCONF notifications forwarder that re-sends NETCONF notifications on another stream.",
    epilog="jakub-holcman.com",
)


@unique
class ArgNames(StrEnum):
    CONFIG_FILE = auto()


@dataclasses.dataclass
class Args:
    """
    Substitute-class for Namespace class.
    Easier access to attributes (autocomplete).
    """

    config_file: str


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


def get_arguments() -> Args:
    args = parser.parse_args()
    constructor_args = {arg.value: getattr(args, arg.value) for arg in ArgNames}
    return Args(**constructor_args)
