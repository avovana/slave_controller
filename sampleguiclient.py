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

#SERVER_ADDR = '192.168.0.116', 6000
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
        self.showMaximized()

        self.tcp_thread_event = threading.Event()
        self.tcp_thread_event.set()

        self.client = SocketClientThread(self.tcp_thread_event)
        self.client.start()

        self.ready_button.clicked.connect(self.send_ready)
        self.finish_button.clicked.connect(self.send_file)
        self.choose_file_pushbutton.clicked.connect(self.choose_file)

        self.scanner_status_checkbox.setEnabled(False)

        self.create_timers()

        self.sensor_counter = 0
        self.scan_counter = 0
        self.defect_counter = 0

        self.log("Started")

        signal.signal(signal.SIGTRAP, self.receiveSignal)

        self.product_passed_dt = datetime.now()
        self.current = 0

        date_time = datetime.now().strftime("%d.%m.%Y-%H:%M")
        self.filename = 'ki_' + self.name_label.text() + '_' + date_time + '.txt'

        #-----------------Serial Port-----------------
        available_ports = QSerialPortInfo.availablePorts()

        for port in available_ports:
            print('port: ', port.portName())

        if len(available_ports) == 0:
            raise IOError("No available com ports ERROR")

        #port = "ttyS1"
        # port = available_ports[0].portName()
        port = available_ports[1].portName()
        self.serial = QSerialPort(self)
        self.serial.setPortName(port)
        if self.serial.open(QIODevice.ReadWrite):
            self.serial.setBaudRate(9600)
            self.serial.clear()
            self.serial.readyRead.connect(self.on_serial_read)
            self.serial.write(b'Hello' + bytes('\n'.encode()))
            #self.serial.write(b'Start' + bytes('\n'.encode()))
        else:
            raise IOError("Cannot connect to device on port {}".format(port))


        print('COM PORT connected INFO')

    def choose_file(self):
        self.filename = QFileDialog.getOpenFileName()
        print('self.filename: ', self.filename[0])

        count = 0
        with open(self.filename[0], 'r') as f:
            for line in f:
                count += 1

        self.current = count
        self.current_label.setText(str(self.current))

    def on_serial_read(self):
        print('on_serial_read starting...')
        print('sensor_counter=', self.sensor_counter)
        print('scan_counter=  ', self.scan_counter)
        print('defect_counter=', self.defect_counter)
        readbytes = bytes(self.serial.readAll())

        print('readbytes: ', readbytes)

        if readbytes == b'Hello\r\n':
            self.comport_status_checkbox.setChecked(True)
            palette = QPalette()
            palette.setColor(QPalette.Base, QColor("#23F617"))
            self.comport_status_checkbox.setPalette(palette)
        elif readbytes == b'+1\r\n':
            self.product_passed_dt = datetime.now()
            print('product_passed_dt: ', self.product_passed_dt)
            self.sensor_counter = self.sensor_counter + 1

            if self.sensor_counter == self.scan_counter + 1 + self.defect_counter:
                print('norm scan')
            else:
                print('ne norm scan')
                self.defect_counter = self.defect_counter + 1

                self.serial.write(b'brak' + bytes('\n'.encode()))
        elif readbytes == b'ON\r\n':
            print('On processed')
        elif readbytes == b'OFF\r\n':
            print('OFF processed')

        print('on_serial_read finished')

    def scan(self, scan):
        scan_len = len(scan)
        print('scan : ', scan)
        print('scan len: ', scan_len)



        current_dt = datetime.now()
        duration = current_dt - self.product_passed_dt
        duration_in_ms = duration.total_seconds() * 1000

        print('duration_in_ms: ', duration_in_ms)
        # if duration_in_ms > 500:
        #     self.log('Прошло больше 500 мс! Отбраковано')
        #     print('Прошло больше 500 мс! Отбраковано WARN')
        #     msg = b'e\n'
        #     self.serial.write(msg)
        #     return
        #print('Скан успел пройти!')

        if scan_len <= 20:
            self.log('Маленькая длина! Отбраковано')
            print('Scan len <= 20 Warn')
            self.defect_counter = self.defect_counter + 1

            self.serial.write(b'brak' + bytes('\n'.encode()))
            return

        gs_pos = scan.find(chr(29))
        print('gs_pos = ', gs_pos)

        if gs_pos == -1:
            print('Нет символа GS Warn')
            self.log('Нет символа GS! Отбраковано')
            self.defect_counter = self.defect_counter + 1

            #self.serial.write(bytes([98, 114, 97, 107, 10]))  # brak/n
            self.serial.write(b'brak' + bytes('\n'.encode()))
            return

        print('Скан ок')

        date_time = datetime.now().strftime("%d.%m.%Y")
        self.filename = 'ki_' + self.name_label.text() + '_' + date_time + '.txt'

        if not os.path.exists(self.filename):
            os.mknod(self.filename)

        with open(self.filename) as f:
            if scan in f.read():
                print("дубликат!")
                self.log('Дубликат! Отбраковано')
                self.defect_counter = self.defect_counter + 1

                self.serial.write(b'brak' + bytes('\n'.encode()))
                return

        print("оригинальный!")
        self.scan_counter = self.scan_counter + 1

        with open(self.filename, "a") as myfile:
            myfile.write(scan + "\n")

        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 2, int(line_number), scan))
        self.log('Записан в файл. Подготовлен для отправки')
        self.current = self.current + 1
        self.current_label.setText(str(self.current))

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
        #self.serial.write(b'brak' + bytes('\n'.encode()))

        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(line_number), SERVER_ADDR))
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(line_number)))
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait info
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait start_signal

    def send_file(self):
        line_number = self.line_number_combobox.currentText()

        date_time = datetime.now().strftime("%d.%m.%Y")
        filename = 'ki_' + self.name_label.text() + '_' + date_time + '.txt'
        print("Подготовка к отправке файла ", filename)

        if not os.path.exists(filename):
            print("Файла нет!")
            return

        with open(filename, "r") as myfile:
            bytes = myfile.read()
            print("Считаны данные из файла ", bytes)
            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 3, int(line_number), bytes))
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

def create_thrift_server(thrift_client, transport):
    processor = SlaveController.Processor(thrift_client)

    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('thrift_server=starting info')
    server.serve()
    print('thrift_server=done info')

if __name__ == "__main__":
    ret = os.fork()
    if ret == 0:
        print('CHILD  scanner run pid        ', os.getpid())
        print('CHILD  scanner run parent pid ', os.getppid())
        fd = os.open('scanner.log', os.O_WRONLY | os.O_APPEND)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.execv("/home/avovana/build-scanner-Desktop-Debug/scanner", ["scanner"])
    elif ret > 0:
        print('PARENT sample  run pid        ', os.getpid())
        print('PARENT sample  run parent pid ', os.getppid())
        print('PARENTs child                 ', ret)
        app = QApplication(sys.argv)
        mainwindow = SlaveGui()
        thrift_impl = ThriftImpl()

        thrift_impl.scan_signal.connect(mainwindow.scan)
        thrift_impl.scanner_state_signal.connect(mainwindow.scanner_status)

        transport = TSocket.TServerSocket(host='localhost', port=9090)
        thread = Thread(target=create_thrift_server, args=(thrift_impl, transport))
        thread.start()

        mainwindow.show()
        app.exec_()
        # transport.close()
        # thread.join()
        os.kill(ret, 2)

        print('Waiting child to finish...')
        done = os.wait()
        print('Child finished: ', {done})
        # transport.close()
        thread.join()
        print('Thrift transport closed')
        mainwindow.client.join()
        #mainwindow.tcp_thread_event.clear()
        mainwindow.close()
        print('mainwindow transport closed')

    print('End pid        ', os.getpid())
    print('End parent pid ', os.getppid())
