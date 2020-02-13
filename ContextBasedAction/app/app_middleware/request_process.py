import json
import falcon
from app.common.logger import set_up_logging

logger = set_up_logging(__name__)

'''
Decodes all responses from the api        
'''


class RequestBodyJSONProcessMiddleware(object):

    def process_request(self, req, resp):
        if req.method in ['POST', 'PUT'] and 'application/json' in req.content_type:
            json_str = req.stream.read().decode("utf-8")
            try:
                # decode() is needed for running in python3.5
                doc = json.loads(json_str) if req.content_length else None
                req.context['doc'] = doc
            except ValueError:
                logger.error("Error parsing json")
                logger.error(json_str)
                raise falcon.HTTPBadRequest("Unable to parse Request Body", json_str)
