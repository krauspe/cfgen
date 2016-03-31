#!/usr/bin/env python

# test script for developing a little parser for
# "value-strings" from template files (.hjson)
#
# GOAL: translate and eval
#
# "cfg.net.nics.nic0.ip"       --> eval "cfg['net']['nics']['nic0']['ip']"
# "myFunction(arg1,arg2,arg3)" --> eval "myFunction(arg1,arg2,arg3)" if 'myFunction' is a known function

import re

KnownFunctions = [
        'myFunctionNoArgs',
        'myFunctionOneArg',
        'myFunctionMultipleArgs'
    ]


def myFunctionNoArgs():
    return "retval_of_myFunctionNoArgs"

def myFunctionOneArg(arg1):
    return "retval_of_myFunctionWithArg"

def myFunctionMultipleArgs(arg1):
    return "retval_of_myFunctionMultipleArgs"

value_strings  = [
    "cfg.net.nics.nic0.ip",
    "myFunctionNoArgs()"
    "myFunctionOneArg(arg1)"
    "myFunctionMultipleArgs(arg1,arg2,arg3)"
    ]


# In[53]: obj = re.split("[()]","getSomething") ; print len(obj); obj
# 1
# Out[52]: ['getSomething']
# In[54]: obj = re.split("[()]","getSomething()") ; print len(obj); obj
# 3
# Out[53]: ['getSomething', '', '']
# In[55]: obj = re.split("[()]","getSomething(arg1)") ; print len(obj); obj
# 3
# Out[54]: ['getSomething', 'arg1', '']
# In[56]: obj = re.split("[()]","getSomething(arg1,arg2)") ; print len(obj); obj
# 3
# Out[55]: ['getSomething', 'arg1,arg2', '']
# In[57]: obj = re.split("[()]","getSomething(arg1,arg2") ; print len(obj); obj
# 2
# Out[56]: ['getSomething', 'arg1,arg2']

# In[60]: obj = re.split("\.","cfg.net.nics.nic1.ip") ; print len(obj); obj
# 5
# Out[59]: ['cfg', 'net', 'nics', 'nic1', 'ip']

# TODO: USE obove outputs to find a strategy ....

def evaluateValFromCfg():
    pass