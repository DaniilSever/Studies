import asyncio
import nats


async def consumer():
    
    nc = await nats.connect(
        servers=["nats://0.0.0.0:4222"]
        # servers=[
        #     "nats://172.30.0.2:4222",
        #     "nats://172.30.0.4:4222",
        #     "nats://172.30.0.3:4222"
        # ],
        # connect_timeout=10,
    )

    # nc = await nats.connect("nats://demo.nats.io:4222")
    js = nc.jetstream()

    sub = await js.subscribe("study-push_sub", ordered_consumer=True)
    data = bytearray()

    while True:
        try:
            msg = await sub.next_msg()
            data.extend(msg.data)
        except TimeoutError:
            break

    print(data.decode())

    await js.delete_stream(name="Study-Push_Sub")



if __name__ == "__main__":
    asyncio.run(consumer())
