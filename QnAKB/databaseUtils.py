import pymongo as pymongo
from logger.logger import set_up_logging

logger = set_up_logging(__name__)
from pymongo import MongoClient
from config.constants import ENV


class DBUtil:
    """
    Description : Class For Managing All the Database Related functionality
    Author : Sachin Ichake

    """

    connection = None

    def __init__(self):
        pass

    @classmethod
    def getConnection(cls):  # get connection for database connection and connection to database
        try:
            if cls.connection is not None:
                return cls.connection
            username = str(ENV.get("USER_NAME"))
            password_kb = str(ENV.get("PASSWORD"))
            hostname = str(ENV.get("HOST"))
            dbSchema = str(ENV.get("DB_SCHEMA"))
            port = int(str(ENV.get("PORT")))
            mongo_auth_db = str(ENV.get("MONGO_AUTH_DB"))
            print('-------',username,password_kb,hostname,dbSchema,port,mongo_auth_db)
            mongoClient = MongoClient(host=hostname, port=port, username=username, password=password_kb,
                                      authSource=mongo_auth_db)
            cls.connection = mongoClient[dbSchema]
            print(cls.connection)
        except Exception as e:
            logger.error("Error while connecting To database : " + str(e))
        return cls.connection

    @classmethod
    def getData(cls, tableName, filterDict={}, projection=[], pageNumber=1, pageSize=100000,
                sort=['_id', pymongo.ASCENDING]):  # get data from collection
        try:
            connection = cls.getConnection()
            skipValue = (pageNumber - 1) * pageSize
            limitValue = pageSize
            response = connection[tableName].find(filterDict).skip(skipValue).limit(limitValue).sort(*sort)

            all_question_list = []
            for i, doc in enumerate(response):
                all_question_list.append([])
                all_question_list[i].append(doc['question'])
                all_question_list[i].append(doc['answer'])
                all_question_list[i].append(doc['q_id'])

            logger.info('----------Result from getdata Start ----------')
            logger.info(all_question_list)
            logger.info('----------Result from getdata End----------')

            return all_question_list

        except Exception as e:
            logger.error("Exception in getData for " + tableName+" : "+str(e))
            return []
