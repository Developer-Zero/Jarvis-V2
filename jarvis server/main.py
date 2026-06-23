import asyncio

from transport.server import Server


async def main() -> None:
    server = Server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
