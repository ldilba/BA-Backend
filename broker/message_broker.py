import json
import os

import pika

from routes import routes

credentials = pika.PlainCredentials('guest', 'guest')
rabbit_host = os.environ.get('RABBIT_HOST')


def produce(uid, service, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, 5672, '/', credentials))
    channel = connection.channel()
    channel.queue_declare(queue=service)

    channel.basic_publish(exchange='',
                          routing_key=service,
                          body=f'{{"uid": "{uid}", "service": "{service}", "message": "{message}"}}'.encode('utf-8'))
    channel.close()
    connection.close()


def callback(ch, method, properties, body: bytes):
    print(body.decode('utf-8'))
    received = json.loads(body.decode('utf-8'))
    routes.receive(received)


def receive():
    credentials = pika.PlainCredentials('guest', 'guest')
    rabbit_host = os.environ.get('RABBIT_HOST')
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, 5672, '/', credentials))
    channel = connection.channel()

    channel.queue_declare(queue='response-text-similarity')

    channel.basic_consume(queue='response-text-similarity',
                          auto_ack=True,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
