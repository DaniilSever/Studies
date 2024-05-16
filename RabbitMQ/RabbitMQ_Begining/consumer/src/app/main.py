from threading import Thread
from src import consumers

for consumer in consumers:
    Thread(target=consumer).start()
