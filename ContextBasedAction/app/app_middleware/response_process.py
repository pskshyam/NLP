from app.common.app_functions import json_of

'''
Decodes all responses from the api        
'''


class ResponseJSONProcessMiddleware(object):

    def process_response(self, req, resp, resource, req_succeeded):
        if not isinstance(resp.body, str):
                resp.body = json_of(resp.body)
