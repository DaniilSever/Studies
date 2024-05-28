from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from time import sleep
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

queue_name = "support"
routing_key = "help.*"

def consumer():
    cn = BlockingConnection(rmq_params)
    ch = cn.channel()
    ch.exchange_declare(exchange="topic_exchange", exchange_type="topic")

    def return_answer(method):
        message = f"Thank you for your message. I will help you as soon as possible."
        ch.basic_reject(
            exchange="topic_exchange",
            routing_key=routing_key[routing_key.find(".")+1:],
            body=message,
        )
        print(f" [support↑] Answer sent: '{message}'")


    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f" [support↓] Problem received: '{message}'")
        print(f" [support] Processing...")
        sleep(5)
        ch.basic_reject(delivery_tag = method.delivery_tag, requeue=False)
        print(f" [support↑] Answer sent: '{message}'")

    ch.queue_declare(queue=queue_name, durable=True, arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'dl',
    })
    ch.queue_bind(
        exchange="topic_exchange", queue=queue_name, routing_key=routing_key
    )
    ch.basic_consume(queue=queue_name, on_message_callback=callback)

    print(" [support] Waiting for messages. To exit press CTRL+C")
    ch.start_consuming()