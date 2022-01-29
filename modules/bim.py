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

class BIM():
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.open_db = sqlite3.connect("")
        self.logs = ShowLogs(parent=main)
        

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
        print(site)
        BD=float(site[0][9][0])
        BM=float(site[0][9][1])
        BS=float(site[0][9][2])
        Bsite=math.radians(BD+BM/60+BS/3600)
        LD=float(site[0][10][0])
        LM=float(site[0][10][1])
        LS=float(site[0][10][2])
        Lsite=math.radians(LD+LM/60+LS/3600)

        self.connect()
        cursor = self.open_db.cursor()
        sql = "SELECT lat_x, lon_y, hei_z FROM POINTS"
        cursor.execute(sql)
        coord = cursor.fetchall()
        print(coord)

        rsensor=np.array([coord[0][1],coord[0][1],coord[0][2]])

        awgs = 6378137
        e2 = 0.00669438
        H=0
        # Расчет радиуса кривизны эллипсоида в первом вертикале
        N = awgs / (math.sqrt(1 - e2 * math.sin(Bsite) * math.sin(Bsite)))
        # Расчет геоцентрических прямоугольных координат начала СК
        rsite = np.array(
            [(N + H) * math.cos(Bsite) * math.cos(Lsite), (N + H) * math.cos(Bsite) * math.sin(Lsite), (N * (1 - e2) + H) * math.sin(Bsite)])

        # вычисление смещений координат одного датчика относительно начала локальной СК модели здания

        SensorOffset=rsite-rsensor


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





