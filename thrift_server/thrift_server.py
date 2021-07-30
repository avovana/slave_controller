#!/usr/bin/env python

import glob
import sys
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('lib*')[0])

from slave_controller import SlaveController
from slave_controller.ttypes import ScannerStatus

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class SlaveControllerHandler:
    def __init__(self):
        self.log = {}

    def scan(self, scan):
        print('scan: ', scan)

    def scanner_status(self, status):
        print('calculate(%i)' % status)
        #
        # if work.op == Operation.ADD:
        #     val = work.num1 + work.num2
        # elif work.op == Operation.SUBTRACT:
        #     val = work.num1 - work.num2
        # elif work.op == Operation.MULTIPLY:
        #     val = work.num1 * work.num2
        # elif work.op == Operation.DIVIDE:
        #     if work.num2 == 0:
        #         raise InvalidOperation(work.op, 'Cannot divide by 0')
        #     val = work.num1 / work.num2
        # else:
        #     raise InvalidOperation(work.op, 'Invalid operation')
        #
        # log = SharedStruct()
        # log.key = logid
        # log.value = '%d' % (val)
        # self.log[logid] = log
        #
        # return val

if __name__ == '__main__':
    handler = SlaveControllerHandler()
    processor = SlaveController.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()
    print('done.')
