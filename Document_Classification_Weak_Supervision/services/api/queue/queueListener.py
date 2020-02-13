import pika
import json
from services.api.common.logger import set_up_logging

logger = set_up_logging(__name__)
import warnings

warnings.filterwarnings("ignore")


class RabbitMQListener:
    """ Listener class for RabbitMQ.
    """
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 5672
    DEFAULT_USERNAME = 'guest'
    DEFAULT_PASSWORD = 'guest'
    DEFAULT_HEARTBEAT_TIMEOUT = 60
    DEFAULT_SLEEP_DURATION = 120
    DEFAULT_PREFETCH_COUNT = 1
    DEFAULT_REQUEUE = False
    DEFAULT_AUTO_ACK = True

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD,
                 heart_beat=DEFAULT_HEARTBEAT_TIMEOUT,
                 prefetch_count=DEFAULT_PREFETCH_COUNT,
                 requeue=DEFAULT_REQUEUE,
                 auto_ack=DEFAULT_AUTO_ACK):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.heart_beat = heart_beat
        self.prefetch_count = prefetch_count
        self.requeue = requeue
        self.auto_ack = auto_ack

    def create_new_connection(self):
        """Creates a new rabbitMQ connection with the configurations specified
        in the config file.
        """
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            kwargs = {"host": self.host, "port": self.port, "credentials": credentials,
                      "heartbeat": self.heart_beat}
            print(kwargs)
            parameters = pika.ConnectionParameters(**kwargs)
            self.connection = pika.BlockingConnection(parameters)

        except Exception as ex:
            print(ex)
            logger.error(
                "Failed to connect RabbitMQ with host - {}, port - {}, username - {}, password - {}, exception - {}".format(
                    self.host, self.port, self.username, self.password, ex))

    def convert_message_to_task_json(self, body):
        """Convert queue body message to json.

        Arguments are
        * body: a byte object

        Returns: a json object
        """
        task_json = None
        try:
            json_str = body.decode("utf-8")
            task_json = json.loads(json_str)
        except Exception as ex:
            # print(ex)
            logger.exception(ex)
        return task_json

    def listen_queue(self, message_callback_classification, doc_classification_queue, doc_classification_exchange):
        """To enter a never-ending loop that waits for data and runs callbacks whenever necessary.
        """

        try:

            channel = self.connection.channel()

            # channel.queue_declare(queue=self.queue_name)
            # channel.basic_qos(prefetch_count=self.prefetch_count)
            channel.queue_bind(exchange=doc_classification_exchange, queue=doc_classification_queue, routing_key=doc_classification_queue)
            channel.basic_consume(queue=doc_classification_queue, on_message_callback=message_callback_classification,
                                  auto_ack=self.auto_ack)

            channel.start_consuming()
            logger.info("Connect established to RabbitMQ")
            logger.info("#####################")
            logger.info("Application is ready")
            logger.info("#####################")
        except Exception as ex:
            logger.error(
                "Failed to connect consume the messages")

    def sleep(self, duration=DEFAULT_SLEEP_DURATION):
        """A safer way to sleep. The connection will "sleep" or block the number of seconds.
        specified in duration in small intervals.

        Arguments are
        * duration: int Time to sleep in seconds
        """
        self.connection.sleep(duration)

    def close_connection(self):
        """Function to close current connection.
        """
        self.connection.close()
