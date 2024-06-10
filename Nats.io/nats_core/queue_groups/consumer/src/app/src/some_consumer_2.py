import nats


async def consumer():
    nc = await nats.connect("nats://demo.nats.io:4222")
    queue_name = "fanout_nats"
    sub = await nc.subscribe(queue_name)

    try:
        async for msg in sub.messages:
            print(
                f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}"
            )
    except Exception as e:
        print(str(e))
    finally:
        await sub.unsubscribe()
        await nc.drain()
