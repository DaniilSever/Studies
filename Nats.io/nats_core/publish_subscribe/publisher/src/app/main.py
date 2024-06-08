import asyncio
import nats
from nats.errors import TimeoutError

async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")

    await nc.publish("foo", b'Hello')
    await nc.publish("foo", b'World')
    await nc.publish("foo", b'!!!!!')

    await nc.publish("bar", b'First')
    await nc.publish("bar", b'Second')


    async def help_request(msg):
        print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
        await nc.publish(msg.reply, b'I can help')

    sub = await nc.subscribe("help", "workers", help_request)
    
    try:
        response = await nc.request("help", b'help me', timeout=0.5)
        print("Received response: {message}".format(
            message=response.data.decode()))
    except TimeoutError:
        print("Request timed out")

    await sub.unsubscribe()

    await nc.drain()

if __name__ == '__main__':
    asyncio.run(publisher())