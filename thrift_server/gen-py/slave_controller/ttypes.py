#
# Autogenerated by Thrift Compiler (0.14.2)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class ScannerStatus(object):
    Ready = 1
    Stop = 2

    _VALUES_TO_NAMES = {
        1: "Ready",
        2: "Stop",
    }

    _NAMES_TO_VALUES = {
        "Ready": 1,
        "Stop": 2,
    }
fix_spec(all_structs)
del all_structs