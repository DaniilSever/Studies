from .support import consumer as support_consumer
from .receive_dl import consumer as receive_dl_consumer

consumers = [
    support_consumer,
    receive_dl_consumer, 
]

__all__ = [consumers]