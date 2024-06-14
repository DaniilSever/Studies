import asyncio
import nats


async def consumer():

    nc = await nats.connect(servers=[
        "nats://172.30.0.2:4222",
        "nats://172.30.0.3:4222",
        "nats://172.30.0.4:4222",
    ])

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



if __name__ == "__main__":
    asyncio.run(consumer())
