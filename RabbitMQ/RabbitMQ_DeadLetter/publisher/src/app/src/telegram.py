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

queue_name = "telegram"
routing_key = "help.telegram"

def publisher():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()
    ch.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    def send_message(message):
        ch.basic_publish(
            exchange="topic_exchange", routing_key=routing_key, body=message
        )
        print(f" [telegram↑] Message sent: '{message}'")

    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f" [telegram↓] Message received: '{message}'")

    ch.queue_declare(queue=queue_name, durable=True)
    ch.queue_bind(
        exchange="topic_exchange", queue=queue_name, routing_key=queue_name
    )
    ch.basic_consume(queue=queue_name, on_message_callback=callback)

    send_message("I need help!...")

    ch.start_consuming()