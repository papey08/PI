import asyncio

from nats_server import NatsServer

async def main():
    await NatsServer("nats://localhost:4222", "secret").run()

if __name__ == "__main__":
    asyncio.run(main())
