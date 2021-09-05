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








# SERVER_ADDR = 'localhost', 50007
#SERVER_ADDR = '192.168.1.69', 6000
SERVER_ADDR = 'localhost', 6000
#SERVER_ADDR = '192.168.116.1', 6000

class CircleWidget(QWidget):
    def __init__(self, parent=None):
        super(CircleWidget, self).__init__(parent)
        self.nframe = 0
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(180, 180)

    def next(self):
        self.nframe += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(self.width() / 2, self.height() / 2)

        for diameter in range(0, 64, 9):
            delta = abs((self.nframe % 64) - diameter / 2)
            alpha = 255 - (delta * delta) / 4 - diameter
            if alpha > 0:
                painter.setPen(QPen(QColor(0, int(diameter / 2), 127, int(alpha)), 3))
                painter.drawEllipse(QRectF(
                    -diameter / 2.0,
                    -diameter / 2.0,
                    diameter,
                    diameter))


class LogWidget(QTextBrowser):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#ddddfd"))
        self.setPalette(palette)


class SampleGUIClientWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SampleGUIClientWindow, self).__init__(parent)

        self.scan_number = 1
        self.is_master_respond = True

        self.create_main_frame()
        self.create_client()
        self.create_timers()

    def create_main_frame(self):
        self.circle_widget = CircleWidget()
        self.doit_button = QPushButton('Do it!')
        self.label_name = QLabel()
        self.label_plan = QLabel()
        self.doit_button.clicked.connect(self.on_doit)
        self.log_widget = LogWidget()

        hbox = QHBoxLayout()
        hbox.addWidget(self.circle_widget)
        hbox.addWidget(self.doit_button)
        hbox.addWidget(self.log_widget)
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.label_plan)

        main_frame = QWidget()
        main_frame.setLayout(hbox)

        self.setCentralWidget(main_frame)

    def create_client(self):
        self.client = SocketClientThread()
        self.client.start()

    def create_timers(self):
        self.circle_timer = QTimer(self)
        self.circle_timer.timeout.connect(self.circle_widget.next)
        self.circle_timer.start(25)
        
        #self.circle_timer = QTimer(self)
        #self.circle_timer.timeout.connect(self.check_scan_file)
        #self.circle_timer.start(1000)

        self.client_reply_timer = QTimer(self)
        self.client_reply_timer.timeout.connect(self.on_client_reply_timer)
        self.client_reply_timer.start(100)

        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, 7, SERVER_ADDR))
        print("Going to send")
        #self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, 7, "9"))  # ready signal
        #self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE, 1, 7))

    def on_doit(self):
        print("Going to connect")
        #self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, SERVER_ADDR))
        #self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 'hello'))
        print("Going to receive")
        #self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))
        print("Going to close")
        #self.client.cmd_q.put(ClientCommand(ClientCommand.CLOSE))

    def check_scan_file(self):
        self.log('check_scan_file')
        # self.log('check_scan_file')
        scan = linecache.getline('/home/avovana/scans.txt', self.scan_number)
        #self.log('Scan number %i: %s' % (self.scan_number, scan))
        if scan and self.is_master_respond:
            self.log('Scan number %i: %s' % (self.scan_number, scan))
        #     """ насколько скане должен быть сохраняем? Что от него надо? Получить, отправить, дождаться(асинхронно?) ответа, написать. Пока ожидаем, брать ли новый скан? ПРостой случай - супер быстрая сеть и обработка на Ц ПК. Всё делаем последовательно. Не проверяем прохождение
        #      Просто есть:
        #                  скан -> сканнер -> driver scanner'a -> file
	    #                               			   file -> python обработчик
        #                                                         	   python обработчик ----------------------------> Ц ПК
        #                                                         	   python обработчик <---------------------------- Ц ПК
        #                                                         	   python обработчик -> GUI OK/not OK
	    #                               			   file -> python обработчик
        #     """
            self.scan_number += 1
            self.is_master_respond = False
            #self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, scan))
            self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, SERVER_ADDR))
            print("Going to send")
            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, b'\x04\x00\x00\x00'))
            self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))
        #
        # else:
        #     self.log('here')

    def on_client_reply_timer(self):
        try:
            reply = self.client.reply_q.get(block=False)
            status = "SUCCESS" if reply.type == ClientReply.SUCCESS else "ERROR"
            self.log('Client reply %s: %s' % (status, reply.data))
            print("   reply.type:", reply.type)
            print("   reply.data:", reply.data)

            msg_type = int.from_bytes(reply.data[0:4], byteorder='big', signed=False)
            reply.remove(0, 4)
            print("msg_type: ", msg_type)
            print("reply.data: ", reply.data)
            body = reply.data.decode()
            print("body: ", body)

            if msg_type == 4:
                self.name_label.setText(body.split(",")[0])
                self.plan_label.setText(body.split(",")[1])
            elif msg_type == 6:
                self.log('Можно начинать')
                #  self.name_label.setText(body.split(",")[0])

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

            #self.label_name.setText(reply.data.split(",")[0])
            #self.label_plan.setText(reply.data.split(",")[1])
        except queue.Empty:
            pass

    def log(self, msg):
        timestamp = '[%010.3f]' % time.process_time()
        self.log_widget.append(timestamp + ' ' + str(msg))

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
