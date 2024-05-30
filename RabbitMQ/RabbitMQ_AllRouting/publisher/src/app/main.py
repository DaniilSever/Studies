from threading import Thread
from src import publishers
from time import sleep

for publisher in publishers:
    Thread(target=publisher).start()
    sleep(10)
