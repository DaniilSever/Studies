import asyncio
import nats


async def consumer():

    nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    await js.add_stream(name="test", subjects=["test"])

    async def qsub_a(msg):
        print("QSUB A:", msg)
        await msg.ack()

    async def qsub_b(msg):
        print("QSUB B:", msg)
        await msg.ack()

    await js.subscribe("test", cb=qsub_a)
    await js.subscribe("test", cb=qsub_b)



if __name__ == "__main__":
    asyncio.run(consumer())
