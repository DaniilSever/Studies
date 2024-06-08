import asyncio
import nats
from nats.errors import TimeoutError

async def consumer():
    nc = await nats.connect("nats://demo.nats.io:4222")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    sub = await nc.subscribe("foo", cb=message_handler)
    await sub.unsubscribe(limit=2)
    sub = await nc.subscribe("bar")
    
    try:
        async for msg in sub.messages:
            print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
            await sub.unsubscribe()
    except Exception as e:
        pass

    await nc.drain()


if __name__ == '__main__':
    asyncio.run(consumer())