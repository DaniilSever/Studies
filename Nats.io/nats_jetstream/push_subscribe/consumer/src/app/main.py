import asyncio
import nats


async def consumer():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="test", subjects=["test"])

    sub = await js.subscribe("test")
    msg = await sub.next_msg()
    await msg.ack()


if __name__ == "__main__":
    asyncio.run(consumer())
