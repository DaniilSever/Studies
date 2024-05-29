import smtplib
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

    def send_email(email, message): 
        # smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        # smtpObj.starttls()
        # smtpObj.login('someaddress@gmail.com','somepassword')
        # smtpObj.sendmail("someaddress@gmail.com", email, message)
        # smtpObj.quit()
        print(f" [dl↑] Message sent to {email} ")
        
    def callback(ch, method, properties, body):
        message = body.decode("utf-8")
        print(f" [dl↓] DeadLetter heard: '{message}'")

        print(" [dl] The message will be delivered to your e-mail")
        routing_key = properties.headers["x-death"][0]["routing-keys"][0]

        send_email(routing_key[routing_key.find(".")+1:], message)



    ch.queue_declare(queue="dl", durable=True)
    ch.queue_bind(exchange="dlx", queue="dl", routing_key="dl")
    ch.basic_consume(queue="dl", on_message_callback=callback)

    print(" [dl] Waiting for messages. To exit press CTRL+C")
    ch.start_consuming()
