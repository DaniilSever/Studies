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
def first_send():
    connection = BlockingConnection(rmq_params)
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
                        routing_key='hello',
                        body='Hello World!')
    
    print(" [x] Sent 'Hello World!'")
    connection.close()