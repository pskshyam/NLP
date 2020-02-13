import warnings
warnings.filterwarnings("ignore")
import urllib.parse
import json
import pika
import os
from bs4 import BeautifulSoup
from services.api.queue.queueListener import RabbitMQListener
from jsonmerge import merge
from services.api.core.classifier import document_classifier
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)


class ClassificationQueueListener:
    def __init__(self):
        """self.host ="clones-dev.southindia.cloudapp.azure.com"
        self.port = 5672
        self.username = "admin"
        self.password = "admin"
        self.doc_classification_queue = "ai.classification.inbound"
        self.doc_classification_exchange = "ai.classification.inbound"
        """
        self.host = os.environ.get("RABBIT_MQ_HOST")
        self.port = os.environ.get("RABBIT_MQ_PORT")
        self.username = os.environ.get("RABBIT_MQ_USERNAME")
        self.password = os.environ.get("RABBIT_MQ_PASSWORD")
        self.doc_classification_queue = os.environ.get("RABBIT_MQ_DOC_CLASSIFICATION_QUEUE")
        self.doc_classification_exchange = os.environ.get("RABBIT_MQ_DOC_CLASSIFICATION_EXCHANGE")
        

    def process_page_content(self, content):
        content = sorted(content, key=lambda k: k['page_no'])
        sorted_content = []
        for page in content:
            sorted_content.append(page["page_hocr"])
        """pages = []
        for file_content in sorted_content:
            soup = BeautifulSoup(file_content, 'html5lib')
            VALID_TAGS = ['div', 'p']
            for page in soup.findAll('div', attrs={'class': 'ocr_page'}):
                page_text = '<div class="page">'
                for area in page.findAll('div', attrs={'class': 'ocr_carea'}):
                    text = ' '.join([x for x in area.text.split()])
                    text = ' <p>' + text + '\n' + '</p> '
                    page_text += text
                page_text += "</div>"
                pages.append(page_text)
        return pages"""
        return sorted_content

    def check_html_file(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        isTika = soup.find('meta', attrs={'content': 'org.apache.tika.parser.pdf.PDFParser'})
        return isTika

    def process_pages(self, sorted_pages):
        isTika = self.check_html_file(sorted_pages[0])
        if isTika is not None:
            pages = self.processTikaFile(sorted_pages)
        else:
            pages = self.processTesseractFile(sorted_pages)
        return pages

    def processTikaFile(self, content):
        pages = []
        for p in content:
            soup = BeautifulSoup(p, 'html5lib')
            for page in soup.findAll('div', attrs={'class': 'page'}):
                paragraphs = []
                for x in page.find_all('p'):
                    paragraphs.append(' '.join([x for x in str(x).split()]))
                text = ' '.join([x for x in paragraphs])
                text = '<div class="page">' + text + "</div>"
                pages.append(text)
        return pages

    def processTesseractFile(self, content):
        pages = []
        for p in content:
            soup = BeautifulSoup(p, 'html5lib')
            for page in soup.findAll('div', attrs={'class': 'ocr_page'}):
                page_text = '<div class="page">'
                for area in page.findAll('div', attrs={'class': 'ocr_carea'}):
                    text = ' '.join([x for x in area.text.split()])
                    text = ' <p>' + text + '</p> '
                    page_text += text
                page_text += "</div>"
                pages.append(page_text)
        return pages

    def get_all_text_from_pages(self, filename, pages):
        text_list = []
        text = None

        try:
            for page in pages:
                soup = BeautifulSoup(page, 'html5lib')
                divpage = soup.find('div', attrs={'class': 'page'})
                text_list.append(divpage.text)
            text = " ".join(text_list)

        except Exception as ex:
            logger.error('[{}] Exception occurred in getting text from html pages - {}'.format(filename, ex))

        return text


    def get_classification(self, ch, method, properties, body):
        response = None
        doc = self.listener.convert_message_to_task_json(body)
        content = doc['content']
        filename = doc['callBack']['fileName']

        # prepare callback for response json
        keys = []
        values = []
        exclude_keys = ['category', 'fileName', 'uniqueId']
        for key, value in doc['callBack'].items():
            if (not (key in exclude_keys)):
                keys.append(key)
                values.append(value)
        json1 = dict(zip(keys, values))

        # Read header information from callback
        headers = {
            "content-type": "application/json",
            "Organization-key": doc["callBack"]["organizationId"]
        }

        try:


            if doc["header"]["requestType"] == "document_classification":

                #logger.info("[{}] file received for Document classification with request json - {}".format(filename, doc))
                logger.info("[{}] file received for Document classification".format(filename))
                pages = self.process_page_content(content)
                pages = self.process_pages(pages)
                text = self.get_all_text_from_pages(filename, pages)
                #logger.info("The text received for file {} is - {}".format(filename, text))
                logger.info("[{}] Converted html to text".format(filename))
                logger.info("[{}] Document classification Process started".format(filename))
                result = document_classifier(text, filename).classify()
                logger.info("[{}] Document classification Process completed".format(filename))

                # Success Response
                json2 = {"requestJson": {
                    "error": "false",
                    "errorMessage": "",
                    "category": result,
                    "callBack": {                      
                        "fileName": filename,
                        "uniqueId": doc["callBack"]["uniqueId"]
                    },
                    "file_store": doc["file_store"]
                }}
                
                response = bytes(json.dumps(merge(json1, json2)), 'utf-8')

                logger.info("[{}] Document classification result: {}".format(filename, response))

            else:
                # Failure response
                json2 = {"requestJson": {
                    "error": "true",
                    "errorMessage": "Wrong document category",
                    "callBack": {                        
                        "fileName": filename,
                        "uniqueId": doc["callBack"]["uniqueId"]
                    },
                    "file_store": doc["file_store"]
                }}

                response = bytes(json.dumps(merge(json1, json2)), 'utf-8')
                logger.error("[{}] Document classification result: {}".format(filename, response))

        except Exception as ex:
            # Exception response
            logger.error('[{}] Exception raised - {}'.format(filename, ex))

            json2 = {"requestJson": {
                "error": "true",
                "errorMessage": "Document classification failed",
                "callBack": {                   
                    "fileName": filename,
                    "uniqueId": doc["callBack"]["uniqueId"]
                },
                "file_store": doc["file_store"]
            }}

            response = bytes(json.dumps(merge(json1, json2)), 'utf-8')

        self.push_response_rabbit_mq(doc, response)

    def push_response_rabbit_mq(self, doc, response):
        try:
            credentials = pika.PlainCredentials(doc["queueDetails"]["userName"], doc["queueDetails"]["password"])
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(doc["queueDetails"]["host"], doc["queueDetails"]["port"], '/', credentials))
            channel = connection.channel()
            channel.queue_declare(queue=doc["queueDetails"]["queueName"], durable='true')
            channel.basic_publish(exchange='', routing_key=doc["queueDetails"]["queueName"], body=response)
            logger.info("[{}] Response is posted back to the RabbitMQ - {}:{}/{}".format(doc["callBack"]["fileName"],
                                                                                         doc["queueDetails"]["host"],
                                                                                         doc["queueDetails"]["port"],
                                                                                         doc["queueDetails"][
                                                                                             "queueName"]))

        except Exception as ex:
            logger.error('[{}] Exception occurred while posting response back to RabbitMQ. Exception - {}'.format(
                doc["callBack"]["fileName"], ex))

    def process_request(self):
        try:
            logger.info("Calling process request")
            self.listener = RabbitMQListener(host=self.host, port=self.port, username=self.username, password=self.password)
            self.listener.create_new_connection()
            self.listener.listen_queue(message_callback_classification=self.get_classification, doc_classification_queue=self.doc_classification_queue,
                                       doc_classification_exchange=self.doc_classification_exchange)
        except Exception as ex:
            logger.error('Exception occurred in listening to Document classification queue. Exception - {}'.format(ex))


def main():
    ql = ClassificationQueueListener()
    ql.process_request()


if __name__ == '__main__':
    main()

