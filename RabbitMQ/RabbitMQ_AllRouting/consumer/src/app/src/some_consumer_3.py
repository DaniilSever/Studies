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

queue_name = "mp4_files"
routing_key = "*.mp4"


def topic_consumer():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()
    ch.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    def callback(ch, method, properties, body):
        global total
        message = body.decode('utf-8')
        print(f" [✔TC] Consumer heard file .mp4: {message}")

    ch.queue_declare(queue=queue_name, durable=True)
    ch.queue_bind(exchange="topic_exchange", queue=queue_name, routing_key=routing_key)
    ch.basic_consume(queue=queue_name, on_message_callback=callback)

    print(" [*TC] Consumer 'Topic' waiting for messages. To exit press CTRL+C")
    ch.start_consuming()