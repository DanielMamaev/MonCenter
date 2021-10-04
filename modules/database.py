from re import M
import sqlite3
import os
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime, timedelta
import psutil
import time
from PyQt5.QtCore import QThread, QUrl

from modules.show_logs import ShowLogs
from modules.settings import Settings

class DataBase():

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.logs = ShowLogs(parent=main)
        self.settings = Settings(main=main)

        self.open_db = sqlite3.connect("")
        self.connect()
        self.post_pro_db = []
        self.bool_ok_db = False
        self.temp_time_db = 0

        self.time_reset_str2str_Thread_instance = TimeResetStr2strThread(
            mainwindow=main)
        self.time_reset_str2str_Thread_instance.start()

    def sql_command(self):
        sql_com = self.main.lineEdit_db_sql.text()
        cursor = self.open_db.cursor()
        cursor.execute(sql_com)
        out = cursor.fetchall()
        for i in range(len(out)):
            self.logs.show_logs(str(out[i]))
        self.open_db.commit()

    def create(self):
        if os.path.exists(self.main.lineEdit_db_new.text()):
            self.logs.show_logs("Database exists.")
            return
        conn = sqlite3.connect(self.main.lineEdit_db_new.text())
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
        self.logs.show_logs("Database is was created!")

    def path_new(self):
        path = QFileDialog.getExistingDirectory(None)
        self.main.lineEdit_db_new.setText(path + "/database.db")

    def path_connect(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_db_con_path.setText(fname)

    def connect(self):
        db_table = ['BASELINES', 'CONV_CONF', 'POINTS',
                    'POS_CONF', 'RECEIVERS', 'SOLUTIONS']
        temp_table = ""
        if self.main.lineEdit_db_con_path.text() != "":
            try:
                self.open_db = sqlite3.connect(
                    self.main.lineEdit_db_con_path.text(), check_same_thread=False)
                for i in db_table:
                    temp_table = i
                    cursor = self.open_db.cursor()
                    sql = "SELECT * FROM " + i
                    cursor.execute(sql)
            except Exception:
                self.logs.show_logs("Doesn't exist table " + str(temp_table))
                self.open_db.close()
            else:
                self.logs.show_logs("Database is was connected!")

    def dir_save(self):
        path = QFileDialog.getExistingDirectory(None)
        self.main.lineEdit_db_save.setText(path)

    def stop(self):
        self.post_pro_db = []
        os.system("killall str2str")

    def start_str2str(self):
        self.stop()
        try:
            cursor = self.open_db.cursor()
            sql = "SELECT name_r FROM RECEIVERS WHERE enable=1"
            cursor.execute(sql)
            host = cursor.fetchall()

            path_save = self.main.lineEdit_db_save.text()
            dir_path_list = []
            if path_save != "":
                today = datetime.today().strftime("%m.%d.%y")
                for i in range(len(host)):
                    temp_host = host[i][0].replace(":", ".")
                    filepath = ""
                    if os.path.exists(
                            path_save + "/" + datetime.today().strftime("%m.%d.%y") + "/" + temp_host):
                        self.logs.show_logs("Directory exists.")
                        filepath = path_save + "/" + datetime.today().strftime("%m.%d.%y") + \
                            "/" + temp_host
                        dir_path_list.append(filepath + "/")
                    else:
                        try:
                            filepath = path_save + "/" + today
                            os.mkdir(filepath)
                        except OSError:
                            self.logs.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            self.logs.show_logs(
                                "Успешно создана директория %s " % filepath)

                        try:
                            filepath = path_save + "/" + today + "/" + temp_host
                            os.mkdir(filepath)
                        except OSError:
                            self.logs.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            dir_path_list.append(filepath + "/")
                            self.logs.show_logs(
                                "Успешно создана директория %s " % filepath)

            else:
                self.logs.show_logs("Укажите путь для сохранения!")
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
                    self.logs.show_logs(
                        "(STR2STR) Не все директории были созданы. Запись в файлы отменена. Не соответствие кол-во "
                        "хостов и созданных директорий")
                    self.settings.send_email(
                        message="(STR2STR) Не все директории были созданы. Запись в файлы отменена. Не соответствие "
                                "кол-во хостов и созданных директорий")

                if self.main.action_debug_stream.isChecked():
                    str_folder = "logs/xterm"
                    today = datetime.today().strftime("%d.%m.%y")
                    filepath = ""
                    if os.path.exists(str_folder + "/" + today + "/"):
                        self.logs.show_logs("Directory exists for str output.")
                        command_str2str += " &>> " + str_folder + "/" + today + "/" + str(
                            os.path.basename(self.post_pro_db[i][1]))
                    else:
                        try:
                            filepath = str_folder + "/" + today
                            os.mkdir(filepath)
                        except OSError:
                            self.logs.show_logs(
                                "Создать директорию %s не удалось" % filepath)
                        else:
                            self.logs.show_logs(
                                "Успешно создана директория %s " % filepath)
                            command_str2str += " &>> " + str_folder + "/" + today + "/" + str(
                                os.path.basename(self.post_pro_db[i][1]))
                command_str2str += "'\"&"

                self.logs.show_logs(command_str2str)
                os.system(command_str2str)
                time.sleep(1)
                if self.main.action_autoclose_xterm.isChecked():
                    os.system("killall xterm")

            free = psutil.disk_usage(path_save).free / (1024 * 1024 * 1024)
            if free < 2:
                self.settings.send_email(
                    message="Внимание! Осталось памяти на диске " + str(free) + " Gb")

        except Exception as e:
            self.logs.show_logs("STR2STR with DB: " + str(e))

        print(self.post_pro_db)

    def start_convbin(self, list_path):
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
                    self.logs.show_logs("(CONVBIN) Декодирование не произошло.")
                    self.settings.send_email(
                        message="(CONVBIN) Декодирование не произошло.")
                self.logs.show_logs(command_convbin)
                os.system(command_convbin)
                time.sleep(1)
        except Exception as e:
            self.logs.show_logs("CONVBIN with DB: " + str(e))

    def start_rnx2rtkp(self, list_path):
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

                        self.logs.show_logs(command_rnx2rtkp)
                        os.system(command_rnx2rtkp)
                        time.sleep(1)

                        # -------------------------------
                        for y in range(len(list_path)):
                            if base_rover[i][1] == list_path[y][0]:
                                if os.path.exists(list_path[y][1] + ".pos"):  # True
                                    self.logs.show_logs("Post processing OK")

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
                                                if 0 <= delta <= 60:
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

                                        self.settings.send_email(message)
                                    else:
                                        self.logs.show_logs(
                                            list_path[y][1] + ".pos" + " Not Found")
                    else:
                        self.logs.show_logs(
                            "(RNX2RTKP) Постобработка не произошла. Не существует RINEX файл ровера. " + error_path)
                        self.settings.send_email(
                            message="(RNX2RTKP) Постобработка не произошла. Не существует RINEX "
                                    "файл ровера. " + error_path)
                else:
                    self.logs.show_logs("(RNX2RTKP) Постобработка не произошла")
                    self.settings.send_email(
                        message="(RNX2RTKP) Постобработка не произошла")
        except Exception as e:
            self.logs.show_logs("RNX2RTKP with DB: " + str(e))


    def posttime(self):
        if not self.bool_ok_db:
            self.bool_ok_db = True
            self.logs.show_logs("On")
            self.temp_time_db = int(datetime.today().timestamp()) + int(self.main.lineEdit_db_hours.text()) * 3600 + int(
                self.main.lineEdit_db_minutes.text()) * 60 + int(self.main.lineEdit_db_seconds.text())
            # print(self.temp_time)
        else:
            self.bool_ok_db = False
            self.logs.show_logs("Off")




class TimeResetStr2strThread(QThread):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.settings = Settings(main=mainwindow)

    def run(self):
        while True:
            if (datetime.today().strftime(
                    "%H:%M:%S") == '00:00:00' and self.mainwindow.action_autopost_reset.isChecked()):
                temp_list = self.mainwindow.post_pro_db
                self.mainwindow.stop()
                self.mainwindow.start_str2str()
                if self.mainwindow.action_autopost_post.isChecked():
                    self.mainwindow.start_convbin(temp_list)
                    self.mainwindow.start_rnx2rtkp(temp_list)

                for path in temp_list:
                    if self.mainwindow.checkBox_settings_ftp_autoconnect.isChecked():
                        self.settings.ftp_connect(path[1])
                    if self.mainwindow.checkBox_settings_ya_autoconnect.isChecked():
                        self.settings.yadisk_connect(path[1])
                    if self.mainwindow.checkBox_settings_google_autoconnect.isChecked():
                        self.settings.gdrive_connect(path[1])
            time.sleep(1)
