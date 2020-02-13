from falcon import testing
from falcon.request import Request
from falcon.response import Response

import app
from app.app_middleware.response_process import ResponseJSONProcessMiddleware


def test_process_request_for_nonstring(mocker):
    resp_data = b"{\"status\": \"success\"}"

    env = testing.create_environ()

    req = Request(env)
    req.method = 'POST'

    mocker.patch('app.app_middleware.response_process.json_of')

    resp = Response()
    resp.body = resp_data

    cut = ResponseJSONProcessMiddleware()
    cut.process_response(req, resp, None, None)
    app.app_middleware.response_process.json_of.assert_called_once_with(resp_data)


def test_process_request_for_string(mocker):
    resp_data = "{\"status\": \"success\"}"

    env = testing.create_environ()

    req = Request(env)
    req.method = 'POST'

    mocker.patch('app.app_middleware.response_process.json_of')

    resp = Response()
    resp.body = resp_data

    cut = ResponseJSONProcessMiddleware()
    cut.process_response(req, resp, None, None)
    app.app_middleware.response_process.json_of.assert_not_called()
