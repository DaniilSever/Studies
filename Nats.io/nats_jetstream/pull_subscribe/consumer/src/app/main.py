import asyncio
import nats


async def consumer():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="test", subjects=["test"])

    psub = await js.pull_subscribe("test", "psub")

    for _ in range(0, 10):
        msgs = await psub.fetch(1)
        for msg in msgs:
            await msg.ack()
            print(msg)


if __name__ == "__main__":
    asyncio.run(consumer())
