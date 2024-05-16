import time
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

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
    channel.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    messages = [str(item) for item in range(10)]

    for message in messages:
        channel.basic_publish(
            exchange="topic_exchange",
            routing_key="list.txt",
            body=message,
        )
        print(f" [x] Sent '{message}' to routing_key '.txt'")
        time.sleep(0.5)

    for message in messages:
        channel.basic_publish(
            exchange="topic_exchange",
            routing_key="movie.mp4",
            body=message,
        )
        print(f" [x] Sent '{message}' to routing_key '.mp4'")
        time.sleep(0.5)

    connection.close()
