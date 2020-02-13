from jobs.config import app
from celery import Task
from util.utils import now
from celery.utils.log import get_task_logger
from app.db.ModelManager import ModelInfoManager
from models.context_extraction.context_extractor import ContextExtractor
logger = get_task_logger(__name__)

class LogErrorsTask(Task):
    """
        Log errors
        """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print ('{0!r} failed: {1!r}'.format(task_id, exc))
        self.save_failed_task(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :param traceback:
        :param kwargs:
        :param args:
        :param task_id:
        :type exc: Exception
        """

        name = self.name.split('.')[-1]
        exception_msg = str(exc).strip()

        str(traceback).strip()
        now()

        print(name)
        print(exception_msg)
        print(args)
        print(kwargs)



@app.task(base = LogErrorsTask)
def get_prediction(service_id, **kwargs):
    info_manager = ModelInfoManager()
    text = kwargs.pop("data")
    try:
        predict_class = ContextExtractor()
        prediction = predict_class.predict(text, **kwargs)
        config = {
            "prediction": prediction,
            "prediction_status": ModelInfoManager.STATUS_PREDICTION_SUCCESS,
            "prediction_status_message": "Prediction completed succesfully"
        }
        document = {
            "$set": config
        }
        info_manager.update({'service_id': service_id}, document)
    except Exception as e:
        logger.exception(str(e))
        config = {
            "prediction_status": ModelInfoManager.STATUS_PREDICTION_FAILED,
            "prediction_status_message": str(e)
        }
        document = {
            "$set": config
        }
        info_manager.update({'service_id': service_id}, document)

