import asyncio
import nats


async def consumer():

    nc = await nats.connect("nats://demo.nats.io:4222")

    js = nc.jetstream()

    await js.add_stream(name="My_Test_Stream", subjects=["test_subject"])


    psub = await js.pull_subscribe("test_subject", "psub")

    for _ in range(0, 10):
        msgs = await psub.fetch()
        for msg in msgs:
            await msg.ack()
            print(msg)


if __name__ == "__main__":
    asyncio.run(consumer())
