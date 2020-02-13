import falcon
from falcon import testing
from falcon.request import Request
from falcon.response import Response

from app.app_middleware.request_process import RequestBodyJSONProcessMiddleware

from pytest import raises


def test_process_request(mocker):
    req_data = "{\"service_id\": \"invoice_extraction1\",\"model_name\": \"invoice_extraction\"," \
               "\"image\": \"test_data\"}".encode("utf-8")

    env = testing.create_environ(headers= {"Content-Type" : "application/json", "Content-Length" : str(len(req_data))})

    req = Request(env)
    req.method = 'POST'

    mocker.patch.object(req.stream, 'read', return_value = req_data)
    doc = {
            "service_id": "invoice_extraction1",
            "model_name": "invoice_extraction",
            "image": "test_data"
        }

    resp = Response()

    cut = RequestBodyJSONProcessMiddleware()
    cut.process_request(req, resp)
    assert req.context['doc'] == doc


def test_invalid_process_request(mocker):
    req_data = "\"service_id\": \"invoice_extraction1\",\"model_name\": \"invoice_extraction\"," \
               "\"image\": \"test_data\"".encode("utf-8")

    env = testing.create_environ(headers= {"Content-Type" : "application/json", "Content-Length" : str(len(req_data))})

    req = Request(env)
    req.method = 'POST'

    mocker.patch.object(req.stream, 'read', return_value = req_data)
    doc = {
            "service_id": "invoice_extraction1",
            "model_name": "invoice_extraction",
            "image": "test_data"
        }

    resp = Response()

    cut = RequestBodyJSONProcessMiddleware()
    with raises(falcon.HTTPBadRequest):
        cut.process_request(req, resp)

