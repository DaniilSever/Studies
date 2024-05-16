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

queue_name = "taxes"
routing_key = ""
taxes = 0


def consumer():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()
    channel.exchange_declare(exchange="fanout_exchange", exchange_type="fanout")

    def callback(ch, method, properties, body):
        global taxes
        message = body.decode("utf-8")
        taxes += round(int(message) * 0.01, 2)
        print(f" [✓] Consumer {queue_name} heard: {taxes}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange="fanout_exchange", queue=queue_name, routing_key=routing_key
    )
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print(" [*] Consumer 'Taxes' waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
