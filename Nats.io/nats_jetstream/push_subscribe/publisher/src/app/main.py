import asyncio
import nats


async def publisher():

    nc = await nats.connect(
        # servers=["nats://localhosh:4222"],
        servers=[
            "nats://172.30.0.2:4222",
            "nats://172.30.0.4:4222",
            "nats://172.30.0.3:4222"
        ],
        connect_timeout=20000,
    )

    js = nc.jetstream()


    await js.add_stream(name="Study-Push_Sub", subjects=["study-push_sub"])

    for i in range(0, 10):
        ack = await js.publish("study-push_sub", f"Test Message: {i}".encode())
        print(ack)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
