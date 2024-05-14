from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from .config import get_config

cfg = get_config()

credentials = PlainCredentials(
    cfg.RABBITMQ_USER, 
    cfg.RABBITMQ_PASSWORD
)

rmq_params = ConnectionParameters(
    host=cfg.RABBITMQ_HOST,
    port=cfg.RABBITMQ_PORT,
    credentials=credentials,
    virtual_host=cfg.RABBITMQ_VHOST,
    heartbeat=30
)

def consumer():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()

    channel.queue_declare(queue='test')

    def callback(ch, method, properties, body):
        print(f" [x] Consumer 2 listening message: {body}")

    channel.basic_consume(queue='test',
                            on_message_callback=callback,
                            auto_ack=True)

    print(' [*] Consumer 2 aiting for messages. To exit press CTRL+C')
    channel.start_consuming()
