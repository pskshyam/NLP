import os

ENV = {
"TFHUB_SENTENCE_MODEL_DIR": os.environ.get("TFHUB_SENTENCE_MODEL_DIR"),
"HOST" : os.environ.get("mongo_host"),
"DB_SCHEMA" : os.environ.get("mongo_auth_db"),
"USER_NAME" : os.environ.get("mongo_username"),
"PASSWORD" : os.environ.get("mongo_password"),
"PORT" : os.environ.get("mongo_port"),
"MONGO_AUTH_DB": os.environ.get("mongo_auth_db")
}

# ENV = {
# "TFHUB_SENTENCE_MODEL_DIR": "/qnakb/sentence_model/",
# "HOST" : "172.16.4.11",
# "DB_SCHEMA" : "knowledge_base",
# "USER_NAME" : "iceAdmin",
# "PASSWORD" : "ice@123",
# "PORT" :27017,
# "MONGO_AUTH_DB": "knowledge_base"
# }

