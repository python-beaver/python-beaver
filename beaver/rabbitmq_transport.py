import os
import datetime
import pika

import beaver.transport


class RabbitmqTransport(beaver.transport.Transport):

    def __init__(self, configfile):
        super(RabbitmqTransport, self).__init__(configfile)

        # Create our connection object
        rabbitmq_address = os.environ.get("RABBITMQ_HOST", "localhost")
        rabbitmq_port    = os.environ.get("RABBITMQ_PORT", 5672)
        rabbitmq_vhost   = os.environ.get("RABBITMQ_VHOST", "/")
        rabbitmq_user    = os.environ.get("RABBITMQ_USERNAME", 'guest')
        rabbitmq_pass    = os.environ.get("RABBITMQ_PASSWORD", 'guest')
        rabbitmq_queue   = os.environ.get("RABBITMQ_QUEUE", 'logstash-queue')
        self.rabbitmq_key      = os.environ.get("RABBITMQ_KEY", 'logstash-key')
        self.rabbitmq_exchange = os.environ.get("RABBITMQ_EXCHANGE", 'logstash-exchange')

        # Setup RabbitMQ connection
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
        self.connection = pika.adapters.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare RabbitMQ queue and bindings
        self.channel.queue_declare(queue=rabbitmq_queue)
        self.channel.exchange_declare(
            exchange=self.rabbitmq_exchange,
            type='direct'
        )
        self.channel.queue_bind(
            exchange=self.rabbitmq_exchange,
            queue=rabbitmq_queue,
            routing_key=self.rabbitmq_key
        )

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().isoformat()
        for line in lines:
            self.channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_key,
                body=self.format(filename, timestamp, line),
                properties=pika.BasicProperties(
                    content_type="text/json",
                    delivery_mode=1
                )
            )

    def interrupt(self):
        self.connection.close()

    def unhandled(self):
        return True
