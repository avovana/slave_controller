# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(612, 411)
        MainWindow.setStyleSheet("background-color: rgb(186, 189, 182);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.current_label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.current_label_2.setFont(font)
        self.current_label_2.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.current_label_2.setObjectName("current_label_2")
        self.gridLayout.addWidget(self.current_label_2, 4, 4, 1, 1)
        self.line_number_combobox = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.line_number_combobox.setFont(font)
        self.line_number_combobox.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.line_number_combobox.setObjectName("line_number_combobox")
        self.line_number_combobox.addItem("")
        self.gridLayout.addWidget(self.line_number_combobox, 0, 4, 1, 1)
        self.name_combobox = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_combobox.sizePolicy().hasHeightForWidth())
        self.name_combobox.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(26)
        self.name_combobox.setFont(font)
        self.name_combobox.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.name_combobox.setObjectName("name_combobox")
        self.gridLayout.addWidget(self.name_combobox, 5, 0, 1, 3)
        self.scanner_status_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.scanner_status_checkbox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.scanner_status_checkbox.setFont(font)
        self.scanner_status_checkbox.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.scanner_status_checkbox.setTristate(True)
        self.scanner_status_checkbox.setObjectName("scanner_status_checkbox")
        self.gridLayout.addWidget(self.scanner_status_checkbox, 0, 0, 1, 2)
        self.finish_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.finish_button.sizePolicy().hasHeightForWidth())
        self.finish_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.finish_button.setFont(font)
        self.finish_button.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.finish_button.setObjectName("finish_button")
        self.gridLayout.addWidget(self.finish_button, 7, 0, 1, 5)
        self.ready_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ready_button.sizePolicy().hasHeightForWidth())
        self.ready_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.ready_button.setFont(font)
        self.ready_button.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.ready_button.setObjectName("ready_button")
        self.gridLayout.addWidget(self.ready_button, 3, 0, 1, 5)
        self.choose_file_pushbutton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_file_pushbutton.sizePolicy().hasHeightForWidth())
        self.choose_file_pushbutton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.choose_file_pushbutton.setFont(font)
        self.choose_file_pushbutton.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.choose_file_pushbutton.setObjectName("choose_file_pushbutton")
        self.gridLayout.addWidget(self.choose_file_pushbutton, 1, 0, 1, 5)
        self.correct_file_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.correct_file_button.sizePolicy().hasHeightForWidth())
        self.correct_file_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.correct_file_button.setFont(font)
        self.correct_file_button.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.correct_file_button.setObjectName("correct_file_button")
        self.gridLayout.addWidget(self.correct_file_button, 6, 0, 1, 5)
        self.plan_label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.plan_label_2.setFont(font)
        self.plan_label_2.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.plan_label_2.setObjectName("plan_label_2")
        self.gridLayout.addWidget(self.plan_label_2, 4, 3, 1, 1)
        self.comport_status_checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.comport_status_checkbox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.comport_status_checkbox.setFont(font)
        self.comport_status_checkbox.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.comport_status_checkbox.setTristate(True)
        self.comport_status_checkbox.setObjectName("comport_status_checkbox")
        self.gridLayout.addWidget(self.comport_status_checkbox, 0, 2, 1, 1)
        self.connect_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connect_button.sizePolicy().hasHeightForWidth())
        self.connect_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.connect_button.setFont(font)
        self.connect_button.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.connect_button.setObjectName("connect_button")
        self.gridLayout.addWidget(self.connect_button, 2, 0, 1, 5)
        self.product_name_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.product_name_label.setFont(font)
        self.product_name_label.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.product_name_label.setObjectName("product_name_label")
        self.gridLayout.addWidget(self.product_name_label, 4, 0, 1, 3)
        self.line_number_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.line_number_label.setFont(font)
        self.line_number_label.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.line_number_label.setObjectName("line_number_label")
        self.gridLayout.addWidget(self.line_number_label, 0, 3, 1, 1)
        self.plan_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plan_label.sizePolicy().hasHeightForWidth())
        self.plan_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(64)
        self.plan_label.setFont(font)
        self.plan_label.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.plan_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plan_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.plan_label.setLineWidth(5)
        self.plan_label.setMidLineWidth(5)
        self.plan_label.setText("")
        self.plan_label.setObjectName("plan_label")
        self.gridLayout.addWidget(self.plan_label, 5, 3, 1, 1)
        self.current_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.current_label.sizePolicy().hasHeightForWidth())
        self.current_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(64)
        self.current_label.setFont(font)
        self.current_label.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.current_label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.current_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.current_label.setLineWidth(5)
        self.current_label.setMidLineWidth(5)
        self.current_label.setText("")
        self.current_label.setObjectName("current_label")
        self.gridLayout.addWidget(self.current_label, 5, 4, 1, 1)
        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exit_button.sizePolicy().hasHeightForWidth())
        self.exit_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.exit_button.setFont(font)
        self.exit_button.setStyleSheet("background-color: rgb(141, 255, 255);")
        self.exit_button.setObjectName("exit_button")
        self.gridLayout.addWidget(self.exit_button, 8, 0, 1, 5)
        self.text_browser = QtWidgets.QTextBrowser(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 254))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 169))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 254))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 254))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 169))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 254))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(238, 238, 254))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(147, 147, 169))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 110, 126))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(186, 189, 182))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(221, 221, 253))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.text_browser.setPalette(palette)
        self.text_browser.setObjectName("text_browser")
        self.gridLayout.addWidget(self.text_browser, 0, 7, 9, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 612, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.current_label_2.setText(_translate("MainWindow", "Факт"))
        self.line_number_combobox.setItemText(0, _translate("MainWindow", "0"))
        self.scanner_status_checkbox.setText(_translate("MainWindow", "Сканнер"))
        self.finish_button.setText(_translate("MainWindow", "Завершить. Отправить файл"))
        self.ready_button.setText(_translate("MainWindow", "Оповестить о готовности"))
        self.choose_file_pushbutton.setText(_translate("MainWindow", "Начать с прошлого файла"))
        self.correct_file_button.setText(_translate("MainWindow", "Корректировка"))
        self.plan_label_2.setText(_translate("MainWindow", "План"))
        self.comport_status_checkbox.setText(_translate("MainWindow", "Компорт"))
        self.connect_button.setText(_translate("MainWindow", "Подключиться"))
        self.product_name_label.setText(_translate("MainWindow", "Наименование продукции"))
        self.line_number_label.setText(_translate("MainWindow", "Номер линии"))
        self.exit_button.setText(_translate("MainWindow", "Выключить"))
