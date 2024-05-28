#!bin/bash

while ! nc -z rabbitmq 5672; do
    sleep 0.5
done