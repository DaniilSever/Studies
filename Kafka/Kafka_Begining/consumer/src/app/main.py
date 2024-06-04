from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'testgroup',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['testtopic'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        break

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()