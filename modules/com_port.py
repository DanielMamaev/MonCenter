import serial
import sys
import glob
from PyQt5.QtCore import QThread
from PyQt5 import QtGui
from datetime import datetime

from modules.show_logs import ShowLogs

class ComPort():

    def __init__(self, main):
        super().__init__()
        self.main = main

        self.realport = None
        self.receivedMessage = None  # ХРАНИТ ПРИХОДЯЩЕЕ СООБЩЕНИЕ С КОМ ПОРТА
        self.button_com_flag = True  # ФЛАГ ДЛЯ ПОДКЛЮЧЕНИЯ К КОМ ПОРТУ
        self.command_list = ['#ser', '#num', '#ip', '#tcp_res', '#restart',
                             '#reset']  # КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ WEMOS ЧЕРЕЗ КОМ ПОРТ
        self.read_text_Thread_instance = ReadTextThread(mainwindow=main)

        self.logs = ShowLogs(parent=main)


    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def connect(self):
        if self.button_com_flag:
            try:
                self.realport = serial.Serial(
                    self.main.comboBox_port.currentText(), int(self.main.comboBox_speed.currentText()))
                self.main.pushButton_connect.setText("Disconnect")
                self.logs.show_logs("Connected")
                self.main.lineEdit_send.setFocus()
                self.read_text_Thread_instance.start()
                self.button_com_flag = False
            except Exception as e:
                self.logs.show_logs(str(e))
        else:
            self.realport.close()
            self.realport = None

            self.logs.show_logs("Disconnected")
            self.button_com_flag = True
            self.main.pushButton_connect.setText("Connect")

    def send(self):
        if self.realport:
            send_text = self.main.comboBox_comm.currentText()
            self.realport.write(bytearray(send_text, 'utf8'))
        self.main.comboBox_comm.setEditText("")

    def clear(self):
        self.main.textEdit_read.clear()

    def update(self):
        # ДОБАВЛЕНИЕ НАЙДЕННЫХ ПОРТОВ В COMBOBOX
        self.main.comboBox_port.clear()
        self.main.comboBox_port.addItems(self.serial_ports())
        self.main.comboBox_str2str_in_ser_port.clear()
        self.main.comboBox_str2str_in_ser_port.addItems(self.serial_ports())
        self.main.comboBox_str2str_out_ser_port.clear()
        self.main.comboBox_str2str_out_ser_port.addItems(self.serial_ports())
        self.main.comboBox_str2str_out_ser_port_2.clear()
        self.main.comboBox_str2str_out_ser_port_2.addItems(self.serial_ports())
        self.main.comboBox_str2str_out_ser_port_3.clear()
        self.main.comboBox_str2str_out_ser_port_3.addItems(self.serial_ports())
        


# ДАННЫЙ КЛАСС НУЖЕН ДЛЯ ЧТЕНИЯ ДАННЫХ С COM ПОРТА В ОТДЕЛЬНОМ ПОТОКЕ
class ReadTextThread(QThread):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

        self.mainwindow.pushButton_log_com.clicked.connect(
            self.com_log)  # ОБРАБОТКА НАЖАТИЯ КНОПКИ START LOG ВО ВКЛАДКЕ COM
        self.log_flag = True  # ФЛАГ СОСТОЯНИЯ КНОПКИ
        self.log_write = False  # ФЛАГ СОСТОЯНИЯ ЗАПИСИ В ФАЙЛ

        self.name_f = None
        self.f = None
        self.logs = ShowLogs(parent=mainwindow)

    def run(self):
        while True:
            try:
                if self.mainwindow.realport:  # ЕСЛИ ПОКЛЮЧЕНЫ К КОМ ПОРТУ
                    self.mainwindow.receivedMessage = self.mainwindow.realport.readline().decode(
                        'ascii')  # ЧИТАЕМ ДАННЫЕ С КОМ ПОРТА

                    if self.mainwindow.receivedMessage != "":
                        if self.mainwindow.checkBox_time.isChecked():
                            today = datetime.today().strftime("%H.%M.%S")
                            self.mainwindow.textEdit_read.append(
                                today + " -> " + self.mainwindow.receivedMessage)
                            if self.log_write:
                                self.f = open(self.name_f, "a")
                                today = datetime.today().strftime("%H.%M.%S")
                                self.f.write(
                                    today + "-> " + self.mainwindow.receivedMessage + "\n")
                                self.f.close()
                        else:
                            self.mainwindow.textEdit_read.append(
                                self.mainwindow.receivedMessage)
                            if self.log_write:
                                self.f = open(self.name_f, "a")
                                self.f.write(
                                    self.mainwindow.receivedMessage + "\n")
                                self.f.close()

                        if self.mainwindow.checkBox_scroll.isChecked():
                            self.mainwindow.textEdit_read.moveCursor(
                                QtGui.QTextCursor.End)
                        self.mainwindow.receivedMessage = ""

            except Exception as e:
                self.logs.show_logs(str(e))

    def com_log(self):
        if self.log_flag:
            self.mainwindow.pushButton_log_com.setText("Stop Log")
            today = datetime.today().strftime("%d%m%y-%H%M%S")
            self.name_f = "logs/com/COM-Log-" + today + ".txt"
            self.f = open(self.name_f, "w")
            self.f.close()
            self.log_flag = False
            self.log_write = True
        else:
            self.mainwindow.pushButton_log_com.setText("Start Log")
            self.log_write = False
            self.log_flag = True