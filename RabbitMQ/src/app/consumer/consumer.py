import os
from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    URLParameters,
)

credentials = PlainCredentials('rmuser', 'rmpassword')
rmq_params = ConnectionParameters(
    host="215.21.0.54",
    port=5672,
    credentials=credentials,
    heartbeat=30
)

def main():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue='hello',
                          on_message_callback=callback,
                          auto_ack=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

