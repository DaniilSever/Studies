#!bin/bash

echo "Waiting for rabbitmq"
while ! nc -z rabbitmq 5672; do
    sleep 0.5
done
echo "RabbitMQ is running"