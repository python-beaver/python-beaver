import os
import ujson as json
import socket
import datetime
import pika

import beaver.transport

class RabbitmqTransport(beaver.transport.Transport):

    def __init__(self):
        # Create our connection object
        rabbitmq_address = os.environ.get("RABBITMQ_HOST", "localhost")
        rabbitmq_port    = os.environ.get("RABBITMQ_PORT", 5672)
        rabbitmq_vhost   = os.environ.get("RABBITMQ_VHOST", "/")
        rabbitmq_user    = os.environ.get("RABBITMQ_USERNAME", 'guest')
        rabbitmq_pass    = os.environ.get("RABBITMQ_PASSWORD", 'guest')
        self.rabbitmq_exchange = os.environ.get("RABBITMQ_EXCHANGE", 'logstash-exchange')
        rabbitmq_queue    = os.environ.get("RABBITMQ_QUEUE", 'logstash-queue')

        credentials = pika.PlainCredentials(
            rabbitmq_user,
            rabbitmq_pass
        )
        parameters = pika.connection.ConnectionParameters(
            credentials=credentials,
            host=rabbitmq_address,
            port=rabbitmq_port,
            virtual_host=rabbitmq_vhost
        )
        # Setup RabbitMQ connection
        self.connection = pika.adapters.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=rabbitmq_queue)
        self.channel.exchange_declare(
            exchange=self.rabbitmq_exchange,
            type='fanout'
        )
        self.channel.queue_bind(
            exchange=self.rabbitmq_exchange,
            queue=rabbitmq_queue
        )

        self.current_host = socket.gethostname()


    def callback(self, filename, lines):
        timestamp = datetime.datetime.now().isoformat()
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
            self.channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key='',
                body=json_msg,
                properties=pika.BasicProperties(
                    content_type="text/json",
                    delivery_mode=1
                )
            )


    def interrupt(self):
        self.connection.close()


    def unhandled(self):
        return True
