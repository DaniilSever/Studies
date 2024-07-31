import asyncio
import nats


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="My_Test_Stream", subjects=["test_subject"])

    for i in range(0, 10):
        await js.publish("test_subject", f"Test Message: {i}".encode())
        await asyncio.sleep(0.5)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
