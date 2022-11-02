import os

import pika

credentials = pika.PlainCredentials('guest', 'guest')
rabbit_host = os.environ.get('RABBIT_HOST')
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, 5672, '/', credentials))
channel = connection.channel()


def produce(uid, service, message):
    channel.queue_declare(queue=service)

    channel.basic_publish(exchange='',
                          routing_key=service,
                          body=f'{{"uid": "{uid}", "service": "{service}", "message": "{message}"}}'.encode('utf-8'))
