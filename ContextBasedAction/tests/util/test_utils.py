import datetime
import mock
import util
from util import utils
from unittest.mock import patch
from datetime import datetime
import base64

@patch('util.utils.datetime')
def test_now(mocker):

    mocker.datetime.utcnow = mock.Mock(return_value=datetime(2019, 2, 12))
    date = utils.now()
    assert datetime(2019, 2, 12) == date


def test_contains_true():
    base_test = "test"
    sub_list_test = "t"
    contains_return = utils.contains(base_test,sub_list_test)
    assert contains_return == True


def test_contains_false():
    base_test = "test"
    sub_list_test = "a"
    contains_return = utils.contains(base_test,sub_list_test)
    assert contains_return == False


def test_dict_contains_not_dict():
    try:
        utils.dict_contains([], [])
    except AssertionError as exc:
        assert str(exc) == "dict_contains: dct should be of type dict "


def test_dict_contains_not_types_keys():
    try:
        utils.dict_contains({}, 1.2)
    except AssertionError as exc:
        assert str(exc) == "dict_contains: keys should be of type list or string "


@patch('util.utils.contains')
def test_dict_contains_contains_call(mocker):

    dct_contains = {'test_key': 'test_value'}
    keys_list_dct_contains = ['test_key']
    utils.dict_contains(dct_contains, keys_list_dct_contains)

    mocker.assert_called_once_with(dct_contains.keys(), keys_list_dct_contains)


def test_token(mocker):
    mocker.patch.object(util.utils.base64, "b64encode")
    utils.token()
    assert base64.b64encode.call_count == 1
