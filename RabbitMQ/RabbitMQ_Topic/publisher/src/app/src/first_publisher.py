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

    file_list = [
        "log_1.txt",
        "movie_1.mp4",
        "log_2.txt",
        "movie_2.mp4",
        "log_3.txt",
        "movie_3.mp4",
        "log_4.txt",
        "movie_4.mp4",
        "log_5.txt",
        "movie_5.mp4",
    ]

    for file in file_list:
        channel.basic_publish(
            exchange="topic_exchange",
            routing_key=file[file.find(".") :],
            body=file,
        )
        print(f"\n [x] Sent '{file}' to routing_key '{file[file.find("."):]}'")
        time.sleep(0.5)

    connection.close()
