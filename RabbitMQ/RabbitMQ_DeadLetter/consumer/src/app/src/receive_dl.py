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

def consumer():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()
    ch.exchange_declare(exchange="dlx", exchange_type="topic")

    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f" [dl↓] DeadLetter heard: '{message}'")

    ch.queue_declare(queue="dl", durable=True)
    ch.queue_bind(
        exchange="dlx", queue="dl", routing_key="dl"
    )
    ch.basic_consume(queue="dl", on_message_callback=callback)

    print(" [dl] Waiting for messages. To exit press CTRL+C")
    ch.start_consuming()