from pymongo import MongoClient
from util.config.idl_config import idl_config
import logging

logger = logging.getLogger(__name__)


class MongoConnection():

    mongo_host = idl_config.mongo_db_host
    mongo_port = idl_config.mongo_db_port
    mongo_user = idl_config.mongo_db_user
    mongo_password = idl_config.mongo_db_password
    mongo_db_model_info_collection = idl_config.mongo_db_model_info_collection
    mongo_auth_enabled = idl_config.mongo_auth_enabled
    mongo_auth_db = idl_config.mongo_auth_db

    def __init__(self, database, collection):
        self.client = self.connect_to_mongodb()
        self.mongo_db_name = database
        self.mongo_collection_name = collection
        self.db = self.get_db(database)
        self.collection = self.get_collection(collection)

    def connect_to_mongodb(self):
        """

        :return:
        """
        client = MongoClient(self.mongo_host, self.mongo_port)

        if self.mongo_auth_enabled:
            logger.info("Auth is enabled for mongo and trying to authenticate")
            client[self.mongo_db_name].authenticate(self.mongo_user, self.mongo_password, source=self.mongo_auth_db)
            logger.info("Auth is enabled for mongo - Successfully authenticated")
        else:
            logger.info("Auth is disabled for mongo")

        return client

    def get_db(self, database):
        """

        :param database:
        :return:
        """
        if self.client.get_database(database):
            return self.client[database]

        else:
            self.raise_exception('Database %s does not exist.'
                                 ' Please check your configuration file parameters and try again.' % database)

    def find_document_by_id(self, query):
        """

        :param modelName:
        :return:
        """
        logger.info("finding document with id: {0} from collection".format(query))
        document = self.collection.find_one(query)
        return document


    def get_collection(self, collection):
        """

        :param collection:
        :return:
        """
        if self.db.get_collection(self.mongo_collection_name):
            return self.db[self.mongo_collection_name]
        else:
            if collection == self.mongo_db_model_info_collection:
                logger.info("Creating the collection to store the predictions")
                self.db.create_collection(collection)
                return self.db[collection]
            else:
                self.raise_exception('Collection does not exist in {0} database.'
                                 'Please check your configuration file parameters and try again.'.format(self.mongo_db_name))

    def raise_exception(self, msg):
        """
        :param msg:
        :return:
        """
        raise Exception(msg)

    def update_document(self, query, document, **options):
        """

        :param query:
        :param document:
        :param options:
        :return:
        """
        logger.info("updating collection", extra={
            'query': query,
            'document': document
        })

        self.collection.update(query, document, **options)

    def create_document(self, document, **options):
        """

        :param document:
        :param options:
        :return:
        """
        logger.info("creating document in {0} collection".format(self.mongo_collection_name), extra={
            'document': document
        })

        self.collection.insert_one(document, **options)

    def get_docs_collection(self):
        """

        :return:
        """

        return self.collection.find()
