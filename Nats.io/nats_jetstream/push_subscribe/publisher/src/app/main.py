import asyncio
import nats


async def publisher():

    nc = await nats.connect("nats://0.0.0.0:4222")

    # nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    # print(await js.streams_info())
    # await js.delete_stream(name="Study-Push_Sub")

    await js.add_stream(name="Study-Push_Sub", subjects=["study-push_sub"])

    for i in range(0, 10):
        ack = await js.publish("study-push_sub", f"Test Message: {i}".encode())
        print(ack)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
