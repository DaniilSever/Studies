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

queue_name = "Fanout_Bank"
routing_key = ""
total = 0


def fanout_consumer():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()
    ch.exchange_declare(exchange="fanout_exchange", exchange_type="fanout")

    def callback(ch, method, properties, body):
        global total
        message = body.decode("utf-8")
        total += int(message)
        print(f" [✔FC] Consumer '{queue_name}' heard: {total}")

    ch.queue_declare(queue=queue_name, durable=True)
    ch.queue_bind(exchange="fanout_exchange", queue=queue_name, routing_key=routing_key)
    ch.basic_consume(queue=queue_name, on_message_callback=callback)

    print(" [*FC] Consumer 'Fanout' waiting for messages. To exit press CTRL+C")
    ch.start_consuming()
