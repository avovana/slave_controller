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

import linecache
import signal

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from socketclientthread import SocketClientThread, ClientCommand, ClientReply

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
        scan = linecache.getline('/home/avovana/slave_controller/scans.txt', self.scan_number)
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

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     mainwindow = SampleGUIClientWindow()
#     mainwindow.show()
#     app.exec_()



class SlaveGui(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.create_client()

        self.ready_button.clicked.connect(self.send_ready)

        self.scanner_status_checkbox.setEnabled(False)

        self.create_timers()

        self.log("Started")

        signal.signal(signal.SIGTRAP, self.receiveSignal)

    def create_timers(self):
        self.client_reply_timer = QTimer(self)
        self.client_reply_timer.timeout.connect(self.on_client_reply_timer)
        self.client_reply_timer.start(100)

    def send_ready(self):
        self.client.cmd_q.put(ClientCommand(ClientCommand.CONNECT, 1, 7, SERVER_ADDR))
        self.client.cmd_q.put(ClientCommand(ClientCommand.SEND, 1, 7))
        self.client.cmd_q.put(ClientCommand(ClientCommand.RECEIVE))

    def on_client_reply_timer(self):
        try:
            reply = self.client.reply_q.get(block=False)
            status = "SUCCESS" if reply.type == ClientReply.SUCCESS else "ERROR"
            self.log('Client reply %s: %s' % (status, reply.data))
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

if __name__ == "__main__":


    print('My PID is:', os.getpid())

    app = QApplication(sys.argv)
    mainwindow = SlaveGui()
    mainwindow.show()
    app.exec_()
