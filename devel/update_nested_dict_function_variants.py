#!/usr/bin/env python
#
# Function: Update nested dicts
# (c) Peter Krauspe 3/2016
#
import pprint
import collections

def update_nested_dict1(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update_nested_dict1(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d



# update_nested_dict1 has an issue if a value within the recursive dict happens to be a list,
# update_nested_dict2 makes it correct

def update_nested_dict2(orig_dict, new_dict):
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = update_nested_dict2(orig_dict.get(key, { }), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict[key] + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict



# update_nested_dict2 doesn't work when replacing an element such as an integer with a dictionary, ' '
# such as update_nested_dict2({'foo':0},{'foo':{'bar':1}}). This update_nested_dict3 addresses it:


def update_nested_dict3(d, u):
    for k, v in u.iteritems():
        if isinstance(d, collections.Mapping):
            if isinstance(v, collections.Mapping):
                r = update_nested_dict3(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        else:
            d = {k: u[k]}
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


updated_dict = update_nested_dict3(dict,dict_update)

print pprint.pprint(updated_dict)