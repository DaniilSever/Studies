import asyncio
import nats


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="test", subjects=["test"])

    for i in range(0, 10):
        await js.publish("test", f"Test Message: {i}".encode())

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
