import sys
import glob

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QUrl, QDateTime
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog

import design
import serial
import os.path
import configparser
import sqlite3
import psutil
from datetime import datetime, time, timedelta

import smtplib
from email.mime.text import MIMEText
from email.header import Header

from ftplib import FTP
import yadisk
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import time


def serial_ports():
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


# ******************************************* MAIN *******************************************
class LedApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_update()
        self.action_exit.triggered.connect(self.ini_save_exit)

        # ------------- .INI
        self.path_ini = "conf.ini"
        self.action_save_config.triggered.connect(self.ini_save)
        self.action_reset_config.triggered.connect(self.ini_reset)
        self.ini_start()

        # -------------STR2STR
        self.filename_tcpcli = ""
        self.path_tcpcli = ""
        self.tcpcli_list = []

        self.filename_tcpsvr = ""
        self.path_tcpsvr = ""

        self.filename_ntrip = ""
        self.ntrip_list = []
        self.path_ntrip = ""

        self.action_start_str2str.triggered.connect(self.str2str_start)  # СТАРТ TCP CLIENT
        self.action_stop_str2str.triggered.connect(self.str2str_stop)
        self.action_close_xterm.triggered.connect(self.str2str_stop_xterm)
        self.Button_str2str_in_file.clicked.connect(self.str2str_inputfile_path)
        self.Button_str2str_out_file.clicked.connect(self.str2str_outputfile_path)
        self.Button_str2str_out_file_2.clicked.connect(self.str2str_outputfile_path_2)
        self.Button_str2str_out_file_3.clicked.connect(self.str2str_outputfile_path_3)
        self.tab_output1.setEnabled(False)
        self.tab_output2.setEnabled(False)
        self.tab_output3.setEnabled(False)
        self.checkBox_str2str_out1.stateChanged.connect(self.str2str_flag_output1)
        self.checkBox_str2str_out2.stateChanged.connect(self.str2str_flag_output2)
        self.checkBox_str2str_out3.stateChanged.connect(self.str2str_flag_output3)

        # -------------CONVBIN
        self.Button_convert.clicked.connect(self.convbin_convert)
        self.Button_input.clicked.connect(self.convbin_input_path)
        self.Button_obs.clicked.connect(self.convbin_obs_path)
        self.Button_nav.clicked.connect(self.convbin_nav_path)
        self.Button_convbin_gnav.clicked.connect(self.convbin_gnav_path)
        self.Button_convbin_hnav.clicked.connect(self.convbin_hnav_path)
        self.Button_convbin_qnav.clicked.connect(self.convbin_qnav_path)
        self.Button_convbin_lnav.clicked.connect(self.convbin_lnav_path)
        self.Button_convbin_sbas.clicked.connect(self.convbin_sbas_path)

        self.format = ['rtcm2', 'rtcm3', 'nov', 'oem3', 'ubx', 'ss2', 'hemis', 'stq', 'javad', 'nvs', 'binex', 'rinex',
                       'rt17']
        self.comboBox_format.addItems(self.format)

        self.rinex_ver = ['3.03', '3.02', '3.01', '3.0', '2.12', '2.11', '2.10']
        self.comboBox_rinex.addItems(self.rinex_ver)

        self.freq_list = ['1', '2']
        self.comboBox_freq.addItems(self.freq_list)

        self.fname_input = ""
        self.convbin_list = []

        self.checkBox_convbin_obs.stateChanged.connect(self.convbin_check_obs)
        self.checkBox_convbin_nav.stateChanged.connect(self.convbin_check_nav)
        self.checkBox_convbin_gnav.stateChanged.connect(self.convbin_check_gnav)
        self.checkBox_convbin_hnav.stateChanged.connect(self.convbin_check_hnav)
        self.checkBox_convbin_qnav.stateChanged.connect(self.convbin_check_qnav)
        self.checkBox_convbin_lnav.stateChanged.connect(self.convbin_check_lnav)
        self.checkBox_convbin_sbas.stateChanged.connect(self.convbin_check_sbas)
        self.checkBox_time_start.stateChanged.connect(self.convbin_check_time_start)
        self.checkBox_time_end.stateChanged.connect(self.convbin_check_time_end)

        # -------------RNX2RTKP
        self.Button_rnx2rtkp_input_conf.clicked.connect(self.rnx2rtkp_input_conf)
        self.Button_rnx2rtkp_input_rover.clicked.connect(self.rnx2rtkp_input_rover)
        self.Button_rnx2rtkp_input_base.clicked.connect(self.rnx2rtkp_input_base)
        self.Button_rnx2rtkp_input_nav.clicked.connect(self.rnx2rtkp_input_nav)
        self.Button_rnx2rtkp_output.clicked.connect(self.rnx2rtkp_output)
        self.Button_rnx2rtkp_start.clicked.connect(self.rnx2rtkp_input_start)

        self.lineEdit_rnx2rtkp_conf.setText("")

        self.fname_input_rnx2rtkp = ""
        self.fname_output_pos = ""

        self.checkBox_rnx2rtkp_conf.stateChanged.connect(self.rxn2rtkp_conf_file_check)
        self.checkBox_rnx2rtkp_time_start.stateChanged.connect(self.rnx2rtkp_time_start_check)
        self.checkBox_rnx2rtkp_time_end.stateChanged.connect(self.rnx2rtkp_time_end_check)

        # ------------- DATABASE
        self.Button_db_new_create.clicked.connect(self.db_create)
        self.Button_db_new_path.clicked.connect(self.db_path_new)
        self.Button_db_con_path.clicked.connect(self.db_path_connect)
        self.Button_db_connect.clicked.connect(self.db_connect)
        self.Button_db_start.clicked.connect(self.db_start_str2str)
        self.Button_db_save.clicked.connect(self.db_dir_save)
        self.Button_db_stop.clicked.connect(self.db_stop)
        self.open_db = sqlite3.connect("")
        self.db_connect()
        self.post_pro_db = []
        self.bool_ok_db = False
        self.temp_time_db = 0

        self.time_reset_str2str_Thread_instance = TimeResetStr2strThread(mainwindow=self)
        self.time_reset_str2str_Thread_instance.start()

        self.checkBox_db_reset.stateChanged.connect(self.db_check_str2str)
        self.checkBox_db_post.stateChanged.connect(self.db_check_post)
        self.Button_db_timepost_ok.clicked.connect(self.db_posttime)
        self.Button_db_sql.clicked.connect(self.db_sql_command)


        # ------------- COM
        self.realport = None
        self.action_refresh_ports.triggered.connect(self.serial_update)
        self.pushButton_connect.clicked.connect(self.com_connect)  # ОБРАБОТКА ПОДКЛЮЧЕНИЯ К ПОРТУ
        self.pushButton_refresh.clicked.connect(self.com_refresh)  # ПОИСК НОВЫХ ПОРТОВ
        self.pushButton_send.clicked.connect(self.com_send)  # ОТПРАВКА СООБЩЕНИЯ
        self.pushButton_clear.clicked.connect(self.com_clear)  # ЧИСТКА ОКНА ПРИХОДЯЩИХ ДАННЫХ С КОМ ПОРТА
        self.receivedMessage = None  # ХРАНИТ ПРИХОДЯЩЕЕ СООБЩЕНИЕ С КОМ ПОРТА
        self.button_com_flag = True  # ФЛАГ ДЛЯ ПОДКЛЮЧЕНИЯ К КОМ ПОРТУ
        self.command_list = ['#ser', '#num', '#ip', '#tcp_res', '#restart',
                             '#reset']  # КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ WEMOS ЧЕРЕЗ КОМ ПОРТ
        self.comboBox_comm.addItems(self.command_list)  # ДОБАВЛЕНИЕ КОМАНД В COMBOBOX
        self.read_text_Thread_instance = ReadTextThread(mainwindow=self)  # ЗАПУСК ПОТОКА ЧТЕНИЯ ДАННЫХ ИЗ КОМ ПОРТА

        #self.ftp_connect("")




    def serial_update(self):
        self.comboBox_port.addItems(serial_ports())  # ДОБАВЛЕНИЕ НАЙДЕННЫХ ПОРТОВ В COMBOBOX
        self.comboBox_str2str_in_ser_port.addItems(serial_ports())
    # *************************** SHOW LOGS ***************************
    def show_logs(self, text):
        print("\n" + text)
        today = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
        self.plainTextEdit_logs.appendPlainText(str(today) + " -> " + text)
        f = open("logs/program/logs.txt", "a")
        f.write(str(today) + " -> " + text + "\n")
        f.close()

    # *************************** E-MAIL ***************************
    def send_email(self, message):
        email = "moncenter.result@gmail.com"
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.starttls()
        smtp_obj.login(email, 'tsoekbtboewzuxyy')

        now = datetime.today().strftime("%m.%d.%Y-%H:%M:%S")
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = Header(now, 'utf-8')
        msg['From'] = email
        msg['To'] = self.lineEdit_settings_email.text()
        if not self.lineEdit_settings_email.text() == "":
            smtp_obj.sendmail(msg['From'], self.lineEdit_settings_email.text(), msg.as_string())
            smtp_obj.quit()
        else:
            self.show_logs("Не указана электронная почта для отправки уведомлений.")

    # *************************** Google Drive ***************************
    """def delete_all_gdrive(self):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        service_account_file = self.lineEdit_settings_google_json.text()
        try:
            credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        except Exception:
            self.show_logs("Файл не найден, либо проблема с файлом json")
        else:
            service = build('drive', 'v3', credentials=credentials)
            results = service.files().list(pageSize=10, fields="files(id, name)", ).execute()
            list_res = results['files']
            print(list_res)
            for i in range(len(list_res)):
                service.files().delete(fileId=list_res[i]['id']).execute()"""

    def gdrive_connect(self, path):
        # Подключение к Google Drive

        SCOPES = ['https://www.googleapis.com/auth/drive']
        service_account_file = self.lineEdit_settings_google_json.text()
        try:
            credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        except Exception:
            self.show_logs("Файл не найден, либо проблема с файлом json")
        else:
            service = build('drive', 'v3', credentials=credentials)
            # Список файлов на диске в корневой папке
            # results = service.files().list(pageSize=10,
            # fields="nextPageToken, files(id, name, mimeType, createdTime, quotaBytesUsed )", ).execute()
            # Создание папки
            folder_id = self.lineEdit_settings_google_id.text()
            today = datetime.today().strftime("%m.%d.%y")
            date = str(today.day) + str(today.month) + str(today.year)

            results = service.files().list(pageSize=10, fields="files(id, name)", ).execute()
            list_res = results['files']

            bool_name_folder = False
            for i in range(len(list_res)):
                if list_res[i]['name'] == date:
                    bool_name_folder = True
                    folder_id = list_res[i]['id']

            if not bool_name_folder:
                name = date
                file_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [folder_id]
                }
                try:
                    r = service.files().create(body=file_metadata, fields='id, name').execute()
                except Exception:
                    self.show_logs("Не удалось создать новую папку")
                else:
                    folder_id = r['id']

            # Загрузка файла измерений
            self.show_logs("Загрузка файла измерений")
            name = os.path.basename(path)
            file_path = path
            file_metadata = {
                'name': name,
                'parents': [folder_id]
            }

            media = ""
            try:
                media = MediaFileUpload(file_path, resumable=True)
            except Exception:
                self.show_logs("Не удалось загрузить файл измерений")
            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            except Exception:
                self.show_logs("Неверный id папки")

            # Загрузка файла базы данных
            self.show_logs("Загрузка файла базы данных")
            name = os.path.basename(self.lineEdit_db_con_path.text())
            file_path = self.lineEdit_db_con_path.text()
            file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
            media = ""
            try:
                media = MediaFileUpload(file_path, resumable=True)
            except Exception:
                self.show_logs("Не удалось загрузить файл базы данных")

            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            except Exception:
                self.show_logs("Неверный id папки")

    # *************************** YA.DISK ***************************
    def yadisk_connect(self, path):
        ya = yadisk.YaDisk(token=self.lineEdit_settings_ya_token.text())
        if ya.check_token():
            try:
                a = list(ya.listdir(self.lineEdit_settings_ya_folder.text()))
            except Exception:
                self.show_logs("Dir is not found!")

            else:
                today = datetime.today().strftime("%m.%d.%y")
                date = str(today.day) + str(today.month) + str(today.year)
                try:
                    ya.mkdir(self.lineEdit_settings_ya_folder.text() + date + "/")
                except Exception:
                    pass

                try:
                    ya.upload(path, self.lineEdit_settings_ya_folder.text() + date + "/" + os.path.basename(path))
                except Exception:
                    self.show_logs("Загрузить не удалось!")
                else:
                    self.show_logs("Загрузка " + os.path.basename(path) + " на Яндекс.Диск.")

                try:
                    ya.upload(self.lineEdit_db_con_path.text(),
                              self.lineEdit_settings_ya_folder.text() + date + "/" + "database.db")
                except Exception:
                    self.show_logs("...")
                else:
                    self.show_logs("Загрузка базы данных на Яндекс.Диск.")

    # *************************** FTP ***************************

    def ftp_connect(self, path):
        ftp = ''
        try:
            ftp = FTP(self.lineEdit_settings_ftp_host.text())
            ftp.login(self.lineEdit_settings_ftp_username.text(), self.lineEdit_settings_ftp_password.text())
        except Exception as e:
            self.show_logs("Проблема с подключением к FTP серверу " + str(e))
        else:
            self.show_logs("К FTP серверу подключились.")
            #print(ftp.retrlines('LIST')) # отображение всех файлов в каталоге
            #print(ftp.pwd()) # текущий путь

            today = datetime.today().strftime("%m.%d.%y")
            flag_dir = False
            try:
                ftp.mkd(today) # создание папки
            except Exception as e:
                if str(e) == "550 Directory already exists":
                    self.show_logs("Папка уже созадана: " + str(e))
                    flag_dir = True
                else:
                    self.show_logs("Проблема с созданием папки: " + str(e))
                    return
            else:
                flag_dir = True
                self.show_logs('Папка создана')
                #print(ftp.retrlines('LIST'))

            if flag_dir:
                try:
                    ftp.cwd('/' + today)
                except Exception as e:
                    self.show_logs("Такой папки /" + today + "не существует: " + str(e))
                    return
                else:
                    try:
                        ftp.storbinary('STOR ' + os.path.basename(path), open(path, "rb"))
                    except Exception as e:
                        self.show_logs("Проблема с загрузкой файла: " + str(e))

                try:
                    ftp.storbinary('STOR ' + os.path.basename(self.lineEdit_db_con_path.text()),
                                   open(self.lineEdit_db_con_path.text(), "rb"))
                except Exception as e:
                    self.show_logs("Проблема с загрузкой БД: " + str(e))
        ftp.close()


            # *************************** FILE .INI ***************************

    def ini_save_exit(self):
        self.ini_save()
        sys.exit()

    def ini_reset(self):
        config = configparser.ConfigParser()
        try:
            config.read(self.path_ini)
            config.set("STR2STR", "create_folder", "False")
            config.set("STR2STR", "autoclose_xterm", "False")
            config.set("CONVBIN", "check_start", "False")
            config.set("CONVBIN", "check_end", "False")
            config.set("CONVBIN", "format", "rtcm2")
            config.set("CONVBIN", "rinex", "3.03")
            config.set("CONVBIN", "frequencies", "1")
            config.set("CONVBIN", "sat_gps", "False")
            config.set("CONVBIN", "sat_glo", "False")
            config.set("CONVBIN", "sat_galileo", "False")
            config.set("CONVBIN", "sat_qzss", "False")
            config.set("CONVBIN", "sat_sbas", "False")
            config.set("CONVBIN", "sat_beidou", "False")
            config.set("CONVBIN", "check_obs", "False")
            config.set("CONVBIN", "check_nav", "False")
            config.set("CONVBIN", "check_gnav", "False")
            config.set("CONVBIN", "check_hnav", "False")
            config.set("CONVBIN", "check_qnav", "False")
            config.set("CONVBIN", "check_lnav", "False")
            config.set("CONVBIN", "check_sbas", "False")
            config.set("RNX2RTKP", "pos_mode", "Single")
            config.set("RNX2RTKP", "frequencies", "L1")
            config.set("RNX2RTKP", "sol_format", "Lat/Lon/Height (deg/m)")
            config.set("RNX2RTKP", "time_format", "yyyy/mm/dd hh:mm:ss.ss")
            config.set("RNX2RTKP", "mask", "")
            config.set("RNX2RTKP", "decimals", "")
            config.set("RNX2RTKP", "base_station", "Lat/Lon/Height (deg/m)")
            config.set("RNX2RTKP", "edit1", "")
            config.set("RNX2RTKP", "edit2", "")
            config.set("RNX2RTKP", "edit3", "")
            config.set("COM", "speed", "9600")
            config.set("COM", "autoscroll", "False")
            config.set("COM", "time", "False")
            config.set("DATABASE", "time_reset", "False")
            config.set("DATABASE", "time_post", "False")
            config.set("DATABASE", "last_post", "False")
            config.set("DATABASE", "connect_to", "")
            config.set("DATABASE", "save_to", "")
            config.set("DATABASE", "delta", "")
            config.set("SETTINGS", "email", "")
            config.set("SETTINGS", "ftp_host", "")
            config.set("SETTINGS", "ftp_username", "")
            config.set("SETTINGS", "ftp_password", "")
            config.set("SETTINGS", "ftp_autoconnect", "False")
            config.set("SETTINGS", "ya_token", "")
            config.set("SETTINGS", "ya_folder", "")
            config.set("SETTINGS", "ya_autoconnect", "False")
            config.set("SETTINGS", "google_json", "")
            config.set("SETTINGS", "google_id", "")
            config.set("SETTINGS", "google_autoconnect", "False")
            config.set("SETTINGS", "output_str_active", "False")
        except Exception:
            self.show_logs("The file conf.ini is corrupted or not found.")
        else:
            with open(self.path_ini, "w") as config_file:
                config.write(config_file)
            self.ini_start()

    def ini_save(self):
        config = configparser.ConfigParser()
        try:
            config.read(self.path_ini)
            config.set("STR2STR", "create_folder", str(self.action_create_folder.isChecked()))
            config.set("STR2STR", "autoclose_xterm", str(self.action_autoclose_xterm.isChecked()))
            config.set("CONVBIN", "check_start", str(self.checkBox_time_start.isChecked()))
            config.set("CONVBIN", "check_end", str(self.checkBox_time_end.isChecked()))
            config.set("CONVBIN", "format", self.comboBox_format.currentText())
            config.set("CONVBIN", "rinex", self.comboBox_rinex.currentText())
            config.set("CONVBIN", "frequencies", self.comboBox_freq.currentText())
            config.set("CONVBIN", "sat_gps", str(self.checkBox_gps.isChecked()))
            config.set("CONVBIN", "sat_glo", str(self.checkBox_glo.isChecked()))
            config.set("CONVBIN", "sat_galileo", str(self.checkBox_galileo.isChecked()))
            config.set("CONVBIN", "sat_qzss", str(self.checkBox_qzss.isChecked()))
            config.set("CONVBIN", "sat_sbas", str(self.checkBox_sbas.isChecked()))
            config.set("CONVBIN", "sat_beidou", str(self.checkBox_beidou.isChecked()))
            config.set("CONVBIN", "check_obs", str(self.checkBox_convbin_obs.isChecked()))
            config.set("CONVBIN", "check_nav", str(self.checkBox_convbin_nav.isChecked()))
            config.set("CONVBIN", "check_gnav", str(self.checkBox_convbin_gnav.isChecked()))
            config.set("CONVBIN", "check_hnav", str(self.checkBox_convbin_hnav.isChecked()))
            config.set("CONVBIN", "check_qnav", str(self.checkBox_convbin_qnav.isChecked()))
            config.set("CONVBIN", "check_lnav", str(self.checkBox_convbin_lnav.isChecked()))
            config.set("CONVBIN", "check_sbas", str(self.checkBox_convbin_sbas.isChecked()))
            config.set("RNX2RTKP", "pos_mode", self.comboBox_rnx2rtkp_pos_mode.currentText())
            config.set("RNX2RTKP", "frequencies", self.comboBox_rnx2rtkp_freq.currentText())
            config.set("RNX2RTKP", "sol_format", self.comboBox_rnx2rtkp_sol_format.currentText())
            config.set("RNX2RTKP", "time_format", self.comboBox_rnx2rtkp_time_format.currentText())
            config.set("RNX2RTKP", "mask", self.lineEdit_rnx2rtkp_mask.text())
            config.set("RNX2RTKP", "decimals", self.lineEdit_rnx2rtkp_dec.text())
            config.set("RNX2RTKP", "base_station", self.comboBox_rnx2rtkp_base.currentText())
            config.set("RNX2RTKP", "edit1", self.lineEdit_rnx2rtkp_1.text())
            config.set("RNX2RTKP", "edit2", self.lineEdit_rnx2rtkp_2.text())
            config.set("RNX2RTKP", "edit3", self.lineEdit_rnx2rtkp_3.text())
            config.set("COM", "speed", self.comboBox_speed.currentText())
            config.set("COM", "autoscroll", str(self.checkBox_scroll.isChecked()))
            config.set("COM", "time", str(self.checkBox_time.isChecked()))
            config.set("DATABASE", "time_reset", str(self.checkBox_db_reset.isChecked()))
            config.set("DATABASE", "time_post", str(self.checkBox_db_post.isChecked()))
            config.set("DATABASE", "last_post", str(self.checkBox_db_lastpost.isChecked()))
            config.set("DATABASE", "connect_to", self.lineEdit_db_con_path.text())
            config.set("DATABASE", "save_to", self.lineEdit_db_save.text())
            config.set("DATABASE", "delta", self.lineEdit_db_delta.text())
            config.set("SETTINGS", "email", self.lineEdit_settings_email.text())
            config.set("SETTINGS", "ftp_host", self.lineEdit_settings_ftp_host.text())
            config.set("SETTINGS", "ftp_username", self.lineEdit_settings_ftp_username.text())
            config.set("SETTINGS", "ftp_password", self.lineEdit_settings_ftp_password.text())
            config.set("SETTINGS", "ftp_autoconnect", str(self.checkBox_settings_ftp_autoconnect.isChecked()))
            config.set("SETTINGS", "ya_token", self.lineEdit_settings_ya_token.text())
            config.set("SETTINGS", "ya_folder", self.lineEdit_settings_ya_folder.text())
            config.set("SETTINGS", "ya_autoconnect", str(self.checkBox_settings_ya_autoconnect.isChecked()))
            config.set("SETTINGS", "google_json", self.lineEdit_settings_google_json.text())
            config.set("SETTINGS", "google_id", self.lineEdit_settings_google_id.text())
            config.set("SETTINGS", "google_autoconnect", str(self.checkBox_settings_google_autoconnect.isChecked()))
            config.set("SETTINGS", "output_str_active", str(self.action_debug_stream.isChecked()))
        except Exception:
            self.show_logs("The file conf.ini is corrupted or not found.")
        else:
            with open(self.path_ini, "w") as config_file:
                config.write(config_file)

    def ini_start(self):
        if not os.path.exists(self.path_ini):
            self.show_logs("The file conf.ini does not exist!")
            
            return

        config = configparser.ConfigParser()
        config.read(self.path_ini)

        try:
            # --- STR2STR
            self.action_create_folder.setChecked(config.getboolean("STR2STR", "create_folder"))
            self.action_autoclose_xterm.setChecked(config.getboolean("STR2STR", "autoclose_xterm"))

            # --- CONVBIN
            self.checkBox_time_start.setChecked(config.getboolean("CONVBIN", "check_start"))
            self.checkBox_time_end.setChecked(config.getboolean("CONVBIN", "check_end"))
            self.comboBox_format.setCurrentText(config.get("CONVBIN", "format"))
            self.comboBox_rinex.setCurrentText(config.get("CONVBIN", "rinex"))
            self.comboBox_freq.setCurrentText(config.get("CONVBIN", "frequencies"))

            self.checkBox_gps.setChecked(config.getboolean("CONVBIN", "sat_gps"))
            self.checkBox_glo.setChecked(config.getboolean("CONVBIN", "sat_glo"))
            self.checkBox_galileo.setChecked(bool(config.getboolean("CONVBIN", "sat_galileo")))
            self.checkBox_qzss.setChecked(bool(config.getboolean("CONVBIN", "sat_qzss")))
            self.checkBox_sbas.setChecked(bool(config.getboolean("CONVBIN", "sat_sbas")))
            self.checkBox_beidou.setChecked(bool(config.getboolean("CONVBIN", "sat_beidou")))

            self.checkBox_convbin_obs.setChecked(config.getboolean("CONVBIN", "check_obs"))
            self.checkBox_convbin_nav.setChecked(config.getboolean("CONVBIN", "check_nav"))
            self.checkBox_convbin_gnav.setChecked(config.getboolean("CONVBIN", "check_gnav"))
            self.checkBox_convbin_hnav.setChecked(config.getboolean("CONVBIN", "check_hnav"))
            self.checkBox_convbin_qnav.setChecked(config.getboolean("CONVBIN", "check_qnav"))
            self.checkBox_convbin_lnav.setChecked(config.getboolean("CONVBIN", "check_lnav"))
            self.checkBox_convbin_sbas.setChecked(config.getboolean("CONVBIN", "check_sbas"))

            # --- RNX2RTKP
            self.comboBox_rnx2rtkp_pos_mode.setCurrentText(config.get("RNX2RTKP", "pos_mode"))
            self.comboBox_rnx2rtkp_freq.setCurrentText(config.get("RNX2RTKP", "frequencies"))
            self.comboBox_rnx2rtkp_sol_format.setCurrentText(config.get("RNX2RTKP", "sol_format"))
            self.comboBox_rnx2rtkp_time_format.setCurrentText(config.get("RNX2RTKP", "time_format"))
            self.lineEdit_rnx2rtkp_mask.setText(config.get("RNX2RTKP", "mask"))
            self.lineEdit_rnx2rtkp_dec.setText(config.get("RNX2RTKP", "decimals"))
            self.comboBox_rnx2rtkp_base.setCurrentText(config.get("RNX2RTKP", "base_station"))
            self.lineEdit_rnx2rtkp_1.setText(config.get("RNX2RTKP", "edit1"))
            self.lineEdit_rnx2rtkp_2.setText(config.get("RNX2RTKP", "edit2"))
            self.lineEdit_rnx2rtkp_3.setText(config.get("RNX2RTKP", "edit3"))

            # --- COM
            self.comboBox_speed.setCurrentText(config.get("COM", "speed"))
            self.checkBox_scroll.setChecked(config.getboolean("COM", "autoscroll"))
            self.checkBox_time.setChecked(config.getboolean("COM", "time"))

            # --- DATABASE
            self.checkBox_db_reset.setChecked(config.getboolean("DATABASE", "time_reset"))
            self.checkBox_db_post.setChecked(config.getboolean("DATABASE", "time_post"))
            self.checkBox_db_lastpost.setChecked(config.getboolean("DATABASE", "last_post"))
            self.lineEdit_db_con_path.setText(config.get("DATABASE", "connect_to"))
            self.lineEdit_db_save.setText(config.get("DATABASE", "save_to"))
            self.lineEdit_db_delta.setText(config.get("DATABASE", "delta"))
            if self.checkBox_db_reset.isChecked():
                self.timeEdit_db.setEnabled(True)

            # --- SETTINGS
            self.lineEdit_settings_email.setText(config.get("SETTINGS", "email"))
            self.lineEdit_settings_ftp_host.setText(config.get("SETTINGS", "ftp_host"))
            self.lineEdit_settings_ftp_username.setText(config.get("SETTINGS", "ftp_username"))
            self.lineEdit_settings_ftp_password.setText(config.get("SETTINGS", "ftp_password"))
            self.checkBox_settings_ftp_autoconnect.setChecked(config.getboolean("SETTINGS", "ftp_autoconnect"))
            self.lineEdit_settings_ya_token.setText(config.get("SETTINGS", "ya_token"))
            self.lineEdit_settings_ya_folder.setText(config.get("SETTINGS", "ya_folder"))
            self.checkBox_settings_ya_autoconnect.setChecked(config.getboolean("SETTINGS", "ya_autoconnect"))
            self.lineEdit_settings_google_json.setText(config.get("SETTINGS", "google_json"))
            self.lineEdit_settings_google_id.setText(config.get("SETTINGS", "google_id"))
            self.checkBox_settings_google_autoconnect.setChecked(config.getboolean("SETTINGS", "google_autoconnect"))
            self.action_debug_stream.setChecked(config.getboolean("SETTINGS", "output_str_active"))
        except Exception:
            self.show_logs("The file conf.ini is corrupted.")

    # *************************** ВКЛАДКА DATABASE ***************************
    def db_sql_command(self):
        sql_com = self.lineEdit_db_sql.text()
        cursor = self.open_db.cursor()
        cursor.execute(sql_com)
        out = cursor.fetchall()
        for i in range(len(out)):
            self.show_logs(str(out[i]))
        self.open_db.commit()

    def db_create(self):
        if os.path.exists(self.lineEdit_db_new.text()):
            self.show_logs("Database exists.")
            return
        conn = sqlite3.connect(self.lineEdit_db_new.text())
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE "BASELINES" (
            "id_line"	INTEGER UNIQUE,
            "enable"	INTEGER,
            "name_r_base"	INTEGER,
            "name_r_rover"	INTEGER,
            "id_pos"	INTEGER,
            "comment"	TEXT,
            PRIMARY KEY("id_line")
            );
        """)
        cursor.execute("""
        CREATE TABLE "CONV_CONF" (
        "id_conv"	INTEGER UNIQUE,
		"name"	TEXT,
		"comment"	TEXT,
        "format"	TEXT,
        "freq"	INTEGER,
        "rinex"	TEXT,
        "satellite"	TEXT,
        "obs"	INTEGER,
        "nav"	INTEGER,
        PRIMARY KEY("id_conv")
        );
        """)
        cursor.execute("""
        CREATE TABLE "POINTS" (
        "id_poi"	INTEGER UNIQUE,
        "lat_x"	REAL,
        "lon_y"	REAL,
        "hei_z"	REAL,
        "name_r"	INTEGER,
        "comment"	TEXT,
        PRIMARY KEY("id_poi")
        );
        """)
        cursor.execute("""
            CREATE TABLE "POS_CONF" (
            "id_pos"	INTEGER UNIQUE,
            "name"	TEXT,
            "comment"	TEXT,
            "pos_mode"	INTEGER,
            "freq"	INTEGER,
            "sol_format"	INTEGER,
            "elevation"	INTEGER,
            "decimals"	INTEGER,
            "format_base"	INTEGER,
            "base_lat_x"	REAL,
            "base_lon_y"	REAL,
            "base_hei_z"	REAL,
            PRIMARY KEY("id_pos")
            );
            """)
        cursor.execute("""
        CREATE TABLE "RECEIVERS" (
        "name_r"	TEXT,
        "enable"	INTEGER,
        "id_conv"	INTEGER,
        "protocol"	INTEGER,
        "ip_host"	TEXT,
        "username"	TEXT,
        "password"	TEXT,
        "mountpoint"	TEXT,
        "type"	TEXT,
        "com_port" TEXT,
        "baudrate" INTEGER,
        "bit_size" INTEGER,
        "patity" TEXT,
        "stop_bit" INTEGER,
        "flow_ctr" TEXT,
        "id_poi"	INTEGER,
        PRIMARY KEY("name_r")
        );
        """)
        cursor.execute("""
        CREATE TABLE "SOLUTIONS" (
        "id_sol"	INTEGER UNIQUE,
        "id_line"	INTEGER,
        "name_r"	INTEGER,
        "date"	TEXT,
        "time"	TEXT,
        "coord_1"	REAL,
        "coord_2"	REAL,
        "coord_3"	REAL,
        "q"	INTEGER,
        "ns"	INTEGER,
        "sdx"	REAL,
        "sdy"	REAL,
        "sdz"	REAL,
        "sdxy"	REAL,
        "sdyz"	REAL,
        "sdzx"	REAL,
        "age"	REAL,
        "ratio"	REAL,
        "comment"	TEXT,
        "work_time"	TEXT,
        "path"	TEXT,
        PRIMARY KEY("id_sol")
        );
        """)
        conn.commit()
        self.show_logs("Database is was created!")

    def db_path_new(self):
        path = QFileDialog.getExistingDirectory(None)
        self.lineEdit_db_new.setText(path + "/database.db")

    def db_path_connect(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.lineEdit_db_con_path.setText(fname)

    def db_connect(self):
        db_table = ['BASELINES', 'CONV_CONF', 'POINTS', 'POS_CONF', 'RECEIVERS', 'SOLUTIONS']
        temp_table = ""
        if self.lineEdit_db_con_path.text() != "":
            try:
                self.open_db = sqlite3.connect(self.lineEdit_db_con_path.text(), check_same_thread=False)
                for i in db_table:
                    temp_table = i
                    cursor = self.open_db.cursor()
                    sql = "SELECT * FROM " + i
                    cursor.execute(sql)
            except Exception:
                self.show_logs("Doesn't exist table " + str(temp_table))
                self.open_db.close()
            else:
                self.show_logs("Database is was connected!")

    def db_dir_save(self):
        path = QFileDialog.getExistingDirectory(None)
        self.lineEdit_db_save.setText(path)

    def db_stop(self):
        self.post_pro_db = []
        os.system("killall str2str")

    def db_start_str2str(self):
        self.db_stop()
        try:
            cursor = self.open_db.cursor()
            sql = "SELECT name_r FROM RECEIVERS WHERE enable=1"
            cursor.execute(sql)
            host = cursor.fetchall()

            path_save = self.lineEdit_db_save.text()
            dir_path_list = []
            if path_save != "":
                today = datetime.today().strftime("%m.%d.%y")
                for i in range(len(host)):
                    temp_host = host[i][0].replace(":", ".")
                    filepath = ""
                    if os.path.exists(
                            path_save + "/" + datetime.today().strftime("%m.%d.%y") + "/" + temp_host):
                        self.show_logs("Directory exists.")
                        filepath = path_save + "/" + datetime.today().strftime("%m.%d.%y") + "/" + temp_host
                        dir_path_list.append(filepath + "/")
                    else:
                        try:
                            filepath = path_save + "/" + today
                            os.mkdir(filepath)
                        except OSError:
                            self.show_logs("Создать директорию %s не удалось" % filepath)
                        else:
                            self.show_logs("Успешно создана директория %s " % filepath)

                        try:
                            filepath = path_save + "/" + today + "/" + temp_host
                            os.mkdir(filepath)
                        except OSError:
                            self.show_logs("Создать директорию %s не удалось" % filepath)
                        else:
                            dir_path_list.append(filepath + "/")
                            self.show_logs("Успешно создана директория %s " % filepath)

            else:
                self.show_logs("Укажите путь для сохранения!")
                return

            sql = "SELECT * FROM RECEIVERS WHERE enable=1"
            cursor.execute(sql)
            host = cursor.fetchall()
            for i in range(len(host)):
                command_str2str = "xterm -e \"/bin/bash -c '" + os.getcwd() + "/RTKLIB-2.4.3-b33/app/str2str/gcc/" + \
                                  "str2str -in "
                if host[i][3] == 0:
                    command_str2str += "tcpcli://"
                    command_str2str += host[i][4]
                if host[i][3] == 1:
                    command_str2str += "ntrip://"
                    command_str2str += host[i][5] + ":" + host[i][6] + "@"
                    command_str2str += host[i][4] + "/" + host[i][7]
                if host[i][3] == 2:
                    command_str2str += "serial://"
                    command_str2str += host[i][9] + ":" + host[i][10] + ":" + host[i][11] + ":" + host[i][12]\
                                       + ":" + host[i][13] + ":" + host[i][14]

                if len(dir_path_list) == len(host):
                    command_str2str += " -out file://"
                    command_str2str += dir_path_list[i]

                    temp_ip = host[i][0]
                    file_n = temp_ip.replace(":", ".")
                    file_n += "_" + datetime.utcnow().strftime("%m.%d.%Y_%H-%M-%S") + ".log"
                    command_str2str += file_n
                    self.post_pro_db.append([])
                    self.post_pro_db[i].append(host[i][0])
                    self.post_pro_db[i].append(dir_path_list[i] + file_n)

                else:
                    self.show_logs(
                        "(STR2STR) Не все директории были созданы. Запись в файлы отменена. Не соответствие кол-во "
                        "хостов и созданных директорий")
                    self.send_email(
                        message="(STR2STR) Не все директории были созданы. Запись в файлы отменена. Не соответствие "
                                "кол-во хостов и созданных директорий")

                if self.action_debug_stream.isChecked():
                    str_folder = "logs/xterm"
                    today = datetime.today().strftime("%d.%m.%y")
                    filepath = ""
                    if os.path.exists(str_folder + "/" + today + "/"):
                        self.show_logs("Directory exists for str output.")
                        command_str2str += " &>> " + str_folder + "/" + today + "/" + str(
                            os.path.basename(self.post_pro_db[i][1]))
                    else:
                        try:
                            filepath = str_folder + "/" + today
                            os.mkdir(filepath)
                        except OSError:
                            self.show_logs("Создать директорию %s не удалось" % filepath)
                        else:
                            self.show_logs("Успешно создана директория %s " % filepath)
                            command_str2str += " &>> " + str_folder + "/" + today + "/" + str(
                                os.path.basename(self.post_pro_db[i][1]))
                command_str2str += "'\"&"

                self.show_logs(command_str2str)
                os.system(command_str2str)
                time.sleep(1)
                if self.action_autoclose_xterm.isChecked():
                    os.system("killall xterm")

            free = psutil.disk_usage(path_save).free / (1024 * 1024 * 1024)
            if free < 2:
                self.send_email(message="Внимание! Осталось памяти на диске " + str(free) + " Gb")

        except Exception as e:
            self.show_logs("STR2STR with DB: " + str(e))

        print(self.post_pro_db)

    def db_start_convbin(self, list_path):
        try:
            cursor = self.open_db.cursor()
            sql = """SELECT COUNT(*) FROM RECEIVERS, CONV_CONF 
            WHERE RECEIVERS.enable=1 AND RECEIVERS.id_conv = CONV_CONF.id_conv"""

            cursor.execute(sql)
            count = cursor.fetchall()
            # print(count)

            for y in range(count[0][0]):
                command_convbin = "RTKLIB-2.4.3-b33/app/convbin/gcc/convbin"

                sql = "SELECT format FROM RECEIVERS, CONV_CONF WHERE RECEIVERS.enable=1 AND " \
                      "RECEIVERS.id_conv = CONV_CONF.id_conv"
                cursor.execute(sql)
                format = cursor.fetchall()
                command_convbin += " -r " + (format[y][0])

                sql = "SELECT freq FROM RECEIVERS, CONV_CONF WHERE RECEIVERS.enable=1 AND " \
                      "RECEIVERS.id_conv = CONV_CONF.id_conv"
                cursor.execute(sql)
                freq = cursor.fetchall()
                command_convbin += " -f " + str(freq[y][0])

                sql = "SELECT rinex FROM RECEIVERS, CONV_CONF WHERE RECEIVERS.enable=1 AND " \
                      "RECEIVERS.id_conv = CONV_CONF.id_conv"
                cursor.execute(sql)
                rinex = cursor.fetchall()
                command_convbin += " -v " + rinex[y][0]
                command_convbin += " -os -od"

                sql = "SELECT satellite FROM RECEIVERS, CONV_CONF WHERE RECEIVERS.enable=1 AND " \
                      "RECEIVERS.id_conv = CONV_CONF.id_conv"
                cursor.execute(sql)
                satellite = cursor.fetchall()

                temp_sat = ["G", "R", "E", "J", "S", "C"]
                my_sat = satellite[y][0].rsplit(',', 7)
                for z in range(len(my_sat)):
                    temp_sat.remove(my_sat[z])
                for z in range(len(temp_sat)):
                    command_convbin += " -y " + temp_sat[z]

                sql = "SELECT obs, nav FROM RECEIVERS, CONV_CONF WHERE RECEIVERS.enable=1 AND " \
                      "RECEIVERS.id_conv = CONV_CONF.id_conv"
                cursor.execute(sql)
                out = cursor.fetchall()

                if list_path != []:
                    if out[y][0] == 1:
                        command_convbin += " -o "
                        command_convbin += list_path[y][1] + ".obs"
                    if out[y][1] == 1:
                        command_convbin += " -n "
                        command_convbin += list_path[y][1] + ".nav"

                    fname = list_path[y][1]
                    p = QUrl.fromLocalFile(fname)
                    p = p.fileName()
                    p = p.rsplit('_', 2)
                    time_conv = ""
                    if len(p) == 3:
                        p[1] = p[1].rsplit('.', 2)
                        p[2] = p[2].rsplit('-', 2)
                        if len(p[2]) == 3:
                            p[2][2] = p[2][2].rsplit('.', 1)
                        if len(p[1]) == 3 and len(p[2]) == 3:
                            time_conv = p[1][2] + "/" + p[1][0] + "/" + p[1][1] + " "
                            time_conv += p[2][0] + ":" + p[2][1] + ":" + p[2][2][0]

                    command_convbin += " -ts " + time_conv
                    command_convbin += " " + list_path[y][1]
                else:
                    self.show_logs("(CONVBIN) Декодирование не произошло.")
                    self.send_email(message="(CONVBIN) Декодирование не произошло.")
                self.show_logs(command_convbin)
                os.system(command_convbin)
                time.sleep(1)
        except Exception as e:
            self.show_logs("CONVBIN with DB: " + str(e))

    def db_start_rnx2rtkp(self, list_path):
        try:
            cursor = self.open_db.cursor()
            sql = """SELECT * FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
            BASELINES.enable = 1"""
            cursor.execute(sql)
            id_pos = cursor.fetchall()

            for i in range(len(id_pos)):
                command_rnx2rtkp = "RTKLIB-2.4.3-b33/app/rnx2rtkp/gcc/rnx2rtkp"
                sql = """SELECT pos_mode FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                BASELINES.enable = 1"""
                cursor.execute(sql)
                pos_mode = cursor.fetchall()
                command_rnx2rtkp += " -p " + str(pos_mode[i][0])

                sql = """SELECT elevation FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                BASELINES.enable = 1"""
                cursor.execute(sql)
                elev = cursor.fetchall()
                command_rnx2rtkp += " -m " + str(elev[i][0])

                sql = """SELECT freq FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                BASELINES.enable = 1"""
                cursor.execute(sql)
                freq = cursor.fetchall()
                command_rnx2rtkp += " -f " + str(freq[i][0])

                sql = """SELECT sol_format FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                BASELINES.enable = 1"""
                cursor.execute(sql)
                sol_format = cursor.fetchall()
                if sol_format[i][0] == 0:
                    pass
                elif sol_format[i][0] == 1:
                    # command_rnx2rtkp += " -g"
                    pass
                elif sol_format[i][0] == 2:
                    command_rnx2rtkp += " -e"
                elif sol_format[i][0] == 3:
                    command_rnx2rtkp += " -a"
                elif sol_format[i][0] == 4:
                    # command_rnx2rtkp += " -a"
                    pass

                command_rnx2rtkp += " -t"

                sql = """SELECT decimals FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                BASELINES.enable = 1"""
                cursor.execute(sql)
                decimals = cursor.fetchall()
                command_rnx2rtkp += " -d " + str(decimals[i][0])

                sql = """SELECT format_base, base_lat_x, base_lon_y, base_hei_z 
                FROM BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND BASELINES.enable = 1"""
                cursor.execute(sql)
                format_base = cursor.fetchall()
                if format_base[i][0] == 0:
                    command_rnx2rtkp += " -l " + str(format_base[i][1]) + " " + str(
                        format_base[i][2]) + " " + str(format_base[i][3])
                if format_base[i][0] == 1:
                    command_rnx2rtkp += " -r " + str(format_base[i][1]) + " " + str(
                        format_base[i][2]) + " " + str(format_base[i][3])

                sql = """SELECT name_r_base, name_r_rover FROM 
                            BASELINES, POS_CONF WHERE BASELINES.id_pos = POS_CONF.id_pos AND BASELINES.enable = 1"""
                cursor.execute(sql)
                base_rover = cursor.fetchall()

                pars_pos = False
                error_path = ""

                if list_path != []:
                    for y in range(len(list_path)):
                        if base_rover[i][1] == list_path[y][0]:
                            command_rnx2rtkp += " -o " + list_path[y][1] + ".pos"
                            if os.path.exists(list_path[y][1] + ".obs"):
                                command_rnx2rtkp += " " + list_path[y][1] + ".obs"
                                error_path = list_path[y][1] + ".obs"
                                pars_pos = True
                            else:
                                pars_pos = False

                    if pars_pos:
                        for y in range(len(list_path)):
                            if base_rover[i][0] == list_path[y][0]:
                                command_rnx2rtkp += " " + list_path[y][1] + ".obs"
                                command_rnx2rtkp += " " + list_path[y][1] + ".nav"

                        self.show_logs(command_rnx2rtkp)
                        os.system(command_rnx2rtkp)
                        time.sleep(1)

                        # -------------------------------
                        for y in range(len(list_path)):
                            if base_rover[i][1] == list_path[y][0]:
                                if os.path.exists(list_path[y][1] + ".pos"):  # True
                                    self.show_logs("Post processing OK")

                                    # ВЫТАСКИВАЕМ ПОСЛЕДНЮЮ СТРОЧКУ В ФАЙЛЕ
                                    f = open(list_path[y][1] + ".pos", "r")
                                    min_str = []
                                    min = 0
                                    frs = True
                                    time_list = []

                                    for line in f:
                                        a = line.split(" ", 100)
                                        while "" in a:
                                            a.remove("")
                                        if a[0] != "%" and a[0] != "%\n":
                                            time_list.append(a[1])

                                            d = float(a[7]) ** 2 + float(a[8]) ** 2 + float(a[9]) ** 2
                                            if frs:
                                                min_str = a
                                                min = d
                                                frs = False
                                            if d < min:
                                                min_str = a
                                                min = d
                                        for j in range(len(min_str)):
                                            if j == len(min_str) - 1:
                                                min_str[j] = min_str[j].replace("\n", "")
                                    # print(min_str)

                                    if min_str != []:

                                        work_time = 0
                                        for j in range(len(time_list)):
                                            temp_time = time_list[j].split(":")
                                            temp_seconds = temp_time[2].split(".")
                                            next_time1 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                                                temp_seconds[0])

                                            if j < len(time_list) - 1:
                                                temp_time = time_list[j + 1].split(":")
                                                temp_seconds = temp_time[2].split(".")
                                                next_time2 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                                                    temp_seconds[0])

                                                delta = next_time2 - next_time1
                                                if not self.lineEdit_db_delta.text() == "":
                                                    if 0 <= delta <= int(self.lineEdit_db_delta.text()):
                                                        work_time += delta
                                                else:
                                                    if 0 <= delta <= 1:
                                                        work_time += delta

                                        # Вставка в БД
                                        sql = "SELECT id_sol FROM SOLUTIONS ORDER BY id_sol DESC LIMIT 1"
                                        cursor.execute(sql)
                                        id_next = cursor.fetchall()

                                        # print(id_next)

                                        sql = """SELECT BASELINES.id_line FROM BASELINES, POS_CONF 
                                        WHERE BASELINES.id_pos = POS_CONF.id_pos AND BASELINES.enable = 1"""
                                        cursor.execute(sql)
                                        id_line = cursor.fetchall()

                                        sql = """SELECT BASELINES.name_r_rover FROM BASELINES, POS_CONF 
                                                                WHERE BASELINES.id_pos = POS_CONF.id_pos AND 
                                                                BASELINES.enable = 1"""
                                        cursor.execute(sql)
                                        name_r = cursor.fetchall()

                                        kor = []
                                        if id_next == []:
                                            id_next = 0
                                            kor.append(id_next)
                                        else:
                                            kor.append(id_next[0][0] + 1)
                                        kor.append(id_line[i][0])
                                        kor.append(name_r[i][0])
                                        for j in range(len(min_str)):
                                            kor.append(min_str[j])
                                        kor.append("")
                                        kor.append(str(timedelta(seconds=work_time)))
                                        kor.append(list_path[y][1] + ".pos")

                                        sql = "INSERT INTO SOLUTIONS " \
                                              "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                                        # print(kor)
                                        cursor.execute(sql, kor)
                                        self.open_db.commit()

                                        # ОТПРАВЛЯЕМ НА ПОЧТУ
                                        message = ""
                                        for j in range(len(min_str)):
                                            message += min_str[j] + " "

                                        self.send_email(message)
                                    else:
                                        self.show_logs(list_path[y][1] + ".pos" + " Not Found")
                    else:
                        self.show_logs(
                            "(RNX2RTKP) Постобработка не произошла. Не существует RINEX файл ровера. " + error_path)
                        self.send_email(
                            message="(RNX2RTKP) Постобработка не произошла. Не существует RINEX "
                                    "файл ровера. " + error_path)
                else:
                    self.show_logs("(RNX2RTKP) Постобработка не произошла")
                    self.send_email(message="(RNX2RTKP) Постобработка не произошла")
        except Exception as e:
            self.show_logs("RNX2RTKP with DB: " + str(e))

    def db_check_str2str(self, state):
        if state != self.checkBox_db_reset.isChecked():
            self.timeEdit_db.setEnabled(True)
        else:
            self.timeEdit_db.setEnabled(False)

    def db_check_post(self, state):
        if state != self.checkBox_db_post.isChecked():
            self.lineEdit_db_hours.setEnabled(True)
            self.lineEdit_db_minutes.setEnabled(True)
            self.lineEdit_db_seconds.setEnabled(True)
            self.Button_db_timepost_ok.setEnabled(True)
        else:
            self.lineEdit_db_hours.setEnabled(False)
            self.lineEdit_db_minutes.setEnabled(False)
            self.lineEdit_db_seconds.setEnabled(False)
            self.Button_db_timepost_ok.setEnabled(False)
            self.bool_ok_db = False

    def db_posttime(self):
        if not self.bool_ok_db:
            self.bool_ok_db = True
            self.show_logs("On")
            self.temp_time_db = int(datetime.today().timestamp()) + int(self.lineEdit_db_hours.text()) * 3600 + int(
                self.lineEdit_db_minutes.text()) * 60 + int(self.lineEdit_db_seconds.text())
            # print(self.temp_time)
        else:
            self.bool_ok_db = False
            self.show_logs("Off")

    # *************************** ВКЛАДКА RNX2RTKP ***************************

    def rxn2rtkp_conf_file_check(self, state):
        if state != self.checkBox_rnx2rtkp_conf.isChecked():
            self.lineEdit_rnx2rtkp_conf.setEnabled(True)
        else:
            self.lineEdit_rnx2rtkp_conf.setEnabled(False)

    def rnx2rtkp_time_start_check(self, state):
        if state != self.checkBox_rnx2rtkp_time_start.isChecked():
            self.dateTimeEdit_rnx2rtkp_start.setEnabled(True)
        else:
            self.dateTimeEdit_rnx2rtkp_start.setEnabled(False)

    def rnx2rtkp_time_end_check(self, state):
        if state != self.checkBox_rnx2rtkp_time_end.isChecked():
            self.dateTimeEdit_rnx2rtkp_end.setEnabled(True)
        else:
            self.dateTimeEdit_rnx2rtkp_end.setEnabled(False)

    def rnx2rtkp_input_conf(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.lineEdit_rnx2rtkp_conf.setText(fname)

    def rnx2rtkp_input_rover(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        if fname == "":
            return
        self.lineEdit_rnx2rtkp_rover.setText(fname)

        p = QUrl.fromLocalFile(fname)
        p = p.fileName()
        p = p.rsplit('.', 1)
        if len(p) == 2:
            self.show_logs(str(p))
            self.fname_input_rnx2rtkp = p[0]
            pa = fname
            fname_path = pa.replace(self.fname_input + '.' + p[1], "")
            self.fname_output_pos = fname_path + ".pos"
            self.lineEdit_rnx2rtkp_output.setText(self.fname_output_pos)
        else:
            self.show_logs("Specify the extension!")

    def rnx2rtkp_input_base(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.lineEdit_rnx2rtkp_base.setText(fname)

    def rnx2rtkp_input_nav(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.lineEdit_rnx2rtkp_nav.setText(fname)

    def rnx2rtkp_output(self):
        fname = QFileDialog.getExistingDirectory(None)
        self.lineEdit_rnx2rtkp_output.setText(fname)

    def rnx2rtkp_input_start(self):
        command_rnx2rtkp = "RTKLIB-2.4.3-b33/app/rnx2rtkp/gcc/rnx2rtkp"
        if self.checkBox_rnx2rtkp_conf.isChecked():
            command_rnx2rtkp += " -k " + self.lineEdit_rnx2rtkp_conf.text()
        else:
            if self.checkBox_rnx2rtkp_time_start.isChecked():
                dt = self.dateTimeEdit_rnx2rtkp_start.text()
                dts = dt.rsplit(" ")
                command_rnx2rtkp += " -ts " + str(dts[0]) + " " + str(dts[1])

            if self.checkBox_rnx2rtkp_time_end.isChecked():
                dt = self.dateTimeEdit_rnx2rtkp_end.text()
                dts = dt.rsplit(" ")
                command_rnx2rtkp += " -te " + str(dts[0]) + " " + str(dts[1])

            command_rnx2rtkp += " -p " + str(self.comboBox_rnx2rtkp_pos_mode.currentIndex())
            command_rnx2rtkp += " -m " + self.lineEdit_rnx2rtkp_mask.text()
            command_rnx2rtkp += " -f " + str(self.comboBox_rnx2rtkp_freq.currentIndex() + 1)

            if self.comboBox_rnx2rtkp_sol_format.currentIndex() == 1:
                command_rnx2rtkp += " -g"
            elif self.comboBox_rnx2rtkp_sol_format.currentIndex() == 2:
                command_rnx2rtkp += " -e"
            elif self.comboBox_rnx2rtkp_sol_format.currentIndex() == 3:
                command_rnx2rtkp += " -a"
            elif self.comboBox_rnx2rtkp_sol_format.currentIndex() == 4:
                command_rnx2rtkp += " -n"

            if self.comboBox_rnx2rtkp_time_format.currentIndex() == 0:
                command_rnx2rtkp += " -t"

            command_rnx2rtkp += " -d " + self.lineEdit_rnx2rtkp_dec.text()

            if self.comboBox_rnx2rtkp_base.currentIndex() == 0:
                command_rnx2rtkp += " -l " + str(self.lineEdit_rnx2rtkp_1.text()) + " " + str(
                    self.lineEdit_rnx2rtkp_2.text()) + " " + str(self.lineEdit_rnx2rtkp_3.text())
            else:
                command_rnx2rtkp += " -r " + str(self.lineEdit_rnx2rtkp_1.text()) + " " + str(
                    self.lineEdit_rnx2rtkp_2.text()) + " " + str(self.lineEdit_rnx2rtkp_3.text())

        command_rnx2rtkp += " -o " + self.lineEdit_rnx2rtkp_output.text()
        command_rnx2rtkp += " " + self.lineEdit_rnx2rtkp_rover.text()
        command_rnx2rtkp += " " + self.lineEdit_rnx2rtkp_base.text()
        command_rnx2rtkp += " " + self.lineEdit_rnx2rtkp_nav.text()

        self.show_logs(command_rnx2rtkp)
        os.system(command_rnx2rtkp)
        time.sleep(1)

        if os.path.exists(self.lineEdit_rnx2rtkp_output.text()):
            self.show_logs("ok")
        else:
            self.show_logs(self.lineEdit_rnx2rtkp_output.text() + " Not Found")
            return

    # ***************************ВКЛАДКА CONVBIN***************************
    def convbin_check_obs(self, state):
        if state != self.checkBox_convbin_obs.isChecked():
            self.lineEdit_obs.setEnabled(True)
            self.Button_obs.setEnabled(True)
        else:
            self.lineEdit_obs.setEnabled(False)
            self.Button_obs.setEnabled(False)

    def convbin_check_nav(self, state):
        if state != self.checkBox_convbin_nav.isChecked():
            self.lineEdit_nav.setEnabled(True)
            self.Button_nav.setEnabled(True)
        else:
            self.lineEdit_nav.setEnabled(False)
            self.Button_nav.setEnabled(False)

    def convbin_check_gnav(self, state):
        if state != self.checkBox_convbin_gnav.isChecked():
            self.lineEdit_convbin_gnav.setEnabled(True)
            self.Button_convbin_gnav.setEnabled(True)
        else:
            self.lineEdit_convbin_gnav.setEnabled(False)
            self.Button_convbin_gnav.setEnabled(False)

    def convbin_check_hnav(self, state):
        if state != self.checkBox_convbin_hnav.isChecked():
            self.lineEdit_convbin_hnav.setEnabled(True)
            self.Button_convbin_hnav.setEnabled(True)
        else:
            self.lineEdit_convbin_hnav.setEnabled(False)
            self.Button_convbin_hnav.setEnabled(False)

    def convbin_check_qnav(self, state):
        if state != self.checkBox_convbin_qnav.isChecked():
            self.lineEdit_convbin_qnav.setEnabled(True)
            self.Button_convbin_qnav.setEnabled(True)
        else:
            self.lineEdit_convbin_qnav.setEnabled(False)
            self.Button_convbin_qnav.setEnabled(False)

    def convbin_check_lnav(self, state):
        if state != self.checkBox_convbin_lnav.isChecked():
            self.lineEdit_convbin_lnav.setEnabled(True)
            self.Button_convbin_lnav.setEnabled(True)
        else:
            self.lineEdit_convbin_lnav.setEnabled(False)
            self.Button_convbin_lnav.setEnabled(False)

    def convbin_check_sbas(self, state):
        if state != self.checkBox_convbin_sbas.isChecked():
            self.lineEdit_convbin_sbas.setEnabled(True)
            self.Button_convbin_sbas.setEnabled(True)
        else:
            self.lineEdit_convbin_sbas.setEnabled(False)
            self.Button_convbin_sbas.setEnabled(False)

    def convbin_check_time_start(self, state):
        if state != self.checkBox_time_start.isChecked():
            self.dateTimeEdit_start.setEnabled(True)
        else:
            self.dateTimeEdit_start.setEnabled(False)

    def convbin_check_time_end(self, state):
        if state != self.checkBox_time_end.isChecked():
            self.dateTimeEdit_end.setEnabled(True)
        else:
            self.dateTimeEdit_end.setEnabled(False)

    def convbin_convert(self):
        command_convbin = "RTKLIB-2.4.3-b33/app/convbin/gcc/convbin"
        command_convbin += " -r " + self.comboBox_format.currentText()
        command_convbin += " -f " + self.comboBox_freq.currentText()
        command_convbin += " -v " + self.comboBox_rinex.currentText()
        command_convbin += " -os -od"
        if self.checkBox_time_start.isChecked():
            command_convbin += " -ts "
            command_convbin += self.dateTimeEdit_start.text()
        if self.checkBox_time_end.isChecked():
            command_convbin += " -te "
            command_convbin += self.dateTimeEdit_end.text()

        if not self.checkBox_gps.isChecked():
            command_convbin += " -y G"
        if not self.checkBox_glo.isChecked():
            command_convbin += " -y R"
        if not self.checkBox_galileo.isChecked():
            command_convbin += " -y E"
        if not self.checkBox_qzss.isChecked():
            command_convbin += " -y J"
        if not self.checkBox_sbas.isChecked():
            command_convbin += " -y S"
        if not self.checkBox_beidou.isChecked():
            command_convbin += " -y C"

        if self.lineEdit_obs != "" and self.checkBox_convbin_obs.isChecked():
            command_convbin += " -o " + self.lineEdit_obs.text()
        if self.lineEdit_nav != "" and self.checkBox_convbin_nav.isChecked():
            command_convbin += " -n " + self.lineEdit_nav.text()
        if self.lineEdit_convbin_gnav != "" and self.checkBox_convbin_gnav.isChecked():
            command_convbin += " -g " + self.lineEdit_convbin_gnav.text()
        if self.lineEdit_convbin_hnav != "" and self.checkBox_convbin_hnav.isChecked():
            command_convbin += " -h " + self.lineEdit_convbin_hnav.text()
        if self.lineEdit_convbin_qnav != "" and self.checkBox_convbin_qnav.isChecked():
            command_convbin += " -q " + self.lineEdit_convbin_qnav.text()
        if self.lineEdit_convbin_lnav != "" and self.checkBox_convbin_qnav.isChecked():
            command_convbin += " -l " + self.lineEdit_convbin_qnav.text()
        if self.lineEdit_convbin_sbas != "" and self.checkBox_convbin_sbas.isChecked():
            command_convbin += " -s " + self.lineEdit_convbin_sbas.text()

        command_convbin += " " + self.lineEdit_input.text()
        self.show_logs(command_convbin)
        os.system("\n" + command_convbin)
        time.sleep(1)

    def convbin_input_path(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        if fname == "":
            return

        p = QUrl.fromLocalFile(fname)
        p = p.fileName()
        p = p.rsplit('_', 2)
        if len(p) == 3:
            p[1] = p[1].rsplit('.', 2)
            # print(p[1])
            p[2] = p[2].rsplit('-', 2)

            if len(p[2]) == 3:
                p[2][2] = p[2][2].rsplit('.', 1)

            # print(p[2])
            if len(p[1]) == 3 and len(p[2]) == 3:
                time_start = QDateTime(int(p[1][2]), int(p[1][0]), int(p[1][1]), int(p[2][0]), int(p[2][1]),
                                       int(p[2][2][0]))
                self.dateTimeEdit_start.setDateTime(time_start)
                self.show_logs("")
                self.show_logs(time_start)
                self.checkBox_time_start.setChecked(True)
        else:
            self.checkBox_time_start.setChecked(False)

        self.lineEdit_input.setText(fname)

        self.lineEdit_obs.setText(self.lineEdit_input.text() + ".obs")
        self.lineEdit_nav.setText(self.lineEdit_input.text() + ".nav")
        self.lineEdit_convbin_gnav.setText(self.lineEdit_input.text() + ".gnav")
        self.lineEdit_convbin_hnav.setText(self.lineEdit_input.text() + ".hnav")
        self.lineEdit_convbin_qnav.setText(self.lineEdit_input.text() + ".qnav")
        self.lineEdit_convbin_lnav.setText(self.lineEdit_input.text() + ".lnav")
        self.lineEdit_convbin_sbas.setText(self.lineEdit_input.text() + ".sbas")

    def convbin_output_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        self.lineEdit_output.setText(path)

    def convbin_obs_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.obs'
        self.lineEdit_obs.setText(path)

    def convbin_nav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.nav'
        self.lineEdit_nav.setText(path)

    def convbin_gnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.gnav'
        self.lineEdit_convbin_gnav.setText(path)

    def convbin_hnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.hnav'
        self.lineEdit_convbin_hnav.setText(path)

    def convbin_qnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.qnav'
        self.lineEdit_convbin_qnav.setText(path)

    def convbin_lnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.lnav'
        self.lineEdit_convbin_lnav.setText(path)

    def convbin_sbas_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.sbas'
        self.lineEdit_convbin_sbas.setText(path)

    # ***************************ВКЛАДКА STR2STR***************************
    def str2str_flag_output1(self, state):
        if state == self.checkBox_str2str_out1.isChecked():
            self.tab_output1.setEnabled(False)
        else:
            self.tab_output1.setEnabled(True)

    def str2str_flag_output2(self, state):
        if state == self.checkBox_str2str_out2.isChecked():
            self.tab_output2.setEnabled(False)
        else:
            self.tab_output2.setEnabled(True)

    def str2str_flag_output3(self, state):
        if state == self.checkBox_str2str_out3.isChecked():
            self.tab_output3.setEnabled(False)
        else:
            self.tab_output3.setEnabled(True)

    def str2str_check_outputflile(self, state):
        if state != self.checkBox_str2str_file.isChecked():
            self.lineEdit_str2str_outputfile.setEnabled(True)
            self.Button_str2str_outputfile.setEnabled(True)
        else:
            self.lineEdit_str2str_outputfile.setEnabled(False)
            self.Button_str2str_outputfile.setEnabled(False)

    def str2str_outputfile_path(self):
        path, _ = QFileDialog.getSaveFileName()
        self.lineEdit_str2str_out_file.setText(path + ".log")

    def str2str_outputfile_path_2(self):
        path, _ = QFileDialog.getSaveFileName()
        self.lineEdit_str2str_out_file_2.setText(path + ".log")

    def str2str_outputfile_path_3(self):
        path, _ = QFileDialog.getSaveFileName()
        self.lineEdit_str2str_out_file_3.setText(path + ".log")

    def str2str_inputfile_path(self):
        path,_ = QFileDialog.getOpenFileName()
        self.lineEdit_str2str_in_file.setText(path + ".log")

    def str2str_start(self):
        command_str2str = "xterm -e \"/bin/bash -c '" + os.getcwd() + "/RTKLIB-2.4.3-b33/app/str2str/gcc/" + \
                          "str2str -in "
        if self.tabWidget_str2str_in.currentIndex() == 0:
            command_str2str += "serial://"
            command_str2str += self.comboBox_str2str_in_ser_port.currentText()
            command_str2str += ":" + self.comboBox_str2str_in_ser_speed.currentText()
            command_str2str += ":" + self.comboBox_str2str_in_ser_bsize.currentText()
            command_str2str += ":" + self.comboBox_str2str_in_ser_parity.currentText()
            command_str2str += ":" + self.comboBox_str2str_in_ser_stopb.currentText()
            command_str2str += ":" + self.comboBox_str2str_in_ser_fctr.currentText()

        elif self.tabWidget_str2str_in.currentIndex() == 1:
            command_str2str += "tcpsvr://:"
            command_str2str += self.lineEdit_str2str_in_tcpsvr_port.text()

        elif self.tabWidget_str2str_in.currentIndex() == 2:
            command_str2str += "tcpcli://"
            command_str2str += self.lineEdit_str2str_in_tcpcli_host.text()

        elif self.tabWidget_str2str_in.currentIndex() == 3:
            command_str2str += "ntrip://"
            command_str2str += self.lineEdit_str2str_in_ntrip_userid.text() + ":" + \
                               self.lineEdit_str2str_in_ntrip_pass.text()

            command_str2str += "@" + self.lineEdit_str2str_in_ntrip_host.text() + "/" + \
                               self.lineEdit_str2str_in_ntrip_mountpoint.text()

        elif self.tabWidget_str2str_in.currentIndex() == 4:
            command_str2str += "file://"
            command_str2str += self.lineEdit_str2str_in_file.text()


        # ПЕРВАЯ ФОРМА
        if self.checkBox_str2str_out1.isChecked():
            command_str2str += " -out "
            if self.tabWidget_str2str_out_1.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.comboBox_str2str_out_ser_port.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_speed.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_bsize.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_parity.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_stopb.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_fctr.currentText()

            if self.tabWidget_str2str_out_1.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.lineEdit_str2str_out_tcpsvr_port.text()

            if self.tabWidget_str2str_out_1.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.lineEdit_str2str_out_tcpcli_host.text()

            if self.tabWidget_str2str_out_1.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.lineEdit_str2str_out_ntrip_userid.text() + ":" + \
                                   self.lineEdit_str2str_out_ntrip_pass.text()

                command_str2str += "@" + self.lineEdit_str2str_out_ntrip_host.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrip_mountpoint.text()

            if self.tabWidget_str2str_out_1.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.lineEdit_str2str_out_ntrips_pass.text()
                command_str2str += "@" + self.lineEdit_str2str_out_ntrips_host.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrips_mountpoint.text()

            if self.tabWidget_str2str_out_1.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.lineEdit_str2str_out_file.text()

        # ВТОРАЯ ФОРМА
        if self.checkBox_str2str_out2.isChecked():
            command_str2str += " -out "
            if self.tabWidget_str2str_out_2.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.comboBox_str2str_out_ser_port_2.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_speed_2.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_bsize_2.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_parity_2.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_stopb_2.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_fctr_2.currentText()

            if self.tabWidget_str2str_out_2.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.lineEdit_str2str_out_tcpsvr_port_2.text()

            if self.tabWidget_str2str_out_2.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.lineEdit_str2str_out_tcpcli_host_2.text()

            if self.tabWidget_str2str_out_2.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.lineEdit_str2str_out_ntrip_userid_2.text() + ":" + \
                                   self.lineEdit_str2str_out_ntrip_pass_2.text()

                command_str2str += "@" + self.lineEdit_str2str_out_ntrip_host_2.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrip_mountpoint_2.text()

            if self.tabWidget_str2str_out_2.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.lineEdit_str2str_out_ntrips_pass_2.text()
                command_str2str += "@" + self.lineEdit_str2str_out_ntrips_host_2.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrips_mountpoint_2.text()

            if self.tabWidget_str2str_out_2.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.lineEdit_str2str_out_file_2.text()

        #ТРЕТЬЯ ФОРМА
        if self.checkBox_str2str_out3.isChecked():
            command_str2str += " -out "
            if self.tabWidget_str2str_out_3.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.comboBox_str2str_out_ser_port_3.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_speed_3.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_bsize_3.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_parity_3.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_stopb_3.currentText()
                command_str2str += ":" + self.comboBox_str2str_out_ser_fctr_3.currentText()

            if self.tabWidget_str2str_out_3.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.lineEdit_str2str_out_tcpsvr_port_3.text()

            if self.tabWidget_str2str_out_3.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.lineEdit_str2str_out_tcpcli_host_3.text()

            if self.tabWidget_str2str_out_3.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.lineEdit_str2str_out_ntrip_userid_3.text() + ":" + \
                                   self.lineEdit_str2str_out_ntrip_pass_3.text()

                command_str2str += "@" + self.lineEdit_str2str_out_ntrip_host_3.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrip_mountpoint_3.text()

            if self.tabWidget_str2str_out_3.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.lineEdit_str2str_out_ntrips_pass_3.text()
                command_str2str += "@" + self.lineEdit_str2str_out_ntrips_host_3.text() + "/" + \
                                   self.lineEdit_str2str_out_ntrips_mountpoint_3.text()

            if self.tabWidget_str2str_out_3.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.lineEdit_str2str_out_file_3.text()

        command_str2str += "'\"&"
        self.show_logs(command_str2str)
        os.system(command_str2str)


    def str2str_stop(self):
        os.system("killall str2str")


    def str2str_stop_xterm(self):
        os.system("killall xterm")

    # *************************** ВКЛАДКА COM ***************************
    def com_connect(self):
        if self.button_com_flag:
            try:
                self.realport = serial.Serial(self.comboBox_port.currentText(), int(self.comboBox_speed.currentText()))
                self.pushButton_connect.setText("Disconnect")
                self.show_logs("Connected")
                self.lineEdit_send.setFocus()
                self.read_text_Thread_instance.start()
                self.button_com_flag = False
            except Exception as e:
                self.show_logs(str(e))
        else:
            self.realport.close()
            self.realport = None

            self.show_logs("Disconnected")
            self.button_com_flag = True
            self.pushButton_connect.setText("Connect")

    def com_send(self):
        if self.realport:
            send_text = self.comboBox_comm.currentText()
            self.realport.write(bytearray(send_text, 'utf8'))
        self.comboBox_comm.setEditText("")

    def com_refresh(self):
        self.comboBox_port.clear()
        self.comboBox_port.addItems(serial_ports())

    def com_clear(self):
        self.textEdit_read.clear()


# даННЫЙ КЛАСС НУЖЕН ДЛЯ ПЕРЕЗАПУСКА STR2STR В ОПРЕДЕЛЕННОЕ ВРЕМЯ
class TimeResetStr2strThread(QThread):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        while True:
            if (datetime.today().strftime(
                    "%H:%M:%S") == self.mainwindow.timeEdit_db.text() and self.mainwindow.checkBox_db_reset.isChecked()):
                temp_list = self.mainwindow.post_pro_db
                self.mainwindow.str2str_stop()
                self.mainwindow.db_start_str2str()
                if self.mainwindow.checkBox_db_lastpost.isChecked():
                    self.mainwindow.db_start_convbin(temp_list)
                    self.mainwindow.db_start_rnx2rtkp(temp_list)

                for path in temp_list:
                    if self.mainwindow.checkBox_settings_ftp_autoconnect.isChecked():
                        self.mainwindow.ftp_connect(path[1])
                    if self.mainwindow.checkBox_settings_ya_autoconnect.isChecked():
                        self.mainwindow.yadisk_connect(path[1])
                    if self.mainwindow.checkBox_settings_google_autoconnect.isChecked():
                        self.mainwindow.gdrive_connect(path[1])

            if self.mainwindow.checkBox_db_post.isChecked() and self.mainwindow.bool_ok_db:
                if int(datetime.today().timestamp()) > self.mainwindow.temp_time_db:
                    self.mainwindow.temp_time_db = int(datetime.today().timestamp()) + int(
                        self.mainwindow.lineEdit_db_hours.text()) * 3600 + int(
                        self.mainwindow.lineEdit_db_minutes.text()) * 60 + int(
                        self.mainwindow.lineEdit_db_seconds.text())
                    if self.mainwindow.post_pro_db != []:
                        temp_list = self.mainwindow.post_pro_db
                        self.mainwindow.db_start_convbin(temp_list)
                        self.mainwindow.db_start_rnx2rtkp(temp_list)
            time.sleep(1)


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

    def run(self):
        while True:
            try:
                if self.mainwindow.realport:  # ЕСЛИ ПОКЛЮЧЕНЫ К КОМ ПОРТУ
                    self.mainwindow.receivedMessage = self.mainwindow.realport.readline().decode(
                        'ascii')  # ЧИТАЕМ ДАННЫЕ С КОМ ПОРТА

                    if self.mainwindow.receivedMessage != "":
                        if self.mainwindow.checkBox_time.isChecked():
                            today = datetime.today().strftime("%H.%M.%S")
                            self.mainwindow.textEdit_read.append(today + " -> " + self.mainwindow.receivedMessage)
                            if self.log_write:
                                self.f = open(self.name_f, "a")
                                today = datetime.today().strftime("%H.%M.%S")
                                self.f.write(today + "-> " + self.mainwindow.receivedMessage + "\n")
                                self.f.close()
                        else:
                            self.mainwindow.textEdit_read.append(self.mainwindow.receivedMessage)
                            if self.log_write:
                                self.f = open(self.name_f, "a")
                                self.f.write(self.mainwindow.receivedMessage + "\n")
                                self.f.close()

                        if self.mainwindow.checkBox_scroll.isChecked():
                            self.mainwindow.textEdit_read.moveCursor(QtGui.QTextCursor.End)
                        self.mainwindow.receivedMessage = ""

            except Exception as e:
                self.show_logs(str(e))

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


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LedApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
