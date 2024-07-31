import asyncio
import nats


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="test", subjects=["test"])

    for _ in range(0, 5):
        await js.publish("test", b"Test Message")
        await asyncio.sleep(0.5)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
