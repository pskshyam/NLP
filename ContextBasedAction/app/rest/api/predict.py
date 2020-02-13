import json
import logging
import falcon
import falcon_multipart
from app.startup import Route
from jobs.tasks import get_prediction
from app.rest.api.impl.helper import update_config
from util.utils import dict_contains, token
from falcon import HTTPBadRequest

logger = logging.getLogger(__name__)


@Route('/context-extractor/predict')
class Predict():

    @staticmethod
    def _bad_request():
        """

        :return:
        """
        description = 'Mandatory params missing from the request for /context-extractor/predict. ' \
                      'Please check your request params and retry'
        logger.exception(description)
        raise HTTPBadRequest("HTTP Bad Request", description)

    def _validate_model_config(req, resp, resource, params):
        """

        :param resp:
        :param resource:
        :param params:
        :return:
        """
        doc = req.params
        mandatory_fields = ["data"]
        assert dict_contains(doc, mandatory_fields) is True, Predict._bad_request()

    @falcon.before(_validate_model_config)
    def on_post(self, req, resp):
        doc = req.params
        data = doc["data"]
        service_id = token()
        doc["service_id"] = service_id
        update_config(doc=doc)
        doc.pop("service_id")
        try:
            if isinstance(data, falcon_multipart.parser.Parser):
                doc['data'] = data.file.read().decode("utf-8")
            get_prediction.delay(service_id=service_id, **doc )
            eval_response = {

                "service_id": service_id,
                "prediction_status": "Initialized",
                "prediction_status_message": "Prediction in progress.  Prediction status can be checked using the "
                                             "model status api - /context-extractor/status."
            }

            resp.body = json.dumps(eval_response, ensure_ascii=False)
        except ValueError as ex:
            logger.exception(str(ex), exc_info=True)
            eval_response = {
                "service_id": service_id,
                "prediction_status": "Failed",
                "prediction_status_message": str(ex)
            }
            resp.body = json.dumps(eval_response, ensure_ascii=False)
