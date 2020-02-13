from app.common.app_functions import json_of


def test_json_of_string():
    data = "{'key':'value'}"
    res = json_of(data)
    assert res == '"{\'key\':\'value\'}"'


def test_json_of_string_with_escaped_quotes():
    data = "{\"key\":\"value\"}"
    res = json_of(data)
    assert res == '"{\\"key\\":\\"value\\"}"'


def test_json_of_mapping():
    data = {'key':'value'}
    res = json_of(data)
    assert res == '{"key": "value"}'


def test_json_of_iterable():
    data = ["value1", "value2"]
    res = json_of(data)
    assert res == '["value1", "value2"]'


def test_json_of_others():
    data = 2
    res = json_of(data)
    assert res == '2'
