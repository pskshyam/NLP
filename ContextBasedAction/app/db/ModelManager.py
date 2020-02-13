from app.db.MongoManager import  MongoConnection
from util.config.idl_config import idl_config
import logging

logger = logging.getLogger(__name__)

class DLManager():

    def __init__(self, database, collection):
        self.connector = MongoConnection(database = database, collection = collection)

    def raise_exception(self, msg):
        """

        :param msg:
        :return:
        """
        raise Exception(msg)

    def update(self, query, document):
        """
        :param query:
        :param document:
        :return:
        """

        self.connector.update_document(query, document)

    def create(self, document):
        """
               :param document:
               :param options:
               :return:
               """
        logger.info("creating document", extra = {'document': document})

        self.connector.create_document(document)

    def get_document(self, field, value):
        """

        :param model_name:
        :return:
        """
        query = {
            field:value
        }
        model = self.connector.find_document_by_id(query)
        return model

    def get_all_documents(self):
        """

        :return:
        """

        documents = [doc for doc in self.connector.get_docs_collection()]
        return  documents



class ModelInfoManager(DLManager):

    STATUS_PREDICTION_INIT = "prediction_initialized"
    STATUS_PREDICTION_FAILED = "prediction_failed"
    STATUS_PREDICTION_SUCCESS = "prediction_success"
    STATUS_UNKNOWN = "unknown"
    mongo_db_name = idl_config.mongo_db_name
    mongo_collection_name = idl_config.mongo_db_model_info_collection

    def __init__(self):
        DLManager.__init__(self, database = self.mongo_db_name, collection = self.mongo_collection_name)




    def service_exists(self, service_id):
        """

        :return: Boolean
        """
        model = self.get_document("service_id",service_id)
        return True if model else False

    def get_status(self, service_id):
        """

        :param service_id:
        :return: response
        """
        service = self.get_document("service_id", service_id)
        if service:
            response = {
                "status": service['prediction_status'],
                "status_message": service['prediction_status_message']
            }
            return response
        else:
            self.raise_exception("service {0} not found in collection {1} ".format(service_id, self.mongo_collection_name))

    def get_prediction_value(self, service_id ):
        """

        :param service_id:
        :return: prediction value
        """
        service = self.get_document("service_id", service_id)

        if service:
            if "prediction" in service.keys():
                response = {
                    "prediction": service['prediction'],
                }
                return response
            else:
                self.raise_exception("Prediction service: {} is not ready. ".format(service_id))

        else:
            self.raise_exception("service {0} not found in collection {1} ".format(service_id, self.mongo_collection_name))

