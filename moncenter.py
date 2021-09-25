from modules.str2str import Str2Str
from modules.convbin import ConvBin
from modules.rnx2rtkp import Rnx2Rtkp
from modules.config_ini import ConfigIni
from modules.filter_sdf import FilterSDF


import sys
import glob

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QUrl
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog

import design
import serial
import os.path

import sqlite3
import psutil
from datetime import time as dt_time
from datetime import datetime, timedelta

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
class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.serial_update()
        

        # ------------- .INI
        self.config_ini = ConfigIni(main=self)
        self.action_exit.triggered.connect(self.config_ini.save_exit)
        self.action_save_config.triggered.connect(self.config_ini.save)
        self.action_reset_config.triggered.connect(self.config_ini.reset)
        self.config_ini.start()

        # -------------STR2STR
        self.str2str = Str2Str(main=self)
        self.action_start_str2str.triggered.connect(self.str2str.start)
        self.action_stop_str2str.triggered.connect(self.str2str.stop)
        self.action_close_xterm.triggered.connect(self.str2str.stop_xterm)
        self.Button_str2str_in_file.clicked.connect(
            self.str2str.inputfile_path)
        self.Button_str2str_out_file.clicked.connect(
            self.str2str.outputfile_path)
        self.Button_str2str_out_file_2.clicked.connect(
            self.str2str.outputfile_path_2)
        self.Button_str2str_out_file_3.clicked.connect(
            self.str2str.outputfile_path_3)
        self.checkBox_str2str_out1.stateChanged.connect(
            self.str2str.flag_output1)
        self.checkBox_str2str_out2.stateChanged.connect(
            self.str2str.flag_output2)
        self.checkBox_str2str_out3.stateChanged.connect(
            self.str2str.flag_output3)
        self.tab_output1.setEnabled(False)
        self.tab_output2.setEnabled(False)
        self.tab_output3.setEnabled(False)

        # -------------CONVBIN
        self.convbin = ConvBin(main=self)
        self.Button_convert.clicked.connect(self.convbin.convert)
        self.Button_input.clicked.connect(self.convbin.input_path)
        self.Button_obs.clicked.connect(self.convbin.obs_path)
        self.Button_nav.clicked.connect(self.convbin.nav_path)
        self.Button_convbin_gnav.clicked.connect(self.convbin.gnav_path)
        self.Button_convbin_hnav.clicked.connect(self.convbin.hnav_path)
        self.Button_convbin_qnav.clicked.connect(self.convbin.qnav_path)
        self.Button_convbin_lnav.clicked.connect(self.convbin.lnav_path)
        self.Button_convbin_sbas.clicked.connect(self.convbin.sbas_path)
        self.checkBox_convbin_obs.stateChanged.connect(self.convbin.check_obs)
        self.checkBox_convbin_nav.stateChanged.connect(self.convbin.check_nav)
        self.checkBox_convbin_gnav.stateChanged.connect(
            self.convbin.check_gnav)
        self.checkBox_convbin_hnav.stateChanged.connect(
            self.convbin.check_hnav)
        self.checkBox_convbin_qnav.stateChanged.connect(
            self.convbin.check_qnav)
        self.checkBox_convbin_lnav.stateChanged.connect(
            self.convbin.check_lnav)
        self.checkBox_convbin_sbas.stateChanged.connect(
            self.convbin.check_sbas)
        self.checkBox_time_start.stateChanged.connect(
            self.convbin.check_time_start)
        self.checkBox_time_end.stateChanged.connect(
            self.convbin.check_time_end)

        # -------------RNX2RTKP
        self.rnx2rtkp = Rnx2Rtkp(main=self)
        self.Button_rnx2rtkp_input_conf.clicked.connect(
            self.rnx2rtkp.input_conf)
        self.Button_rnx2rtkp_input_rover.clicked.connect(
            self.rnx2rtkp.input_rover)
        self.Button_rnx2rtkp_input_base.clicked.connect(
            self.rnx2rtkp.input_base)
        self.Button_rnx2rtkp_input_nav.clicked.connect(self.rnx2rtkp.input_nav)
        self.Button_rnx2rtkp_output.clicked.connect(self.rnx2rtkp.output)
        self.Button_rnx2rtkp_start.clicked.connect(self.rnx2rtkp.start)
        self.lineEdit_rnx2rtkp_conf.setText("")

      

        self.checkBox_rnx2rtkp_conf.stateChanged.connect(
            self.rnx2rtkp.conf_file_check)
        self.checkBox_rnx2rtkp_time_start.stateChanged.connect(
            self.rnx2rtkp.time_start_check)
        self.checkBox_rnx2rtkp_time_end.stateChanged.connect(
            self.rnx2rtkp.time_end_check)

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

        self.time_reset_str2str_Thread_instance = TimeResetStr2strThread(
            mainwindow=self)
        self.time_reset_str2str_Thread_instance.start()

        self.checkBox_db_reset.stateChanged.connect(self.db_check_str2str)
        self.checkBox_db_post.stateChanged.connect(self.db_check_post)
        self.Button_db_timepost_ok.clicked.connect(self.db_posttime)
        self.Button_db_sql.clicked.connect(self.db_sql_command)

        # ------------- COM
        self.realport = None
        self.action_refresh_ports.triggered.connect(self.serial_update)
        self.pushButton_connect.clicked.connect(
            self.com_connect)  # ОБРАБОТКА ПОДКЛЮЧЕНИЯ К ПОРТУ
        self.pushButton_refresh.clicked.connect(
            self.com_refresh)  # ПОИСК НОВЫХ ПОРТОВ
        self.pushButton_send.clicked.connect(
            self.com_send)  # ОТПРАВКА СООБЩЕНИЯ
        # ЧИСТКА ОКНА ПРИХОДЯЩИХ ДАННЫХ С КОМ ПОРТА
        self.pushButton_clear.clicked.connect(self.com_clear)
        self.receivedMessage = None  # ХРАНИТ ПРИХОДЯЩЕЕ СООБЩЕНИЕ С КОМ ПОРТА
        self.button_com_flag = True  # ФЛАГ ДЛЯ ПОДКЛЮЧЕНИЯ К КОМ ПОРТУ
        self.command_list = ['#ser', '#num', '#ip', '#tcp_res', '#restart',
                             '#reset']  # КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ WEMOS ЧЕРЕЗ КОМ ПОРТ
        # ДОБАВЛЕНИЕ КОМАНД В COMBOBOX
        self.comboBox_comm.addItems(self.command_list)
        self.read_text_Thread_instance = ReadTextThread(mainwindow=self)

        # ------------- filterSDF
        self.filterSDF = FilterSDF(main=self)
        self.pushButton_filterSDF_inputPath.clicked.connect(
            self.filterSDF.input_path)
        self.pushButton_filterSDF_outputPath.clicked.connect(
            self.filterSDF.output_path)
        self.pushButton_filterSDF_start.clicked.connect(self.filterSDF.start)




    def serial_update(self):
        # ДОБАВЛЕНИЕ НАЙДЕННЫХ ПОРТОВ В COMBOBOX
        self.comboBox_port.addItems(serial_ports())
        self.comboBox_str2str_in_ser_port.addItems(serial_ports())
    # *************************** SHOW LOGS ***************************

    

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
            smtp_obj.sendmail(
                msg['From'], self.lineEdit_settings_email.text(), msg.as_string())
            smtp_obj.quit()
        else:
            self.show_logs(
                "Не указана электронная почта для отправки уведомлений.")

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
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=SCOPES)
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
                    ya.upload(path, self.lineEdit_settings_ya_folder.text(
                    ) + date + "/" + os.path.basename(path))
                except Exception:
                    self.show_logs("Загрузить не удалось!")
                else:
                    self.show_logs(
                        "Загрузка " + os.path.basename(path) + " на Яндекс.Диск.")

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
            ftp.login(self.lineEdit_settings_ftp_username.text(),
                      self.lineEdit_settings_ftp_password.text())
        except Exception as e:
            self.show_logs("Проблема с подключением к FTP серверу " + str(e))
        else:
            self.show_logs("К FTP серверу подключились.")
            # print(ftp.retrlines('LIST')) # отображение всех файлов в каталоге
            # print(ftp.pwd()) # текущий путь

            today = datetime.today().strftime("%m.%d.%y")
            flag_dir = False
            try:
                ftp.mkd(today)  # создание папки
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
                # print(ftp.retrlines('LIST'))

            if flag_dir:
                try:
                    ftp.cwd('/' + today)
                except Exception as e:
                    self.show_logs("Такой папки /" + today +
                                   "не существует: " + str(e))
                    return
                else:
                    try:
                        ftp.storbinary(
                            'STOR ' + os.path.basename(path), open(path, "rb"))
                    except Exception as e:
                        self.show_logs("Проблема с загрузкой файла: " + str(e))

                try:
                    ftp.storbinary('STOR ' + os.path.basename(self.lineEdit_db_con_path.text()),
                                   open(self.lineEdit_db_con_path.text(), "rb"))
                except Exception as e:
                    self.show_logs("Проблема с загрузкой БД: " + str(e))
        ftp.close()

        # *************************** FILE .INI ***************************

    

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
        db_table = ['BASELINES', 'CONV_CONF', 'POINTS',
                    'POS_CONF', 'RECEIVERS', 'SOLUTIONS']
        temp_table = ""
        if self.lineEdit_db_con_path.text() != "":
            try:
                self.open_db = sqlite3.connect(
                    self.lineEdit_db_con_path.text(), check_same_thread=False)
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
                        filepath = path_save + "/" + datetime.today().strftime("%m.%d.%y") + \
                            "/" + temp_host
                        dir_path_list.append(filepath + "/")
                    else:
                        try:
                            filepath = path_save + "/" + today
                            os.mkdir(filepath)
                        except OSError:
                            self.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            self.show_logs(
                                "Успешно создана директория %s " % filepath)

                        try:
                            filepath = path_save + "/" + today + "/" + temp_host
                            os.mkdir(filepath)
                        except OSError:
                            self.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            dir_path_list.append(filepath + "/")
                            self.show_logs(
                                "Успешно создана директория %s " % filepath)

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
                    file_n += "_" + datetime.now().strftime("%m.%d.%Y_%H-%M-%S") + ".log"
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
                            self.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            self.show_logs(
                                "Успешно создана директория %s " % filepath)
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
                self.send_email(
                    message="Внимание! Осталось памяти на диске " + str(free) + " Gb")

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
                            time_conv = p[1][2] + "/" + \
                                p[1][0] + "/" + p[1][1] + " "
                            time_conv += p[2][0] + ":" + \
                                p[2][1] + ":" + p[2][2][0]

                    command_convbin += " -ts " + time_conv
                    command_convbin += " " + list_path[y][1]
                else:
                    self.show_logs("(CONVBIN) Декодирование не произошло.")
                    self.send_email(
                        message="(CONVBIN) Декодирование не произошло.")
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
                            command_rnx2rtkp += " -o " + \
                                list_path[y][1] + ".pos"
                            if os.path.exists(list_path[y][1] + ".obs"):
                                command_rnx2rtkp += " " + \
                                    list_path[y][1] + ".obs"
                                error_path = list_path[y][1] + ".obs"
                                pars_pos = True
                            else:
                                pars_pos = False

                    if pars_pos:
                        for y in range(len(list_path)):
                            if base_rover[i][0] == list_path[y][0]:
                                command_rnx2rtkp += " " + \
                                    list_path[y][1] + ".obs"
                                command_rnx2rtkp += " " + \
                                    list_path[y][1] + ".nav"

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

                                            d = float(
                                                a[7]) ** 2 + float(a[8]) ** 2 + float(a[9]) ** 2
                                            if frs:
                                                min_str = a
                                                min = d
                                                frs = False
                                            if d < min:
                                                min_str = a
                                                min = d
                                        for j in range(len(min_str)):
                                            if j == len(min_str) - 1:
                                                min_str[j] = min_str[j].replace(
                                                    "\n", "")
                                    # print(min_str)

                                    if min_str != []:

                                        work_time = 0
                                        for j in range(len(time_list)):
                                            temp_time = time_list[j].split(":")
                                            temp_seconds = temp_time[2].split(
                                                ".")
                                            next_time1 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                                                temp_seconds[0])

                                            if j < len(time_list) - 1:
                                                temp_time = time_list[j +
                                                                      1].split(":")
                                                temp_seconds = temp_time[2].split(
                                                    ".")
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
                                        kor.append(
                                            str(timedelta(seconds=work_time)))
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
                                        self.show_logs(
                                            list_path[y][1] + ".pos" + " Not Found")
                    else:
                        self.show_logs(
                            "(RNX2RTKP) Постобработка не произошла. Не существует RINEX файл ровера. " + error_path)
                        self.send_email(
                            message="(RNX2RTKP) Постобработка не произошла. Не существует RINEX "
                                    "файл ровера. " + error_path)
                else:
                    self.show_logs("(RNX2RTKP) Постобработка не произошла")
                    self.send_email(
                        message="(RNX2RTKP) Постобработка не произошла")
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

    

    # ***************************ВКЛАДКА CONVBIN***************************
    

    # ***************************ВКЛАДКА STR2STR***************************
    

    # *************************** ВКЛАДКА COM ***************************
    def com_connect(self):
        if self.button_com_flag:
            try:
                self.realport = serial.Serial(
                    self.comboBox_port.currentText(), int(self.comboBox_speed.currentText()))
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
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
