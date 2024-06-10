from .file_sharing import consumer as sharing
from .some_chat import consumer as chat

consumers = [
    sharing(),
    chat(),
]

__all__ = [
    consumers,
]
