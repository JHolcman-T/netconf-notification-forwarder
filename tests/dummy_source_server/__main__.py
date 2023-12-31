from tests.dummy_source_server.server import Server
import asyncio, sys, asyncssh

if __name__ == "__main__":
    print(f"Test: {__file__}")
    loop = asyncio.get_event_loop()
    server = Server("127.0.0.1", 2222)
    server.register_streams(
        [
            "NETCONF",
            "S1",
            "S2",
            "S3",
            "MULTICAST",
        ],
    )
    try:
        loop.create_task(server.send())
        loop.run_until_complete(server.start())
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
