#!/usr/bin/python
"""
based on:
Sample GUI using SocketClientThread for socket communication, while doing other
stuff in parallel.

Eli Bendersky (eliben@gmail.com)
This code is in the public domain
"""
import os
import queue
import design

from datetime import datetime
from threading import Thread
import threading

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

import yaml


class Config:
    def __init__(self):
        with open("config.yaml", "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        self.comport = self.config['comport']
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']
        self.scanner_path = self.config['scanner_path']
        self.line_number = self.config['line_number']

        print("self.comport: ", self.comport)
        print("self.host: ", self.host)
        print("self.port: ", self.port)
        print("self.scanner_path: ", self.scanner_path)


config = Config()
SERVER_ADDR = config.host, config.port

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

        self.connect_button.clicked.connect(self.send_connect)
        self.ready_button.clicked.connect(self.send_ready)
        self.finish_button.clicked.connect(self.send_file)
        self.choose_file_pushbutton.clicked.connect(self.choose_file)
        #self.choose_file_pushbutton.clicked.connect(self.send_scan_test)
        self.correct_file_button.clicked.connect(self.correct_file)
        self.name_combobox.currentTextChanged.connect(self.name_text_changed)
        self.exit_button.clicked.connect(self.exit)
        # self.choose_file_pushbutton.hide()

        self.scanner_status_checkbox.setEnabled(False)

        self.create_timers()

        self.sensor_counter = 0
        self.scan_counter = 0
        self.defect_counter = 0

        self.correct_file = False
        # self.connect_flag = False
        # self.send_ready_flag = False

        self.ki_filename = ""
        self.log("Started")

        self.product_passed_dt = datetime.now()

        self.tasks = {}

        # body = "1,prod1,20;2,prod2,30"
        #
        # tasks = body.split(";")
        #
        # for idx, value in enumerate(tasks):
        #     task, name, plan = value.split(",")
        #     self.tasks[task] = (name, plan)
        #
        # self.log(tasks)

        #-----------------Serial Port-----------------
        available_ports = QSerialPortInfo.availablePorts()

        for port in available_ports:
            print('port: ', port.portName())

        if len(available_ports) == 0:
            self.log("Ошибка! Нет доступных ком портов!")

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Нет доступных ком портов!")
            msgBox.setWindowTitle("Предупреждение")
            msgBox.setStandardButtons(QMessageBox.Ok)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                print('OK clicked')

            return
        self.line_number_combobox.setItemText(0, str(config.line_number))
        self.line_number_combobox.setEnabled(False)

        port = available_ports[config.comport].portName()  # port = "ttyS1"
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

    def exit(self):
        print('in exit')
        self.exit_button.setStyleSheet("background-color: green")
        self.close()

    def name_text_changed(self, str):
        print('str: ', str)
        plan, task = self.tasks.get(str)
        print('plan: ', plan)
        print('task: ', task)

    def choose_file(self):
        ki_filename_dialog = QFileDialog.getOpenFileName()
        self.ki_filename = ki_filename_dialog[0]
        print('ki filename: ', self.ki_filename)

        self.log("Файл для сканов: %s" % self.ki_filename)

        count = 0
        with open(self.ki_filename, 'r') as f:
            for line in f:
                count += 1

        self.scan_counter = count
        self.sensor_counter = count
        self.current_label.setText(str(self.scan_counter))

    def send_scan_test(self):
        scan = "0104629418600327215/lfI,933yJ9"
        self.scan(scan)

    def correct_file(self):
        if not self.correct_file:
            self.correct_file = True
            self.log('Режим корректировки включен')
            self.correct_file_button.setStyleSheet("background-color: green")
        else:
            self.correct_file = False
            self.correct_file_button.setStyleSheet("background-color: rgb(141, 255, 255)")
            self.log('Режим корректировки выключен')

    def on_serial_read(self):
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
            self.sensor_counter = self.sensor_counter + 1

            current_dt = datetime.now()
            duration = current_dt - self.product_passed_dt
            duration_in_ms = duration.total_seconds() * 1000
            print('duration_in_ms: ', duration_in_ms)

            if self.sensor_counter == self.scan_counter + self.defect_counter:
                print('previously scanner read scan success')
            else:
                print('previously scanner read scan failed')
                self.defect_counter = self.defect_counter + 1
                self.serial.write(b'brak' + bytes('\n'.encode()))  #  self.serial.write(bytes([98, 114, 97, 107, 10]))  # brak/n
        elif readbytes == b'ON\r\n':
            print('On processed')
        elif readbytes == b'OFF\r\n':
            print('OFF processed')

    def scan(self, scan):
        scan_len = len(scan)
        print('scan : ', scan)

        if self.correct_file:
            lines = []
            with open(self.ki_filename) as f:
                lines = f.readlines()

            print('lines : ', lines)
            lines.remove(scan + "\n")

            with open(self.ki_filename, 'w') as f:
                for line in lines:
                    f.write(line)

            self.scan_counter = self.scan_counter - 1
            self.current_label.setText(str(self.scan_counter))

            return

        self.product_passed_dt = datetime.now()
        print('product_passed_dt: ', self.product_passed_dt)

        if scan_len <= 20:
            self.log('Маленькая длина! Будет отбраковано')
            print('Scan len <= 20 Warn')
            return

        gs_pos = scan.find(chr(29))
        print('gs_pos = ', gs_pos)

        if gs_pos == -1:
            print('Нет символа GS Warn')
            self.log('Нет символа GS! Будет отбраковано')
            return

        if not os.path.exists(self.ki_filename):
            os.mknod(self.ki_filename)

        with open(self.ki_filename) as f:
            if scan in f.read():
                print("дубликат!")
                self.log('Дубликат! Будет отбраковано')
                return

        print("Скан валидный")
        self.scan_counter = self.scan_counter + 1
        self.serial.write(b'good' + bytes('\n'.encode()))

        with open(self.ki_filename, "a") as ki_file:
            ki_file.write(scan + "\n")

        self.log('Скан записан в файл. Подготовлен для отправки')
        self.current_label.setText(str(self.scan_counter))

        product = self.name_combobox.currentText()
        task, plan = self.tasks.get(product)
        print("current name: ", product)
        print("task: ", task)

        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 2, int(line_number), self.current_label.text(), int(task)))
        print("Отправлено оповещение об инкременте скана")

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

    def send_connect(self):
        self.connect_button.setStyleSheet("background-color: green")
        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(line_number), SERVER_ADDR))

    def send_ready(self):
        self.ready_button.setStyleSheet("background-color: green")
        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(line_number)))
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait info

    def send_file(self):
        self.finish_button.setStyleSheet("background-color: green")
        line_number = self.line_number_combobox.currentText()

        product = self.name_combobox.currentText()
        task, plan = self.tasks.get(product)
        print("current name: ", product)
        print("task: ", task)

        date_time = datetime.now().strftime("%d.%m.%Y")
        print("Подготовка к отправке файла ", self.ki_filename)

        if not os.path.exists(self.ki_filename):
            print("Файла нет!")
            return

        with open(self.ki_filename, "r") as ki_file:
            read_bytes = ki_file.read()
            print("Считаны данные из файла ", read_bytes)
            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 3, int(line_number), read_bytes, int(task)))
            self.log('Файл отправляется')

    def on_client_reply_timer(self):
        try:
            reply = self.client.reply_q.get(block=False)

            if reply.type == ClientReply.CONNECTED:
                self.log('Установлена связь')
                return
            elif reply.type == ClientReply.ERROR:
                self.log("ОШИБКА: %s" % reply.data)
                return

            self.log("УСПЕШНО: %s" % reply.data)

            #if reply.data is None:
            #    return

            print("type: 3", type(reply.data))
            # first4bytes = b'\x00\x00\x00\x04'  #  reply.data[0:4]
            first4bytes = reply.data[0:4]

            print("type: 4", type(first4bytes))
            msg_type = int.from_bytes(first4bytes, byteorder='big', signed=False)
            print("msg_type", msg_type)
            print("msg_type", type(msg_type))
            print("type: 5", type(reply.data))
            print("type: 6", type(reply.data))
            print("type: 7", type(reply.data[4:len(reply.data)]))
            print("type: 8", type(reply.data[4:len(reply.data)].decode())) # м.б. я делаю операцию по ссылке? а думал, что по копии
            # print("msg_type: ", msg_type)
            # print("reply.data: ", reply.data)
            # print("len(reply.data): ", len(reply.data))
            # print("reply.data[4:len(reply.data) - 4 - 1]: ", reply.data[4:len(reply.data)])
            # print("len(reply.data[4:len(reply.data) - 4 - 1]): ", len(reply.data[4:len(reply.data)]))
            body = reply.data[4:len(reply.data)].decode()
            print("body ", type(body))
            print("body: ", body)

            if msg_type == 4:
                tasks = body.split(";")[0]
                print("tasks: ", tasks)

                task, name, plan = tasks.split(",")
                self.tasks[name] = (task, plan)
                # for idx, value in enumerate(tasks):
                #     task, name, plan = value.split(",")
                #     self.tasks[name] = (task, plan)
                #     print("name: ", name)
                #     print("task: ", task)
                #     print("plan: ", plan)
                #     self.name_combobox.addItem(name)

                # plan, task = self.tasks.get(str)
                print('plan: ', plan)
                print('task: ', task)
                print('name: ', name)

                self.name_combobox.addItem(name)
                date_time = datetime.now().strftime("%d.%m.%Y-%H:%M")
                self.ki_filename = self.ki_filename if self.ki_filename != "" else 'ki_' + self.name_combobox.currentText() + '_' + date_time + '.txt'
                self.log('Файл для сканов: %s' % self.ki_filename)
                self.plan_label.setText(plan)
                self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))  # Wait start_signal
                self.log('Ожидание стартового сигнала...')
            elif msg_type == 6:
                self.log('Можно начинать')
            elif msg_type == 8:
                self.log('Задачи еще не созданы')
        except queue.Empty:
            pass

    def log(self, msg):
        timestamp = '[%010.3f]' % time.process_time()
        self.text_browser.append(timestamp + ' ' + str(msg))


def create_thrift_server(thrift_client, transport):
    processor = SlaveController.Processor(thrift_client)

    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print('thrift_server=starting info')
    server.serve()
    print('thrift_server=done info')

if __name__ == "__main__":
    with open("interface.pid", "r") as pid_file:
        pid = pid_file.read()
        print("prev interface pid: ", pid)

    with open("scanner.pid", "r") as pid_file:
        pid = pid_file.read()
        print("prev child pid: ", pid)

    ret = os.fork()
    if ret == 0:
        with open("scanner.pid", "w") as child_pid:
            child_pid.write(str(os.getpid()))

        print('CHILD pid        ', os.getpid())
        fd = os.open('scanner.log', os.O_CREAT | os.O_WRONLY | os.O_APPEND)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        print('pid ', os.getpid())
        os.execv(config.scanner_path, ["scanner"])
    elif ret > 0:
        with open("interface.pid", "w") as interface_pid:
            interface_pid.write(str(os.getpid()))

        print('PARENT pid       ', os.getpid())
        print('PARENT parent pid', os.getppid())
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

    print('Program finished')
    # os.system("shutdown now -h")
