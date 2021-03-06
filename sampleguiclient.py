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
import random
import string
import psycopg2

import time
from shutil import copyfile

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
import xml.etree.ElementTree as ET

class Config:
    def __init__(self):
        with open("config.yaml", "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        self.comport = self.config['comport']
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']
        self.postgres_host = self.config['postgres']['host']
        self.postgres_user = self.config['postgres']['user']
        self.postgres_password = self.config['postgres']['password']
        self.postgres_write_to_db = self.config['postgres']['write_to_db']
        self.scanner_path = self.config['scanner_path']
        self.position_path = self.config['position_path']
        self.line_number = self.config['line_number']
        self.check_group_code = self.config['check_group_code']
        self.check_comport = self.config['check_comport']
        self.company = self.config['company_name']
        self.auto_start_same_product = self.config['auto_start_same_product']
        self.test = self.config['test']

        print("__config__")
        print(" comport: ", self.comport)
        print(" host: ", self.host)
        print(" port: ", self.port)
        print(" scanner_path: ", self.scanner_path)
        print(" position_path: ", self.position_path)
        print(" check_group_code: ", self.check_group_code)
        print(" check_comport: ", self.check_comport)
        print(" postgres_host: ", self.postgres_host)
        print(" postgres_user: ", self.postgres_user)
        print(" postgres_password: ", self.postgres_password)
        print(" postgres_write_to_db: ", self.postgres_write_to_db)
        print(" auto_start_same_product: ", self.auto_start_same_product)
        print(" test: ", self.test)


config = Config()
SERVER_ADDR = config.host, config.port

class LogWidget(QTextBrowser):
    def __init__(self, parent=None):
        super(LogWidget, self).__init__(parent)
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor("#ddddfd"))
        self.setPalette(palette)


class XMLparser:
    def __init__(self):
        self.root_node = ET.parse(config.position_path).getroot()

    def get_rus_name(self, eng_name):
        for tag in self.root_node.findall('input/position'):
            if eng_name == tag.attrib['name_english']:
                # print("name rus: ", tag.attrib['name'])
                return tag.attrib['name']

    def get_eng_name(self, rus_name):
        for tag in self.root_node.findall('input/position'):
            if rus_name == tag.attrib['name']:
                # print(" name eng: ", tag.attrib['name_english'])
                return tag.attrib['name_english']

    def get_rus_names(self):
        names = []
        for tag in self.root_node.findall('input/position'):
            names.append(tag.attrib['name'])
        # print("names: ", names)
        return names

    def get_group_code(self, eng_name):
        for tag in self.root_node.findall('input/position'):
            if eng_name == tag.attrib['name_english']:
                # print(" group_code: ", tag.attrib['group_code'])
                return tag.attrib['group_code']


class ScanValidator:
    def __init__(self, scan):
        # print('__ScanValidator__')
        # print(' scan : ', scan)
        self.scan = scan
        self.scan_len = len(self.scan)

    def check_len(self):
        if self.scan_len <= 20:
            # print(' Scan len <= 20 Warn')
            return False
        else:
            return True

    def check_gs(self):
        gs_pos = self.scan.find(chr(29))
        # print(' gs_pos = ', gs_pos)

        if gs_pos == -1:
            # print(' ?????? ?????????????? GS Warn')
            return False
        else:
            return True

    def check_dublicate(self, file_path):
        with open(file_path) as f:
            if self.scan in f.read():
                print(" ????????????????!")
                return False
        return True

    def check_group(self, group):
        if group not in self.scan:
            # print(" ?????? ???????????? ?? ??????????")
            return False
        return True

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

        self.xml_parser = XMLparser()

        self.tcp_thread_event = threading.Event()
        self.tcp_thread_event.set()

        self.client = SocketClientThread(self.tcp_thread_event)
        self.client.start()

        self.connect_button.clicked.connect(self.send_connect)
        self.ready_button.clicked.connect(self.send_ready)
        self.finish_button.clicked.connect(self.send_file)
        if not config.test:
            self.choose_file_pushbutton.clicked.connect(self.choose_file)
        else:
            self.choose_file_pushbutton.clicked.connect(self.send_scan_test)
        self.correct_file_button.clicked.connect(self.correct_file)
        self.name_combobox.currentIndexChanged.connect(self.name_index_changed)
        self.start_button.clicked.connect(self.start_work)
        self.exit_button.clicked.connect(self.exit)
        # self.auto_button.clicked.connect(self.auto_handling)
        # self.choose_file_pushbutton.hide()
        # self.auto_choose_combobox.hide()
        # self.start_auto_button.hide()
        self.apply_colores()
        self.scanner_status_checkbox.setEnabled(False)

        self.create_timers()

        self.sensor_counter = 0
        self.scan_counter = 0
        self.defect_counter = 0
        self.scan_read_success = False
        self.m_scanner_status = ScannerStatus.Stop

        self.correct_file = False
        # self.connect_flag = False
        # self.send_ready_flag = False
        self.auto_state = False
        self.scan_can_be_read_now = False
        self.scans_wait_to_proceed = []

        self.py_script_path = os.path.dirname(os.path.realpath(__file__))
        self.ki_filename = ""
        self.today_folder = "ki/" + datetime.now().strftime("%d-%m")
        os.makedirs(self.today_folder, exist_ok=True)

        os.chdir(self.today_folder)
        self.log("?????????? ??????????????????")

        self.product_passed_dt = datetime.now()

        self.tasks = {}
        self.index_to_task_n = {}

        self.line_number_combobox.setItemText(0, str(config.line_number))
        self.line_number_combobox.setEnabled(False)

        #-----------------Serial Port-----------------
        available_ports = QSerialPortInfo.availablePorts()

        for port in available_ports:
            print('port: ', port.portName())

        if len(available_ports) == 0:
            self.log("????????????! ?????? ?????????????????? ?????? ????????????!")

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("?????? ?????????????????? ?????? ????????????!")
            msgBox.setWindowTitle("????????????????????????????")
            msgBox.setStandardButtons(QMessageBox.Ok)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                print('OK clicked')

            return

        port = available_ports[config.comport].portName()  # port = "ttyS1"
        self.serial = QSerialPort(self)
        self.serial.setPortName(port)
        if self.serial.open(QIODevice.ReadWrite):
            self.serial.setBaudRate(9600)
            self.serial.clear()
            self.serial.readyRead.connect(self.on_serial_read)
            self.serial.write(b'Hello' + bytes('\n'.encode()))
            print(" Send to comport: ", "Hello")
            #self.serial.write(b'Start' + bytes('\n'.encode()))
        else:
            self.log("????????????! ???? ???????????????????? ???????????????????????? ?? ?????? ??????????!")

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("?????? ?????????????????????? ?? ?????? ??????????. ???????????????????? ?????????????????????????? ?????????????????? ?????? ????.")
            msgBox.setWindowTitle("????????????????????????????")
            msgBox.setStandardButtons(QMessageBox.Ok)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                print('OK clicked')
                self.exit()

    def exit(self):
        print('in exit')
        self.exit_button.setStyleSheet("background-color: rgb(66, 193, 152)")
        self.close()

    def apply_colores(self):
        if config.company == "imperia":
            self.scanner_status_checkbox.setStyleSheet("QCheckBox{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.comport_status_checkbox.setStyleSheet("QCheckBox{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.line_number_label.setStyleSheet("QLabel{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.line_number_combobox.setStyleSheet("QComboBox{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.connect_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.ready_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.start_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.product_name_label.setStyleSheet("QLabel{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.plan_label_2.setStyleSheet("QLabel{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.current_label_2.setStyleSheet("QLabel{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.name_combobox.setStyleSheet("QComboBox{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.product_name_label.setStyleSheet("QLabel{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.plan_label.setStyleSheet("QLabel{font-size: 64px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.current_label.setStyleSheet("QLabel{font-size: 64px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.choose_file_pushbutton.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.correct_file_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.finish_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")
            self.exit_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")


    def auto_handling(self):
        self.auto_choose_combobox.show()
        self.start_auto_button.show()
        self.auto_choose_combobox.addItems(self.xml_parser.get_rus_names())
        self.connect_button.hide()
        self.ready_button.hide()
        self.auto_state = True

    def name_index_changed(self, index):
        print(' name_index_changed:')
        # print('  index = ', index)
        # print('  current index = ', self.name_combobox.currentIndex())

        if index == -1:
            print('  empty name_combobox')
            self.ready_button.setStyleSheet("background-color: rgb(66, 193, 152);")
            return

        task_n = self.index_to_task_n.get(index)
        # print('  task_n: ', task_n)
        eng_name, date, task_n, plan = self.tasks.get(task_n)

        rus_name_and_date = self.xml_parser.get_rus_name(eng_name) + ":" + date

        self.plan_label.setText(plan)
        print(" Task name {0}, number {1}, date {2}".format(eng_name, task_n, date))
        self.log(' ?????????????? ??????????????: %s' % rus_name_and_date)

    def get_current_task_info(self):

        task_n = self.index_to_task_n.get(self.name_combobox.currentIndex())
        eng_name, date, task_n, plan = self.tasks.get(task_n)
        # print(' current task: ', eng_name)
        # print('  date: ', date)
        # print('  eng_name: ', eng_name)
        # print('  plan: ', plan)
        # print('  task: ', task_n)

        return eng_name, task_n, plan, date

    def start_work(self):
        print('Start: ')
        # self.choose_file_pushbutton.setDisabled(True)
        self.name_combobox.setDisabled(True)
        self.start_button.setDisabled(True)
        self.finish_button.setStyleSheet("QPushButton{font-size: 18px;font-family: Arial;color: rgb(255, 255, 255);background-color: rgb(92, 99, 118);}")

        eng_name, task_n, plan, date = self.get_current_task_info()

        # print(' task: ', task_n, eng_name)
        print(" Task name {0}, number {1}.".format(eng_name, task_n))
        date_time = datetime.now().strftime("%H-%M")
        self.ki_filename = self.ki_filename if self.ki_filename != "" else eng_name + '__' + date_time + '.csv'
        self.log('???????? ?????? ????????????: %s' % self.ki_filename)
        self.log('????????: %s' % date)
        # self.log('???????????????? ???????????????????? ?????????????? ?????? %s' % self.name_combobox.currentText())
        # self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE, 10000))  # Wait start_signal

        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 4, int(line_number), self.current_label.text(), int(task_n)))
        self.log_success('?????????????????? ???????????? ?? ???????????? ????????????')
        print(" ???????????????????? ???????????????????? ?? ???????????? ???????????? ?? ????????????????")

    def choose_file(self):
        ki_filename_dialog = QFileDialog.getOpenFileName()
        self.ki_filename = ki_filename_dialog[0]
        print('ki filename: ', self.ki_filename)

        self.log("???????? ?????? ????????????: %s" % self.ki_filename)

        count = 0
        with open(self.ki_filename, 'r') as f:
            for line in f:
                count += 1

        self.scan_counter = count
        self.sensor_counter = count
        self.current_label.setText(str(self.scan_counter))

    def send_scan_test(self):
        # scan = "0104629418600167215/lfI,933yJ9"

        # scan = "0104629418600167215/lfI,"
        # scan = scan.join([random.choice(string.ascii_letters) for n in range(6)])

        scan = "0104629418600167215/lfI,933yJ"
        scan = scan + random.choice(string.ascii_letters)
        self.scan(scan)

    def correct_file(self):
        if not self.correct_file:
            self.correct_file = True
            self.log('?????????? ?????????????????????????? ??????????????')
            self.correct_file_button.setStyleSheet("background-color: rgb(66, 193, 152)")
        else:
            self.correct_file = False
            self.correct_file_button.setStyleSheet("background-color: rgb(66, 193, 152)")
            self.log('?????????? ?????????????????????????? ????????????????')

    def on_serial_read(self):
        readbytes = bytes(self.serial.readAll())

        print('Read from comport: ', readbytes)

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
            # print('duration_in_ms: ', duration_in_ms)

            #if self.sensor_counter == self.scan_counter + self.defect_counter:
            if self.scan_read_success:
                print(' Scan passed success')
                self.scan_read_success = False
            else:
                print(' Scan passed fail')
                self.defect_counter = self.defect_counter + 1
                self.serial.write(b'brak' + bytes('\n'.encode()))  #  self.serial.write(bytes([98, 114, 97, 107, 10]))  # brak/n
                print(" Send to comport: ", "brak")
        elif readbytes == b'ON\r\n':
            print(' On processed')
        elif readbytes == b'OFF\r\n':
            print(' OFF processed')

        print(' sensor counter = ', self.sensor_counter)
        print(' scan counter   = ', self.scan_counter)
        print(' defect counter = ', self.defect_counter)

    def scan(self, scan):
        print('Scan received:')
        print('', scan)

        # if not self.scan_can_be_read_now:
        #     print(' wait for self.scan_can_be_read_now')
        #     self.scans_wait_to_proceed.append(scan_)
        #     print(' scan added to list', scan_)
        #     print(' list size', len(self.scans_wait_to_proceed))
        #     return
        # else:
        #     self.scans_wait_to_proceed.append(scan_)
        #     print(' added to list', scan_)


        # for scan in self.scans_wait_to_proceed:
        if config.auto_start_same_product:
            if not self.ki_filename:
                self.start_work()
        else:
            if not self.ki_filename:
                self.log_error("?????? ??????????! ???????????????????? ???????????? \"????????????\" ?????? ???????????????? ??????????")
                return


        if self.correct_file:
            lines = []
            with open(self.ki_filename) as f:
                lines = f.readlines()

            print(' lines : ', lines)
            lines.remove(scan + "\n") # if we didn't find it?

            with open(self.ki_filename, 'w') as f:
                for line in lines:
                    f.write(line)

            self.scan_counter = self.scan_counter - 1
            self.current_label.setText(str(self.scan_counter))

            eng_name, task_n, plan, date = self.get_current_task_info()

            line_number = self.line_number_combobox.currentText()
            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 2, int(line_number), self.current_label.text(), int(task_n)))
            print(" ???????????????????? ???????????????????? ???? ??????????????????????????")
            return

        self.product_passed_dt = datetime.now()
        # print(' product_passed_dt: ', self.product_passed_dt)

        scan_validator = ScanValidator(scan)

        if not scan_validator.check_len():
            self.log('?????????????????? ??????????, ???? ???????????????????????? ??????????????, ???? ???????????? ?? ????????')
            return

        if not scan_validator.check_gs():
            self.log('?????? ?????????????? GS! ?????????? ??????????????????????')
            return

        eng_name, task_n, plan, date = self.get_current_task_info()

        os.chdir(self.py_script_path)
        this_task_folder = "ki/" + date
        os.makedirs(this_task_folder, exist_ok=True)

        os.chdir(this_task_folder)

        if not os.path.exists(self.ki_filename):
            os.mknod(self.ki_filename)

        if not scan_validator.check_dublicate(self.ki_filename):
            self.log('????????????????, ???? ???????????? ?? ????????')
            return

        if config.check_group_code:
            group_code = self.xml_parser.get_group_code(eng_name)
            if not scan_validator.check_group(group_code):
                self.log('???? ?????????????????????????? ???????????????? ????????????')
                return

        self.scan_counter = self.scan_counter + 1
        print(" ???????? ????????????????. ??? " + str(self.scan_counter))
        self.scan_read_success = True
        self.serial.write(b'good' + bytes('\n'.encode()))
        print(" Send to comport: ", "good")

        with open(self.ki_filename, "a") as ki_file:
            ki_file.write(scan + "\n")

        self.log('???????? ' + str(self.scan_counter) + ' ?????????????? ?? ????????')
        self.current_label.setText(str(self.scan_counter))
        self.current_label.setText(str(self.scan_counter))

        line_number = self.line_number_combobox.currentText()
        self.write_db(line_number, eng_name, date, self.scan_counter, plan)

        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 2, int(line_number), self.current_label.text(), int(task_n)))
        # print(" ???????????????????? ???????????????????? ???? ???????????????????? ??????????")

        if config.auto_start_same_product and self.scan_counter == int(plan):
            # self.scan_can_be_read_now = False # wait until answer OK received and "start" is pushed = new file is ready
            print(" auto send")
            self.send_file()
            time.sleep(2)

        # self.scans_wait_to_proceed.clear()
        # print(' end read scan. list size = ', len(self.scans_wait_to_proceed))
    def write_db(self, line_number, eng_name, release_date, current, plan):
        if config.postgres_write_to_db:
            conn = None
            try:
                conn = psycopg2.connect(user=config.postgres_user, password=config.postgres_password, host=config.postgres_host)

                cur = conn.cursor()
                cur.execute("insert into production (line, production, current, plan) values (%s, %s, %s, %s)", (line_number, self.xml_parser.get_rus_name(eng_name) + ":" + release_date, current, plan))
                conn.commit()
                cur.close()
                print(" write to db")
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()

    def scanner_status(self, status):
        self.m_scanner_status = status
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
        if not config.test:
            if self.m_scanner_status == ScannerStatus.Stop:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("???????????? ???? ??????????????????!")
                msgBox.setWindowTitle("????????????????????????????")
                msgBox.setStandardButtons(QMessageBox.Ok)

                returnValue = msgBox.exec()
                if returnValue == QMessageBox.Ok:
                    print('OK clicked')
                    return

        self.connect_button.setStyleSheet("background-color: rgb(66, 193, 152)")
        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(line_number), SERVER_ADDR))

    def send_ready(self):
        print("__send_ready__")
        self.ready_button.setStyleSheet("background-color: rgb(66, 193, 152)")
        line_number = self.line_number_combobox.currentText()
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(line_number)))
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE,10000))  # Wait info

    def send_file(self):
        print("Send file:")
        self.finish_button.setStyleSheet("background-color: rgb(66, 193, 152)")

        line_number = self.line_number_combobox.currentText() # TODO -> self.line_number

        # name_rus = self.name_combobox.currentText()
        # name_eng = self.xml_parser.get_eng_name(name_rus) if not self.auto_state else self.xml_parser.get_eng_name(self.auto_choose_combobox.currentText())
        # print(" current name_rus: ", name_rus)
        # print("         name_eng: ", name_eng)
        #
        # task, plan, date = self.tasks.get(name_eng)
        # print(" task: ", task)
        # print(" plan: ", plan)
        # print(" date: ", date)

        date_time = datetime.now().strftime("%d.%m.%Y")

        eng_name, task_n, plan, date = self.get_current_task_info()

        print(" ???????????????????? ?? ???????????????? ?????????? ", self.ki_filename)

        if not os.path.exists(self.ki_filename):
            print(" ?????????? ??????!")
            return

        with open(self.ki_filename, "r") as ki_file:
            counter = 0
            read_bytes = ki_file.read()
            paired_list = read_bytes.split("\n")

            for i in paired_list:
                if i:
                    counter += 1

            print(" scans: ", counter)
            # print(" ?????????????? ???????????? ???? ?????????? ", read_bytes)

            self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 3, int(line_number), read_bytes, int(task_n)))
            self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE,7))  # Wait confirm, 3 for file... # better 3 means sec # no 3 timeout socket attempts
            self.log(' ???????? ????????????????????????. ?????????????????? ?????????????????????????? ????????????????...')

        # rename if wasn't
        if "line_N" not in self.ki_filename:
            count_substr = str(counter) + "__" + "line_N" + str(config.line_number) + "__"
            idx_to_insert = len(self.ki_filename) - 9
            new_name = self.ki_filename[:idx_to_insert] + count_substr + self.ki_filename[idx_to_insert:]
            print(" filename: ", self.ki_filename)

            # os.rename(self.ki_filename, new_name)
            copyfile(self.ki_filename, new_name)
            os.remove(self.ki_filename)
            self.ki_filename = new_name
            self.log(' ???????? ???????????????????????? ?? %s' % self.ki_filename)
            print(" saved with new name: ", self.ki_filename)
        else:
            print(" already renamed!")


    def on_client_reply_timer(self):
        try:
            reply = self.client.reply_q.get(block=False)
            print("Reply:")

            if reply.type == ClientReply.CONNECTED:
                self.log_success('?????????????????????? ??????????')
                return
            elif reply.type == ClientReply.ERROR:
                # if reply.data == "socket_closed":
                #     self.log("????????????: ???????????????????? ??????????????????. ???????????????????? ????????????????????????????????")
                if reply.data == "connection_error":
                    self.log_error("???????????? ????????????????????")
                    self.log_error("????????????: ?????? ????????????. ???????????? ????????????????????????????????")
                    self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(config.line_number), SERVER_ADDR))
                    self.finish_button.setStyleSheet("background-color: rgb(66, 193, 152);")
                    # while working not needed to request data after connection recover
                    # self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(config.line_number)))
                    # self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE, 10000))  # Wait info
                # elif reply.data == "[Errno 32] Broken pipe":
                #     self.log("?????????????????? ??????????! ???????????????????? ???????? ?????????? ????????????????, ???? ???? ?????????? ??????????????????!")
                #     print("[Errno 32] Broken pipe")
                elif reply.data == "send_error":
                    self.log_error("???????????? ????????????????. ???????????? ????????????????????????????????")
                    self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, int(config.line_number), SERVER_ADDR))
                    self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, int(config.line_number)))
                    self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE, 10000))  # Wait info
                else:
                    self.log_error("????????????: %s" % reply.data)
                return

            #self.log("%s" % reply.data)

            #if reply.data is None:
            #    return

            # print("type: 3", type(reply.data))
            # first4bytes = b'\x00\x00\x00\x04'  #  reply.data[0:4]
            first4bytes = reply.data[0:4]

            # print("type: 4", type(first4bytes))
            msg_type = int.from_bytes(first4bytes, byteorder='big', signed=False)
            # print("msg_type", msg_type)
            # print("msg_type", type(msg_type))
            # print("type: 5", type(reply.data))
            # print("type: 6", type(reply.data))
            # print("type: 7", type(reply.data[4:len(reply.data)]))
            # print("type: 8", type(reply.data[4:len(reply.data)].decode())) # ??.??. ?? ?????????? ???????????????? ???? ????????????? ?? ??????????, ?????? ???? ??????????

            # print("msg_type: ", msg_type)
            # print("reply.data: ", reply.data)
            # print("len(reply.data): ", len(reply.data))
            # print("reply.data[4:len(reply.data) - 4 - 1]: ", reply.data[4:len(reply.data)])
            # print("len(reply.data[4:len(reply.data) - 4 - 1]): ", len(reply.data[4:len(reply.data)]))
            body = reply.data[4:len(reply.data)].decode()
            # print("body ", type(body)) # str
            # print(" body: ", body)

            if msg_type == 4:
                # tasks = body.split(";")[0]
                tasks = body.split(";")
                print(" New tasks received: ", tasks)

                for task in tasks:
                    #print(' ', task)

                    task_n, eng_name, plan, date = task.split(":")
                    self.tasks[task_n] = (eng_name, date, task_n, plan)

                    print(' plan: ', plan)
                    print(' task: ', task_n)
                    print(' name: ', eng_name)
                    print(' date: ', date)

                    self.log(' ?????????????????? ??????????????: %s' % self.xml_parser.get_rus_name(eng_name) + ":" + date)
                    print(' added task: ', self.xml_parser.get_rus_name(eng_name) + ":" + date)
                    print(' index going to be: ', self.name_combobox.count())
                    self.index_to_task_n[self.name_combobox.count()] = task_n
                    self.name_combobox.addItem(self.xml_parser.get_rus_name(eng_name) + ":" + date)
                    line_number = self.line_number_combobox.currentText()
                    self.write_db(line_number, eng_name, date, 0, plan)

                self.log('?????????????? ?????????????? ?? ???????????? \"????????????\"')
                # self.log('???????????????? ???????????????????? ?????????????? ?????? %s' % self.xml_parser.get_rus_name(eng_name) + ":" + date)
            elif msg_type == 8:
                print(" Tasks not created yet")
                self.log_error('???????????? ?????? ???? ??????????????')
            elif msg_type == 10:
                # print(' File send OK')
                # print(' current index = ', self.name_combobox.currentIndex())
                # print(' current text = ', self.name_combobox.currentText())
                self.log_success(' ???????? ??????????????????. ?????????????? ??????????????????.')

                self.name_combobox.setDisabled(False)
                self.start_button.setDisabled(False)
                self.ki_filename = ""

                self.finish_button.setStyleSheet("background-color: rgb(66, 193, 152);")
                self.current_label.setText("")
                self.plan_label.setText("")
                self.scan_counter = 0
                self.defect_counter = 0
                self.sensor_counter = 0

                # remove from map current index (0)
                # get index with the same product name (1)
                # set new index as current (1)
                # remove prev index (0)
                # current that is 1 will came 0

                # =>
                # remember product name
                # remove from map current index (0)
                # all indexes will change
                # map will be invalidated
                # will be invalidated only those that were after it
                # 0 1 2 3 4 5
                #       |
                # =>
                # 0 1 2   4 5
                #       |
                # =>
                # 0 1 2 3 4
                #       |
                # So I need to -1 every that is after him:
                # should find them(4,5), remove from the map, remove this finished(3), mimus them 4-1, 5-1 and added to the map

                # what we gonna do next?...
                # Index switch to the same product
                last_index = self.name_combobox.count() - 1 # 5
                curr_index = self.name_combobox.currentIndex() # 3
                curr_text = self.name_combobox.itemText(curr_index)

                for index in range(self.name_combobox.count()): # 0 -> 5
                    if index == curr_index:
                        del self.index_to_task_n[self.name_combobox.currentIndex()] # remove key = 3
                    if index > curr_index:
                        self.index_to_task_n[index - 1] = self.index_to_task_n.get(index)

                self.name_combobox.removeItem(self.name_combobox.currentIndex())

                for i in range(self.name_combobox.count()):
                    if self.name_combobox.itemText(i) == curr_text:
                        print(' i...........', i)
                        self.name_combobox.setCurrentIndex(i)

                # if config.auto_start_same_product and self.name_combobox.count() != 0:
                #     self.start_work()
        #         Let it send file or fail. New file will be created with new scan income

        except queue.Empty:
            pass

    def log(self, msg):
        # time_t = datetime.now().time()
        time_t = datetime.now().strftime('%H:%M:%S')
        timestamp = '[%010.3f]' % time.process_time()
        # self.text_browser.append(timestamp + ' ' + str(msg))
        cursor = self.text_browser.textCursor()
        cursor.insertHtml('''<p><span style="color: black;">{0} {1} </span><br>'''.format(time_t, msg))
        cursor = self.text_browser.textCursor()
        self.text_browser.moveCursor(QTextCursor.End)

    def log_success(self, msg):
        # time_t = datetime.now().time()
        time_t = datetime.now().strftime('%H:%M:%S')
        timestamp = '[%010.3f]' % time.process_time()
        cursor = self.text_browser.textCursor()
        cursor.insertHtml('''<p><span style="font-size: 18pt; color: rgb(66, 193, 152);">{0} {1} </span><br>'''.format(time_t, msg))
        self.text_browser.moveCursor(QTextCursor.End)
        # self.text_browser.append(timestamp + ' ' + str(msg))

    def log_error(self, msg):
        time_t = datetime.now().strftime('%H:%M:%S')
        # time_t = datetime.now().time()
        timestamp = '[%010.3f]' % time.process_time()
        cursor = self.text_browser.textCursor()
        cursor.insertHtml('''<p><span style="font-size: 18pt; color: red;">{0} {1} </span><br>'''.format(time_t, msg))
        self.text_browser.moveCursor(QTextCursor.End)


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
