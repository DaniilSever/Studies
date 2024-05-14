from .first_consumer import consumer as first_consumer
from .second_consumer import consumer as second_consumer

consumers = [
    first_consumer,
    second_consumer,
]


__all__ = [
    consumers
]