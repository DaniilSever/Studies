from .some_consumer_1 import direct_consumer as some_direct_consumer
from .some_consumer_2 import fanout_consumer as some_fanout_consumer
from .some_consumer_3 import topic_consumer as some_topic_consumer


consumers = [
    some_direct_consumer,
    some_fanout_consumer,
    some_topic_consumer,
]


__all__ = [consumers]
