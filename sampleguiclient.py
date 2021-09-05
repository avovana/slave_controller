#!/usr/bin/python
"""
Sample GUI using SocketClientThread for socket communication, while doing other
stuff in parallel.

Eli Bendersky (eliben@gmail.com)
This code is in the public domain
"""
import os, sys, time
import queue
import design
import re

from datetime import datetime
from threading import Thread
import threading

import linecache
import signal
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from socketclientthread import SocketClientThread, ClientCommand, ClientReply

import glob
import sys
sys.path.append('thrift_server/gen-py')
sys.path.insert(0, glob.glob('thrift_server/lib*')[0])

from slave_controller import SlaveController
from slave_controller.ttypes import ScannerStatus

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

SERVER_ADDR = 'localhost', 6000

class LogWidget(QTextBrowser):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#ddddfd"))
        self.setPalette(palette)

class ThriftImpl(QObject):
    scan_signal = pyqtSignal(str)
    scanner_state_signal = pyqtSignal(int)
    def __init__(self):
        QObject.__init__(self)

    def scan(self, scan):
        self.scan_signal.emit(scan)

    def scanner_status(self, state):
        self.scanner_state_signal.emit(state)

class SlaveGui(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.create_client()

        self.ready_button.clicked.connect(self.send_ready)
        self.finish_button.clicked.connect(self.send_file)

        self.scanner_status_checkbox.setEnabled(False)

        self.create_timers()

        self.log("Started")

        signal.signal(signal.SIGTRAP, self.receiveSignal)

        self.product_passed_dt = datetime.now()

        #-----------------Serial Port-----------------
        available_ports = QSerialPortInfo.availablePorts()
        for port in available_ports:
            print('port: ', port.portName())

        port = "ttyS1"
        self.serial = QSerialPort(self)
        self.serial.setPortName(port)
        if self.serial.open(QIODevice.ReadWrite):
            self.serial.setBaudRate(115200)
            self.serial.readyRead.connect(self.on_serial_read)
            self.serial.write(b'h\n')
        else:
            raise IOError("Cannot connect to device on port {}".format(port))

        print('COM PORT connected INFO')

    def on_serial_read(self):
        print('on_serial_read starting...')
        readbytes = bytes(self.serial.readAll())

        print('readbytes: ', readbytes)

        if readbytes == b'h\n':
            print('Received:', "b'h\\n'")
            self.comport_status_checkbox.setChecked(True)

            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#23F617"))
            self.comport_status_checkbox.setPalette(palette)
        elif readbytes == b'p\n':
            print('Received:', "b'p\\n'")
            self.product_passed_dt = datetime.now()
            print('product_passed_dt: ', self.product_passed_dt)

        print('on_serial_read finished')

    def scan(self, scan):
        scan_len = len(scan)
        print('scan : ', scan)
        print('scan len: ', scan_len)

        current_dt = datetime.now()
        duration = current_dt - self.product_passed_dt
        duration_in_ms = duration.total_seconds() * 1000

        print('duration_in_ms: ', duration_in_ms)
        if duration_in_ms > 500:
            self.log('Прошло больше 500 мс! Отбраковано')
            print('Прошло больше 500 мс! Отбраковано WARN')
            msg = b'e\n'
            self.serial.write(msg)
            return

        print('Скан успел пройти!')

        if scan_len <= 20:
            self.log('Маленькая длина! Отбраковано')
            print('Scan len <= 20 Warn')
            # отправить сигнал отбраковщику
            return

        gs_pos = scan.find(chr(29))
        print('gs_pos = ', gs_pos)

        if gs_pos == -1:
            print('Нет символа GS Warn')
            self.log('Нет символа GS! Отбраковано')
            # отправить сигнал отбраковщику
            return

        print('Скан ок')

        # scan = "\"1234\"5"
        # print('scan : ', scan)
        #
        # scan = re.sub(r"\"", '\"\"', scan)
        # print('scan : ', scan)
        #
        #scan = scan[:gs_pos]
        #print('scan : ', scan)

        date_time = datetime.now().strftime("%d.%m.%Y")
        filename = 'ki_' + date_time + '.txt'

        if not os.path.exists(filename):
            os.mknod(filename)

        # with open(filename) as f:
        #     if scan in f.read():
        #         print("дубликат!")
        #         self.log('Дубликат! Отбраковано')
        #         # отправить сигнал отбраковщику
        #         return

        print("оригинальный!")

        with open(filename, "a") as myfile:
            myfile.write(scan + "\n")

        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 2, 7, scan))
        self.log('Записан в файл. Подготовлен для отправки')

    def scanner_status(self, status):
        if status == ScannerStatus.Ready:
            print('scan ready: ', status)
            self.scanner_status_checkbox.setChecked(True)
            self.scanner_status_checkbox.setEnabled(False)

            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#23F617"))
            self.scanner_status_checkbox.setPalette(palette)
        elif status == ScannerStatus.Stop:
            self.scanner_status_checkbox.setChecked(False)
            print('scan stop: ', status)
            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#ff1200"))
            self.scanner_status_checkbox.setPalette(palette)
        else:
            print('invalid status: ', status)

    def create_timers(self):
        self.client_reply_timer = QTimer(self)
        self.client_reply_timer.timeout.connect(self.on_client_reply_timer)
        self.client_reply_timer.start(100)

    def send_ready(self):
        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(line_number), SERVER_ADDR))
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(line_number)))
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait info
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait start_signal

    def send_file(self):
        date_time = datetime.now().strftime("%d.%m.%Y")
        filename = 'ki_' + date_time + '.txt'
        print("Подготовка к отправке файла ", filename)

        if not os.path.exists(filename):
            print("Файла нет!")
            return

        with open(filename, "r") as myfile:
            bytes = myfile.read()
            print("Считаны данные из файла ", bytes)
            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 3, 7, bytes))
            #self.log('Файл отправлен')

    def on_client_reply_timer(self):
        try:
            reply = self.client.reply_q.get(block=False)
            status = "УСПЕШНО" if reply.type == ClientReply.SUCCESS else "ОШИБКА"
            #  "Получены данные: " + body_data.decode('utf-8')
            self.log('%s: %s' % (status, reply.data))
            # print("   reply.type:", reply.type)
            # print("   reply.data:", reply.data)

            if reply.data is None:
                return

            msg_type = int.from_bytes(reply.data[0:4], byteorder='big', signed=False)
            # print("msg_type: ", msg_type)
            # print("reply.data: ", reply.data)
            # print("len(reply.data): ", len(reply.data))
            # print("reply.data[4:len(reply.data) - 4 - 1]: ", reply.data[4:len(reply.data)])
            # print("len(reply.data[4:len(reply.data) - 4 - 1]): ", len(reply.data[4:len(reply.data)]))
            body = reply.data[4:len(reply.data)].decode()
            # print("body: ", body)

            if msg_type == 4:
                name, plan = body.split(",")
                self.name_label.setText(name)
                self.plan_label.setText(plan)
            elif msg_type == 6:
                self.log('Можно начинать')
        except queue.Empty:
            pass

    def create_client(self):
        self.client = SocketClientThread()
        self.client.start()

    def log(self, msg):
        timestamp = '[%010.3f]' % time.process_time()
        self.text_browser.append(timestamp + ' ' + str(msg))

    def receiveSignal(self, signalNumber, frame):
        print('Received:', signalNumber)
        self.scanner_status_checkbox.setChecked(True)
        self.scanner_status_checkbox.setEnabled(False)

        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#23F617"))
        self.scanner_status_checkbox.setPalette(palette)

def create_thrift_server(thrift_client):
    processor = SlaveController.Processor(thrift_client)
    transport = TSocket.TServerSocket(host='localhost', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('thrift_server=starting info')
    server.serve()
    print('thrift_server=done info')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = SlaveGui()
    thrift_impl = ThriftImpl()

    thrift_impl.scan_signal.connect(mainwindow.scan)
    thrift_impl.scanner_state_signal.connect(mainwindow.scanner_status)

    thread = Thread(target=create_thrift_server, args=(thrift_impl,))
    thread.start()

    mainwindow.show()
    app.exec_()
    thread.join()
