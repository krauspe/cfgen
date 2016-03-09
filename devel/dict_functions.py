#!/usr/bin/env python
#
# Function: Update nested dicts
# (c) Peter Krauspe 3/2016
#
import pprint
import collections

def update_nested_dict(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update_nested_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


dict = {
    'key1':'val1',
    'key2':'val2',
    'dict':{
        'dkey1':'dval1',
        'dkey2':'dval2',
        'dkey3':'dval3',
        },
    }

dict_update = {
    'key2':'val2-changed',
    'key3':'val3-added',
    'dict':{
        'dkey2':'dval2-changed',
        'dkey3':'dval3-added',
        },
}


updated_dict = update_nested_dict(dict,dict_update)

print pprint.pprint(updated_dict)