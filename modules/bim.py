import sys
import os
sys.path.insert(0, os.getcwd())

import ifcpatch
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
import math
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import sqlite3
from modules.show_logs import ShowLogs
import configparser

class BIM():
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.open_db = sqlite3.connect("")
        self.logs = ShowLogs(parent=main)
        self.config = configparser.ConfigParser()
        self.path_ini = "conf.ini"
        

    def open_bilding(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_bim_input_bilding.setText(fname)
    
    def open_sensor(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_bim_input_sensor.setText(fname)
    
    def out(self):
        path = QFileDialog.getExistingDirectory(None)
        self.main.lineEdit_bim_out.setText(path)
    
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

    def start(self):
        BIMprojectIFCfile_path=self.main.lineEdit_bim_input_bilding.text()
        SensorIFC_file_path=self.main.lineEdit_bim_input_sensor.text()

        f=ifcopenshell.open(BIMprojectIFCfile_path)

        site=f.by_type("IfcSite")
        BD=float(site[0][9][0])
        BM=float(site[0][9][1])
        BS=float(site[0][9][2])+float(site[0][9][3])/(10**str(site[0][9][3]).__len__()) #здесь внес изменения

        Bsite=math.radians(BD+BM/60+BS/3600)
        LD=float(site[0][10][0])
        LM=float(site[0][10][1])
        LS=float(site[0][10][2])+float(site[0][10][3])/(10**str(site[0][10][3]).__len__())#и здесь
        Lsite=math.radians(LD+LM/60+LS/3600)
        Hsite=float(site[0][11])


        self.connect()
        cursor = self.open_db.cursor()
        sql = "SELECT lat_x, lon_y, hei_z FROM POINTS"
        cursor.execute(sql)
        coord = cursor.fetchall()
        print(coord)

        rsensor=np.array([455570.60176688,3639412.00720654,5200664.00725219])

        awgs = 6378137
        e2 = 0.00669438
        H=0
        # Расчет радиуса кривизны эллипсоида в первом вертикале
        N = awgs / (math.sqrt(1 - e2 * math.sin(Bsite) * math.sin(Bsite)))
        # Расчет геоцентрических прямоугольных координат начала СК
        rsite = np.array(
            [(N + Hsite) * math.cos(Bsite) * math.cos(Lsite), (N + Hsite) * math.cos(Bsite) * math.sin(Lsite), (N * (1 - e2) + Hsite) * math.sin(Bsite)])

        # вычисление смещений координат одного датчика относительно начала локальной СК модели здания

        SensorOffset=-(rsite-rsensor)# здесь с обратным знаком должно быть


        ofsetsensorfile=self.main.lineEdit_bim_out.text() + '/out.ifc'


        #вызов процедуры смещения координат файла модели сенсора
        ifcpatch.execute({
            "input": SensorIFC_file_path,
            "output": ofsetsensorfile,
            "recipe": "OffsetObjectPlacements",
            "log": "Bimextract.log",
            "arguments": [SensorOffset[0],SensorOffset[1],SensorOffset[2],0],
        })

        # вызов процедуры слияния двух IFC файлов
        ifcpatch.execute({
            "input": BIMprojectIFCfile_path,
            "output": ofsetsensorfile,
            "recipe": "MergeProject",
            "log": "Bimextract.log",
            "arguments": [ofsetsensorfile],
        })

        self.config.read(self.path_ini)
        self.config.set("BIM", "path_out_ifc", ofsetsensorfile)
        with open(self.path_ini, "w") as config_file:
                self.config.write(config_file)
        print('OK')
        
    def open_blender(self):
        self.config.read(self.path_ini)
        try:
            ifc_path = self.config.get("BIM", "path_out_ifc")
        except Exception:
            print('No output path in BIM')
        else:
            os.system("./IfcConvert '" + ifc_path + "'")
            os.system('blender -P open_blend.py')






