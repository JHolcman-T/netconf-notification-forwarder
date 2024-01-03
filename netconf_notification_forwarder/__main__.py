from netconf_notification_forwarder.server import Server
from netconf_notification_forwarder.server import settings
import netconf_notification_forwarder.logger.logger
import asyncio, sys, asyncssh
import netconf_notification_forwarder.cli as cli

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    arguments = cli.get_arguments()
    print(arguments)
    settings = settings.Settings.from_file(arguments.config_file)
    server = Server("127.0.0.1", 3333, settings)
    try:
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
