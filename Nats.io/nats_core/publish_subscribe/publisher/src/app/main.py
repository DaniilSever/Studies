import asyncio
import nats


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")
    queue_name = "fanout_nats"

    for _ in range(0, 10):
        await nc.publish(queue_name, b"Test_message")
        await asyncio.sleep(0.5)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
