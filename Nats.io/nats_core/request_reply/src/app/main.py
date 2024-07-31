import asyncio
import nats
from uuid import uuid4
from string import ascii_letters, digits
from random import randint, choices
from nats.errors import TimeoutError


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")

    async def support_request(msg):
        print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
        await nc.publish(msg.reply, b"I can help")

    queue_name = "support.*"
    sub = await nc.subscribe(queue_name, cb=support_request)

    try:
        for _ in range(0, 10):
            queue_group = "support."
            user_id = str(uuid4())

            response = await nc.request(
                queue_group + user_id, b"Help Me!!", timeout=0.5
            )
            print("Received response: {message}".format(message=response.data.decode()))
            await asyncio.sleep(0.5)

    except Exception as e:
        print(str(e))
    finally:
        await sub.unsubscribe()
        await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
