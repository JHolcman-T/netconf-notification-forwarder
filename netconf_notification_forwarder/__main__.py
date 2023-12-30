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
    # server.register_streams(
    #     [
    #         "TEST-1",
    #         "TEST-2",
    #         "TEST-3",
    #     ],
    # )
    # server.notifications_subscriber.subscribe("127.0.0.1", 2222, "NETCONF")
    # server.notifications_subscriber.subscribe("127.0.0.1", 2222, "TEST-1")
    # server.notifications_subscriber.subscribe("127.0.0.1", 2222, "TEST-2")
    # server.notifications_subscriber.subscribe("127.0.0.1", 2222, "TEST-3")
    try:
        loop.create_task(server.send2())
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
