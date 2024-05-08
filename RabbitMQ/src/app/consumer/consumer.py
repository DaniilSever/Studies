import os
from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    URLParameters,
)

url_rmq_params = URLParameters('amqp://rmuser:rmpassword@215.21.0.54:15672/%2F')
url_params = URLParameters(os.environ['AMQP_URL'])
credentials = PlainCredentials('rmuser', 'rmpassword')
rmq_params = ConnectionParameters(
    host="215.21.0.54",
    port=15672,
    credentials=credentials,
    heartbeat=30
)

def main():
    connection = URLParameters(url_params)
    channel = connection.channel()

    channel.queue_declare(queue='hello', durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(callback,
                          queue='hello',
                          on_message_callback=callback,
                          auto_ack=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

