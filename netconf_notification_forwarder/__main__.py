from netconf_notification_forwarder.server import Server
from netconf_notification_forwarder.server import settings
import asyncio, sys, asyncssh
from netconf_notification_forwarder.notifications_subscriber import Subscriber

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    settings = settings.Settings.from_file(
        "C:\\Users\\kubih\\GitRepository\\netconf-notification-forwarder\\tests\\stream-routes.json"
    )
    server = Server("127.0.0.1", 3333, settings)
    try:
        loop.create_task(server.send2())
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
