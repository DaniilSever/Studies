#!bin/bash

echo "Waiting for kafka"
while ! nc -z kafka 29092; do
    sleep 0.1
done
echo "Kafka is running"