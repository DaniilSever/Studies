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

queue_name = "txt_files"
routing_key = "*.txt"


def consumer():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()
    channel.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    def callback(ch, method, properties, body):
        order_date = body.decode("utf-8")
        print(f" [x] Consumer heard file .txt: {order_date}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange="topic_exchange", queue=queue_name, routing_key=routing_key
    )
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print(" [*] Consumer 1 waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
