from threading import Thread
from src import publishers

for publisher in publishers:
    Thread(target=publisher).start()
