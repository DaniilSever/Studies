import sys, os
from app import consumers, publishers

try:
    for publisher in publishers:
        publisher()
        
    for consumer in consumers:
        consumer()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
