import time
from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from .config import get_config

cfg = get_config()

credentials = PlainCredentials(cfg.RABBITMQ_USER, cfg.RABBITMQ_PASSWORD)

rmq_params = ConnectionParameters(
    host=cfg.RABBITMQ_HOST,
    port=cfg.RABBITMQ_PORT,
    credentials=credentials,
    heartbeat=30,
    virtual_host=cfg.RABBITMQ_VHOST,
)


def publisher():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()

    msg = [
        "Hello World!",
        "Hello",
        "World",
        "Hello World!",
        "Hello",
        "World",
        "Hello World!",
        "TEST",
        "Hello",
        "Direct Publisher close",
        "movie.mp4"
    ]

    ch.queue_declare(queue="direct_queue")

    for message in msg:
        ch.basic_publish(exchange="", routing_key="direct_queue", body=message)
        print(f"\n [DP] Sent '{message}'")
        time.sleep(0.5)

    cn.close()
