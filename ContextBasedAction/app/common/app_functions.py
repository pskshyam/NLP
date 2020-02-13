import json
from bson import json_util
import collections


def __convert(data):
    if isinstance(data, str):
        try:
            return str(data.decode('utf-8', 'ignore').encode('utf-8').decode('ascii', 'ignore'))
        except:
            return str(data.encode('utf-8').decode('ascii', 'ignore'))
    elif isinstance(data, collections.Mapping):
        return dict(map(__convert, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(__convert, data))
    else:
        return data


def json_of(json_obj):
    json_obj=json.dumps(__convert(json_obj), default=json_util.default, ensure_ascii=False)
    return json_obj
