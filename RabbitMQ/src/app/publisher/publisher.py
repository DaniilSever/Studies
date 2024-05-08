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
def first_send():
    connection = BlockingConnection(url_params)
    channel = connection.channel()

    channel.queue_declare(queue='hello', durable=True)

    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body='Hello World!')
    
    print(" [x] Sent 'Hello World!'")
    connection.close()