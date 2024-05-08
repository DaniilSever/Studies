from .publisher.publisher import first_send
from .consumer.consumer import main

publishers = [
    first_send,
]

consumers = [
    main,
]


__all__ = [
    publishers,
    consumers,
]
