from app.db.ModelManager import ModelInfoManager
import logging

logger = logging.getLogger(__name__)

def get_status(service_id):
    manager = ModelInfoManager()
    status = manager.get_status(service_id)
    return status

def get_prediction_value(service_id):
    manager = ModelInfoManager()
    prediction_value = manager.get_prediction_value(service_id)
    return prediction_value



