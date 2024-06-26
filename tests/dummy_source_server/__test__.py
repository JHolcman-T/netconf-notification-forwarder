from tests.dummy_source_server.server import Server
import asyncio, sys, asyncssh

if __name__ == "__main__":
    print(f"Test: {__file__}")
    loop = asyncio.get_event_loop()
    source_streams = [
        [
            "NETCONF",
            "S1",
        ],
        [
            "NETCONF",
            "S1",
        ],
        [
            "NETCONF",
            "S2",
        ],
        [
            "S3",
            "MULTICAST",
        ],
    ]
    server_instances = list()
    for index, streams in enumerate(source_streams, 1):
        ip_address = f"127.0.0.{index}"
        port = 2222
        print(f"Server-{index}: {ip_address=}, {port=}")

        server = Server(ip_address, port)
        server.register_streams(streams)
        server_instances.append(server)
    try:
        loop.run_until_complete(
            asyncio.gather(*[server.start() for server in server_instances]),
        )
    except (OSError, asyncssh.Error, KeyboardInterrupt) as exc:
        sys.exit(f"Error: {exc}")
    loop.run_forever()
