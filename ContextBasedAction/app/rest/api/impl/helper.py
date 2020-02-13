from app.db.ModelManager import ModelInfoManager
from util.utils import now

class ConfigHelper():

    def __init__(self, doc):
        self.service_id = doc['service_id']
        self.info_manager = ModelInfoManager()


    def update_config(self):
        query = {
            "service_id": self.service_id
        }
        config = {
            "prediction_status": self.info_manager.STATUS_PREDICTION_INIT,
            "prediction_status_message": "Prediction Initialized. Prediction in progress",
            "updated_at": now()
        }
        document = {
            "$set": config,
            "$unset":{"prediction":""}
        }

        self.info_manager.update(query=query, document=document)

    def save_config(self):
        document = {
            "service_id": self.service_id,
            "prediction_status": self.info_manager.STATUS_PREDICTION_INIT,
            "prediction_status_message": "Prediction Initialized. Evaluation in progress",
            "created_at": now(),
            "updated_at": now()

        }
        self.info_manager.create(document)

    def service_info_exists(self):
        exists = self.info_manager.service_exists(self.service_id)

        return exists

def update_config(doc):
     config_helper = ConfigHelper(doc)
     if config_helper.service_info_exists():
        config_helper.update_config()
     else:
         config_helper.save_config()
