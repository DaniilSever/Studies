from string import ascii_letters, digits
from random import choices
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
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()

    user = "".join(choices(ascii_letters + digits, k=15))
    email = user + "@example.com"

    queue_name = "jivochat." + email
    routing_key = "help." + queue_name

    ch.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    def send_message(message):
        ch.basic_publish(
            exchange="topic_exchange", routing_key=routing_key, body=message
        )
        print(f" [jivochat↑] Message sent: '{message}'")

    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f" [jivochat↓] Message received: '{message}'")

    ch.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-message-ttl": 1000,
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dl",
        },
    )
    ch.queue_bind(exchange="topic_exchange", queue=queue_name, routing_key=queue_name)
    ch.basic_consume(queue=queue_name, on_message_callback=callback)

    send_message("I need help!...")

    print(f" [×jivochat×] User disconnected")
    cn.close()
