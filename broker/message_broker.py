
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


def produce(uid, service, message):
    channel.queue_declare(queue=service)

    channel.basic_publish(exchange='',
                          routing_key=service,
                          body=f'{{"uid": "{uid}", "service": "{service}", "message": "{message}"}}'.encode('utf-8'))
