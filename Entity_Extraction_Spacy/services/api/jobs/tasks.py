import warnings
warnings.filterwarnings("ignore")
import json
import pika
import urllib.parse
from jsonmerge import merge
from services.api.core.msa_entity_extraction import entity_extraction
from services.api.jobs.config import celery_app
from services.api.core.MongoExtract import MongoDocLink
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

@celery_app.task()
def get_doc_links_async(doc):
    dl = MongoDocLink()
    host = doc["mongoDetails"]["host"]
    port = doc["mongoDetails"]["port"]
    username = doc["mongoDetails"]["username"]
    password = doc["mongoDetails"]["password"]
    sessionId = doc["sessionId"]
    print(host, port, username, password, sessionId)
    username = urllib.parse.quote_plus(username)
    password = urllib.parse.quote_plus(password)
    dl.link_process(host, port, username, password, sessionId)

@celery_app.task()
def get_msa_entities_async(doc):

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

        if doc["callBack"]["category"] == "MSA":
            logger.info("[{}] MSA file received for entities extraction".format(doc["callBack"]["fileName"]))
            text = doc['content']
            logger.info("The text received for file {} is - {}".format(doc["callBack"]["fileName"], text))
            logger.info("[{}] MSA Entities extraction Process started".format(doc["callBack"]["fileName"]))
            result = entity_extraction(doc["callBack"]["fileName"]).process(text)
            logger.info("[{}] MSA Entity Extraction Process completed".format(doc["callBack"]["fileName"]))

            # Success Response
            json2 = {"requestJson": {
                     "error": "false",
                     "errorMessage": "",
                     "firstParty": result.get('first_party'),
                     "secondParty": result.get('second_party'),
                     "effectiveDate": result.get('effective_date'),
                     "rebateInfoAvailable": result.get('rebate_table_flag'),
                     "payment": result.get('payment'),
                     "warranties": result.get('warranties'),
                     "termination": result.get('termination'),
                     "indemnification": result.get('indemnification'),
                     "callBack": {
                         "category": doc["callBack"]["category"],
                         "fileName": doc["callBack"]["fileName"],
                         "uniqueId": doc["callBack"]["uniqueId"]
                   },
                     "file_store": doc["file_store"]
                }}

            response = bytes(json.dumps(merge(json1, json2)), 'utf-8')

            logger.info("[{}] Entities extracted: {}".format(doc["callBack"]["fileName"], response))

        else:

            # Failure response
            json2 = {"requestJson": {
                                        "error": "true",
                                        "errorMessage": "Wrong document category",
                                        "callBack": {
                                                    "category": doc["callBack"]["category"],
                                                    "fileName": doc["callBack"]["fileName"],
                                                    "uniqueId": doc["callBack"]["uniqueId"]
                                                    },
                     "file_store": doc["file_store"]
                }}

            response = bytes(json.dumps(merge(json1, json2)), 'utf-8')
            logger.error("[{}] Entities extracted: {}".format(doc["callBack"]["fileName"], response))

    except Exception as ex:
        # Exception response
        logger.error('[{}] Exception raised - {}'.format(doc["callBack"]["fileName"], ex))

        json2 = {"requestJson": {
                                    "error": "true",
                                    "errorMessage": "Extraction failed",
                                    "callBack": {
                                                "category": doc["callBack"]["category"],
                                                "fileName": doc["callBack"]["fileName"],
                                                "uniqueId": doc["callBack"]["uniqueId"]
                                                },
                     "file_store": doc["file_store"]
            }}

        response = bytes(json.dumps(merge(json1, json2)), 'utf-8')

    try:
        credentials = pika.PlainCredentials(doc["queueDetails"]["userName"], doc["queueDetails"]["password"])
        connection = pika.BlockingConnection(pika.ConnectionParameters(doc["queueDetails"]["host"], doc["queueDetails"]["port"], '/', credentials))
        channel = connection.channel()
        channel.queue_declare(queue=doc["queueDetails"]["queueName"], durable='true')
        channel.basic_publish(exchange='', routing_key=doc["queueDetails"]["queueName"], body=response)
        logger.info("[{}] Response is posted back to the RabbitMQ - {}:{}/{}".format(doc["callBack"]["fileName"], doc["queueDetails"]["host"], doc["queueDetails"]["port"], doc["queueDetails"]["queueName"]))

    except Exception as ex:
        logger.error('[{}] Exception occurred while posting response back to RabbitMQ. Exception - {}'.format(doc["callBack"]["fileName"], ex))
