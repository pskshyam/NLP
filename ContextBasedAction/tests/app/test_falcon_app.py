from falcon import testing
import pytest
from mock import patch
import falcon
from urllib.parse import urlencode

from app.falcon_app import create_application


# Depending on your testing strategy and how your application
# manages state, you may be able to broaden the fixture scope
# beyond the default 'function' scope used in this example.

@pytest.fixture()
def client():
    # Assume the hypothetical `myapp` package has a function called
    # `create()` to initialize and return a `falcon.API` instance.
    return testing.TestClient(create_application())


@patch('app.rest.api.predict.update_config')
def no_test_predict_call(client):
    body = urlencode({
        'model_name': 'test_model',
        'image': 'test_image'
    })
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = client.simulate_post('/dl/predict', headers=headers, body=body)

 #   app.rest.api.predict.update_config.assert_called_once()
    assert res.status_code == falcon.HTTP_200


def test_status_call(client):
    json_data = {"service_id" : "v9maerssi7ncngpugml7rwba0bljlg9liqulmyjddlk"}
    headers = {"Content-Type": "application/json"}

    response_list = client.simulate_post('/dl/status', json=json_data, headers=headers)
    assert response_list.status_code == 200


def test_status_call_400(client):
    json_data = {}
    headers = {"Content-Type": "application/json"}

    response_list = client.simulate_post('/dl/status', json=json_data, headers=headers)
    assert response_list.status_code == 400


def test_result_call(client):
    json_data = {"service_id" : "v9maerssi7ncngpugml7rwba0bljlg9liqulmyjddlk"}
    headers = {"Content-Type": "application/json"}

    response_list = client.simulate_post('/dl/result', json=json_data, headers=headers)
    assert response_list.status_code == 200


def test_result_call_400(client):
    json_data = {}
    headers = {"Content-Type": "application/json"}

    response_list = client.simulate_post('/dl/result', json=json_data, headers=headers)
    assert response_list.status_code == 400
