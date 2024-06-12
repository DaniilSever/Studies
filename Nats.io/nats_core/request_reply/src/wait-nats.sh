#!bin/bash

echo "Waiting for nats"
while ! nc -z nats 6222; do
    sleep 0.1
done
echo "Nats is running"