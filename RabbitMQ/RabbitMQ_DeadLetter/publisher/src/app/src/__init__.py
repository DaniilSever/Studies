from .telegram import publisher as telegram_publisher
from .jivochat import publisher as jivochat_publisher

publishers = [
    telegram_publisher,
    jivochat_publisher,
]

__all__ = [publishers]
