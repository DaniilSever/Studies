import time
from random import randrange
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

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
    ch.exchange_declare(exchange="fanout_exchange", exchange_type="fanout")

    messages = [str(randrange(100, 10000)) for i in range(10)]

    for message in messages:
        ch.basic_publish(
            exchange="fanout_exchange",
            routing_key="",
            body=message,
        )
        print(f"\n [FP] Sent '{message}'")
        time.sleep(0.5)

    cn.close()
