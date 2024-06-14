import asyncio
import nats


async def publisher():

    nc = await nats.connect(servers=[
        "nats://172.30.0.2:4222",
        "nats://172.30.0.3:4222",
        "nats://172.30.0.4:4222"
    ],)

    # nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    # await js.delete_stream(name="Study-Push_Sub")

    await js.add_stream(name="Study-Push_Sub", subjects=["study-push_sub"])

    for i in range(0, 10):
        ack = await js.publish("study-push_sub", f"Test Message: {i}".encode())
        print(ack)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
