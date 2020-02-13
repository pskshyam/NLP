from util.config import config_access as config


class IDLConfig:
    log_location = config.get_config('log')

    # [Mongo]
    mongo_db_host = config.get_config('mongo_db_host')
    mongo_db_port = config.get_config_int('mongo_db_port')
    mongo_db_name = config.get_config('mongo_db_name')
    mongo_db_model_config_collection = config.get_config('mongo_db_model_config_collection')
    mongo_db_model_info_collection = config.get_config('mongo_db_model_info_collection')
    mongo_db_keys_info = config.get_config('mongo_db_keys_info')

    mongo_db_user = config.get_config('mongo_db_user')
    mongo_db_password = config.get_config('mongo_db_password')

    mongo_auth_enabled = config.get_config_boolean('mongo_auth_enabled')
    mongo_auth_db = config.get_config('mongo_auth_db')

    # [Celery]
    celery_broker = config.get_config('celery_broker')
    celery_backend = config.get_config('celery_backend')

    # [ML]
    # ml_pdf_conv_resolution = config.get_config_int('ml_pdf_conv_resolution')

    def __init__(self):
        pass


idl_config = IDLConfig()



