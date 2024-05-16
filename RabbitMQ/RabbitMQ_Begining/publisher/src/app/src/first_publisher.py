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
    virtual_host=cfg.RABBITMQ_VHOST,
    heartbeat=30,
)


def publisher():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()

    messages = [str(item) for item in range(10)]

    channel.queue_declare(queue="test")

    for message in messages:
        channel.basic_publish(exchange="", routing_key="test", body=message)
        print(f"\n [x] Sent '{message}'")
        time.sleep(0.5)

    connection.close()
