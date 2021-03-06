"""
Simple socket client thread sample.

Eli Bendersky (eliben@gmail.com)
This code is in the public domain
"""
import socket
import struct
import threading
import queue
from time import sleep

class ClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:

        CONNECT:    (host, port) tuple
        SEND:       Data string
        RECEIVE:    None
        CLOSE:      None
    """
    CONNECT, SEND, RECEIVE, CLOSE = range(4)

    def __init__(self, type, msg_type=None, line_number=None, data=None, task=None):
        self.type = type
        self.msg_type = msg_type
        self.line_number = line_number
        # print("task is ", task)
        self.task = 0 if task is None else task
        # print("self.task is ", self.task)
        self.data = data


class ClientReply(object):
    """ A reply from the client thread.
        Each reply type has its associated data:

        ERROR:      The error string
        SUCCESS:    Depends on the command - for RECEIVE it's the received
                    data string, for others None.
    """
    ERROR, SUCCESS, CONNECTED = range(3)

    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class SocketClientThread(threading.Thread):
    """ Implements the threading.Thread interface (start, join, etc.) and
        can be controlled via the cmd_q queue attribute. Replies are placed in
        the reply_q queue attribute.
    """
    def __init__(self, tcp_thread_event, cmd_q=queue.Queue(), reply_q=queue.Queue()):
        super(SocketClientThread, self).__init__()
        self.cmd_q = cmd_q
        self.reply_q = reply_q
        self.alive = tcp_thread_event
        self.socket = None

        self.line_number = 0
        self.address = ""

        self.handlers = {
            ClientCommand.CONNECT: self._handle_CONNECT,
            ClientCommand.CLOSE: self._handle_CLOSE,
            ClientCommand.SEND: self._handle_SEND,
            ClientCommand.RECEIVE: self._handle_RECEIVE,
        }

    def run(self):
        while self.alive.isSet():
            try:
                # queue.get with timeout to allow checking self.alive
                cmd = self.cmd_q.get(True, 0.1)
                self.handlers[cmd.type](cmd)
            except queue.Empty as e:
                continue
        print("TCP thread finished")

    def join(self, timeout=None):
        print("TCP start to join")
        self.alive.clear()
        threading.Thread.join(self, timeout)
        print("TCP join finished")

    def _handle_CONNECT(self, cmd):
        try:
            if self.socket:
                self.socket.close()
            self.line_number = cmd.data[0]
            self.address = cmd.data[1]
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.line_number, self.address))
            self.socket.settimeout(2)
            self.reply_q.put(self._success_connected())
            print("connect OK")
        except IOError as e:
            print("connect FAILD")
            self.reply_q.put(self._error_reply(str(e)))

    def _handle_CLOSE(self, cmd):
        self.socket.close()
        reply = ClientReply(ClientReply.SUCCESS)
        self.reply_q.put(reply)

    #  def _handle_SEND(self, cmd):
        print("_handle_CLOSE")
        print("len(cmd.data): ", len(cmd.data))
        header = struct.pack('>L', len(cmd.data))
        try:
            self.socket.sendall(header + format(cmd.data).encode())
            self.reply_q.put(self._success_reply())
        except IOError as e:
            self.reply_q.put(self._error_reply(str(e)))

    #  def _handle_SEND_ready(self, cmd):
    def _handle_SEND(self, cmd):
        # print("Send to socket:")

        # msg_type = struct.pack('>b', cmd.data[0])
        #msg_type = cmd.data[0]
        # Think smth to decrease debug log or make it... debug
        # print("cmd.msg_type: ", cmd.msg_type)
        # print("format(cmd.msg_type).encode(): ", format(cmd.msg_type).encode())
        # print("struct.pack('>b', cmd.msg_type): ", struct.pack('>b', cmd.msg_type))
        #
        # print("cmd.line_number: ", cmd.line_number)
        # print("format(cmd.line_number).encode(): ", format(cmd.line_number).encode())
        # print("struct.pack('>b', cmd.line_number): ", struct.pack('>b', cmd.line_number))
        #
        # print("cmd.task: ", cmd.task)
        # print("format(cmd.task).encode(): ", format(cmd.task).encode())
        # print("struct.pack('>b', cmd.task): ", struct.pack('>b', cmd.task))

        #line_number = cmd.data[1]
        #print("line_number: ", line_number)
        #print("format(line_number).encode(): ", format(line_number).encode())
        # ???????????????????? ????????:
        # scan = linecache.getline('/home/avovana/slave_controller/scans.txt', 1)
        # scan2 = linecache.getline('/home/avovana/slave_controller/scans.txt', 2)
        # scan3 = linecache.getline('/home/avovana/slave_controller/scans.txt', 3)
        # print("scan.encode(): ", scan.encode() + scan2.encode() + scan3.encode())
        # self.socket.sendall(scan.encode() + scan2.encode() + scan3.encode())

        if cmd.data:
            header = struct.pack('>L', 3 + len(cmd.data))
            # print(" len: ", len(cmd.data))
            # print(" header: ", header)
        else:
            header = struct.pack('>L', 3)
            # print(" header: ", header)

        try:
            if cmd.data is None:
                self.socket.sendall(header + struct.pack('>b', cmd.msg_type) + struct.pack('>b', cmd.line_number) + struct.pack('>b', cmd.task))
                print(" Send to socket. header: {0} OK".format(header))
            else:
                self.socket.sendall(header + struct.pack('>b', cmd.msg_type) + struct.pack('>b', cmd.line_number) + struct.pack('>b', cmd.task) + cmd.data.encode())
                print(" Send to socket. header: {0}, len: {1}, data: {2}, status: OK".format(header, len(cmd.data), cmd.data))

            # self.reply_q.put(self._success_reply("????????????????????"))

        except IOError as e:
            print(" Send to socket error: ", str(e))
            self.reply_q.put(self._error_reply(str("send_error")))

    def _handle_RECEIVE(self, cmd):
        attempts = cmd.msg_type
        print("Received:")
        try:
            #msg_len = self._recv_header()  # ???????? ???? ??????????????????, ???? ????????????????????
            #print("--msg_len: ", msg_len)

            header_data = self._recv_n_bytes(4, attempts)  # ???????? ???? ??????????????????, ???? ????????????????????
            print("header:", header_data)
            if header_data == b'':
                # self.reply_q.put(self._error_reply(str("receive_timeout")))
                self.reply_q.put(self._error_reply(str("connection_error")))
                return

            # print("header_data: ", header_data)
            msg_size = int.from_bytes(header_data, byteorder='big', signed=False)
            # print("msg_size: ", msg_size)

            body_data = self._recv_n_bytes(msg_size, attempts)  # type = bytes
            print("body_data:", body_data)

            # print("type 1: ", type(body_data))

            if body_data != b'':
                self.reply_q.put(self._success_reply(body_data))
            else:
                self.reply_q.put(self._error_reply(str("???????????????????? ??????????????????")))

            return

            # print("type_data: ", type_data)
            # msg_type = int.from_bytes(type_data, byteorder='big', signed=False)
            # print("msg_type: ", msg_type)

            # if msg_type == 4:
            #     #print("header_data[0:4]", body_data[0:4])
            #     #msg_type = int.from_bytes(body_data[0:4], byteorder='big', signed=False)
            #
            #     body_data = self._recv_n_bytes(msg_size - 4)
            #     print("body_data: ", body_data)
            #     body = body_data.decode()
            #     print("body: ", body)
            #
            #     self.reply_q.put(self._success_reply(body))
            #     return

            self.reply_q.put(self._error_reply('Socket closed prematurely'))
        except IOError as e:
            print("read IO error: ", str(e))
            self.reply_q.put(self._error_reply(str(e)))

    def _recv_header(self):
        chunk = self.socket.recv(4)
        header = int.from_bytes(chunk, byteorder='big', signed=False)
        print("header: ", header)

        return header

    def _recv_n_bytes(self, n, attempts):
        """ Convenience method for receiving exactly n bytes from self.socket
            (assuming it's open and connected).
        """
        # print("__in receive_______ attempts {0} wait {1} bytes".format(attempts, n))
        data = b''
        while len(data) < n and self.alive.isSet():
            print(" attempts {0}".format(attempts))
            try:
                chunk = self.socket.recv(n - len(data))
                print(" chunk len ", len(data))
            except socket.timeout as e:
                err = e.args[0]
                print(" socket error {0} attempts {1}".format(err, attempts))
                attempts = attempts - 1
                if attempts == 0:
                    print(" attempts == 0 ")
                    data = b''
                    break
            except socket.error as e:
                print(" socket error: ", e)
                data = b''
                break
                #self.reply_q.put(self._error_reply(str(e)))
            else:
                print(" chunk: ", chunk) # Case: data transmitted, socket on server was closed, wait answer, receive 0 byte => means socket was closed
                if chunk == b'':
                    print(" ???????????? ????????????????????")
                    # self.socket.close()
                    data = b''
                    # self.reply_q.put(self._error_reply(str("socket_closed")))
                    break

                data += chunk

        # print(" data: ", data)
        return data

    def _error_reply(self, errstr):
        return ClientReply(ClientReply.ERROR, errstr)

    def _success_reply(self, data=None):
        # print("type: 2", type(data))
        return ClientReply(ClientReply.SUCCESS, data)

    def _success_connected(self, data=None):
        return ClientReply(ClientReply.CONNECTED, data)


#------------------------------------------------------------------------------
if __name__ == "__main__":
    sct = SocketClientThread()
    sct.start()
    sct.cmd_q.put(ClientCommand(ClientCommand.CONNECT, ('localhost', 50007)))
    reply = sct.reply_q.get(True)
    print(reply.type, reply.data)
    sct.cmd_q.put(ClientCommand(ClientCommand.SEND, "hellothere"))
    reply = sct.reply_q.get(True)
    print(reply.type, reply.data)
    sct.cmd_q.put(ClientCommand(ClientCommand.RECEIVE, "hellothere"))
    reply = sct.reply_q.get(True)
    print(reply.type, reply.data)
    sct.cmd_q.put(ClientCommand(ClientCommand.CLOSE))
    reply = sct.reply_q.get(True)
    print(reply.type, reply.data)
    pass
