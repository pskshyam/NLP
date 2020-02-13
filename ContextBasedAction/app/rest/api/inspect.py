import json
import logging
import falcon
from app.startup import Route
from collections import OrderedDict
from app.rest.api.impl.inspect_impl import get_status, get_prediction_value
from util.utils import dict_contains
from falcon import HTTPBadRequest

logger = logging.getLogger(__name__)

@Route('/context-extractor/status')
class Status():

    @staticmethod
    def _bad_request():
        """

        :return:
        """
        description = 'Mandatory params missing from the request for /context-extractor/status. ' \
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
        doc = req.context['doc']
        mandatory_fields = ['service_id']
        assert dict_contains(doc, mandatory_fields) is True, Status._bad_request()

    @falcon.before(_validate_model_config)
    def on_post(self, req, resp):

        doc = req.context['doc']
        service_id = doc['service_id']
        try:
            status = get_status(service_id)
            resp.body = json.dumps(status, ensure_ascii=False)
        except Exception as e:
            logger.exception(str(e), exc_info=True)
            eval_response = {
                "title": "Error while fetching model status",
                "description": str(e)
            }
            resp.body = json.dumps(eval_response, ensure_ascii=False)


@Route('/context-extractor/result')
class PredictionValue():

    @staticmethod
    def _bad_request():
        """

        :return:
        """
        description = 'Mandatory params missing from the request for /context-extractor/result. ' \
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
        doc = req.context['doc']
        mandatory_fields = ['service_id']
        assert dict_contains(doc, mandatory_fields) is True, Status._bad_request()

    @falcon.before(_validate_model_config)
    def on_post(self, req, resp):

        doc = req.context['doc']
        service_id = doc['service_id']
        try:
            prediction = get_prediction_value(service_id)
            resp.body = json.dumps(prediction, ensure_ascii=False)
        except Exception as e:
            logger.exception(str(e), exc_info=True)
            eval_response = {
                "title": "Error while fetching prediction",
                "description": str(e)
            }
            resp.body = json.dumps(eval_response, ensure_ascii=False)