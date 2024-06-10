import asyncio
import nats
from uuid import uuid4
from string import ascii_letters, digits, ascii_lowercase
from random import randint, choices
from nats.errors import TimeoutError


async def publisher():

    nc = await nats.connect("nats://demo.nats.io:4222")
    queue_group = "topic_nats"

    for _ in range(0, 10):
        check = randint(0, 1)
        match check:
            case 0:
                queue_group = "sharing."
                file_name = "".join(choices(ascii_letters + digits, k=8))
                file_extensions = [".txt", ".zip", ".pdf", ".doc", ".docx"]
                rand_file = file_name + file_extensions[randint(0, len(file_extensions)-1)]
                
                print(queue_group+rand_file, b"Test_File")
                await nc.publish(queue_group+rand_file, b"Test_File")
                await asyncio.sleep(0.5)

            case 1:
                queue_group = "chat."
                user_id = "".join(choices(ascii_lowercase, k=10))
                
                print(queue_group+user_id, b"Test_Message")
                await nc.publish(queue_group+user_id, b"Test_Message")
                await asyncio.sleep(0.5)


    await nc.drain()


if __name__ == "__main__":
    asyncio.run(publisher())
