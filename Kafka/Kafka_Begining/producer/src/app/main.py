from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'kafka:9092'})

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

G = [str(i) for i in range(1, 10)]

for data in G:
    p.poll(0)
    
    p.produce('mytopic', data.encode('utf-8'), callback=delivery_report)

p.flush()