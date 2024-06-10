from .some_consumer_1 import consumer as first_consumer
from .some_consumer_2 import consumer as second_consumer

consumers = [
    first_consumer(),
    second_consumer(),
]

__all__ = [
    consumers,
]
