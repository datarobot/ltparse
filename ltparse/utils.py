import collections
import copy
import json
import yaml


def update_recursive(old, new):
    out = copy.deepcopy(old)
    if new is None:
        return out
    for key, val in new.iteritems():
        try:
            old_val = old[key]
        except KeyError:
            out[key] = val
            break
        if not isinstance(old_val, dict) or not isinstance(val, dict):
            out[key] = val
            break
        out[key] = update_recursive(old_val, val)
    return out


def unicode_to_str(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode_to_str, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode_to_str, data))
    else:
        return data


def dump_yaml(data):
    return yaml.dump(data, indent=2, default_flow_style=False)


def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True)
