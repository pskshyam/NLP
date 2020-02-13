from util.config import config_loader

config = config_loader.idl_options
_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}


def get_config(key=None):
    if key is None:
        raise ValueError("Parameter 'key' should be provided")
    return config.__getattribute__(key)


def get_config_boolean(key):
    v = get_config(key)
    if v.lower() not in _boolean_states:
        raise ValueError('Not a boolean: %s' % v)
    return _boolean_states[v.lower()]


def get_config_int(key):
    return int(get_config(key))




