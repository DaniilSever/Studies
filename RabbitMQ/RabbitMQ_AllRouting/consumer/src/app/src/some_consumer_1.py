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
    heartbeat=30,
    virtual_host=cfg.RABBITMQ_VHOST,
)


def direct_consumer():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()

    ch.queue_declare(queue="direct_queue")

    def redirect_topic(file):
        ch.basic_publish(
            exchange="topic_exchange",
            routing_key=file[file.find(".") :],
            body=file,
        )
        print(f"\n [DC] Sent '{file}' to routing_key '{file[file.find("."):]}'")
        time.sleep(0.5)

    def callback(ch, method, properties, body):
        msg = body.decode("utf-8")
        if msg[msg.find(".") :] == ".mp4":
            redirect_topic(msg)
        print(f" [✔DC] Consumer 'Direct' heard: {msg}")

    ch.basic_consume(queue="direct_queue", on_message_callback=callback)

    print(" [*DC] Consumer 'Direct' waiting for messages. To exit press CTRL+C")
    ch.start_consuming()
