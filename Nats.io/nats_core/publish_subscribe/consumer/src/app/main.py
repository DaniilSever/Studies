import asyncio
from threading import Thread
from src import consumers

try:
    for consumer in consumers:
        Thread(target=asyncio.run(consumer)).start()

except Exception as e:
    print(str(e))
