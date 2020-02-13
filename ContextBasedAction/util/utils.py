import base64
import datetime
import hashlib
import random

def now():
    """
    Returns the current date time. useful for created_at for db operations
    :return:
    """
    return datetime.datetime.utcnow()

def contains(base, sub_list):
    """
    Checks if an array is a subset of another
    :param base:
    :param sub_list:
    :return:
    """
    return set(base) & set(sub_list) == set(sub_list)

def dict_contains(dct, keys):
    """
    :param dct:
    :param keys:
    :return:
    """
    assert isinstance(dct, dict), "dict_contains: dct should be of type dict "
    assert type(keys) in [int, str, list], "dict_contains: keys should be of type list or string "
    if not type(keys) == list:
        keys = [keys]

    return contains(dct.keys(), keys)

def token():
    """

    :return:
    """
    hlib = hashlib.sha256(str(random.getrandbits(256)).encode('utf-8')).digest()
    rand = random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD']).encode('utf-8')
    return base64.b64encode(hlib, rand).rstrip(('==').encode('utf-8')).lower().decode("utf-8")

