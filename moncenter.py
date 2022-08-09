import sys
import time 
import os


from PyQt5.QtGui import QPixmap
from modules.str2str import Str2Str
from modules.convbin import ConvBin
from modules.rnx2rtkp import Rnx2Rtkp
from modules.database import DataBase
from modules.com_port import ComPort
from modules.settings import Settings
from modules.config_ini import ConfigIni
from modules.filter_sdf import FilterSDF
from modules.map import OpenMap

import forms.main_form as main_form
import forms.about as about
import forms.auto_mode

from modules.bim import BIM

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
from datetime import datetime



class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

# ******************************************* ABOUT *******************************************

class About(QtWidgets.QMainWindow, about.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        

# ******************************************* MAIN *******************************************
class MainWindow(QtWidgets.QMainWindow, main_form.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        

        self.tabWidget.setTabBar(TabBar(self.tabWidget))
        self.tabWidget.setTabPosition(self.tabWidget.West)
        self.tabWidget.insertTab(1, self.tab, "STR2STR")
        self.tabWidget.insertTab(2, self.tab, "CONVBIN")
        self.tabWidget.insertTab(3, self.tab, "RNX2RTKP")
        self.tabWidget.insertTab(4, self.tab, "Database")
        self.tabWidget.insertTab(5, self.tab, "BIM")
        self.tabWidget.insertTab(6, self.tab, "COM")
        self.tabWidget.insertTab(7, self.tab, "Settings")
        self.tabWidget.insertTab(8, self.tab, "Logs")
        self.tabWidget.insertTab(9, self.tab, "Fileter SDF")

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
        self.db_tab = DataBase(main=self)
        self.Button_db_new_create.clicked.connect(self.db_tab.create)
        self.Button_db_new_path.clicked.connect(self.db_tab.path_new)
        self.Button_db_con_path.clicked.connect(self.db_tab.path_connect)
        self.Button_db_connect.clicked.connect(self.db_tab.connect)
        self.Button_db_save.clicked.connect(self.db_tab.dir_save)
        self.Button_db_sql.clicked.connect(self.db_tab.sql_command)
        self.Button_db_browser.clicked.connect(self.db_tab.open_sqlite_browser)

        self.action_autopost_start.triggered.connect(self.db_tab.start_str2str)
        self.action_autopost_stop.triggered.connect(self.db_tab.stop)

        # ------------- COM
        self.com_port = ComPort(main=self)
        self.com_port.update()
        self.action_refresh_ports.triggered.connect(self.com_port.update)
        self.pushButton_connect.clicked.connect(self.com_port.connect)
        self.pushButton_send.clicked.connect(self.com_port.send)
        self.pushButton_clear.clicked.connect(self.com_port.clear)
        self.comboBox_comm.addItems(self.com_port.command_list)

        # ------------- filterSDF
        self.filterSDF = FilterSDF(main=self)
        self.pushButton_filterSDF_inputPath.clicked.connect(
            self.filterSDF.input_path)
        self.pushButton_filterSDF_outputPath.clicked.connect(
            self.filterSDF.output_path)
        self.pushButton_filterSDF_start.clicked.connect(self.filterSDF.start)

        # ------------- Map
        self.map = None
        self.Button_db_openMap.clicked.connect(self.showMap)

        # ------------- About
        self.ab = None
        self.action_About.triggered.connect(self.showAbout)


        # ------------- BIM
        self.bim = BIM(main=self)
        self.Button_bim_inputBilding.clicked.connect(self.bim.open_bilding)
        self.Button_bim_inputSensor.clicked.connect(self.bim.open_sensor)
        self.Button_bim_out.clicked.connect(self.bim.out)
        self.Button_bim_start.clicked.connect(self.bim.start)
        self.Button_bim_open.clicked.connect(self.bim.open_blender)
        
   
    def showMap(self):
        if self.map is None:
            self.map = OpenMap(main=self)
        self.map.show()
    
    def showAbout(self):
        if self.ab is None:
            self.ab = About()
        self.ab.show()
        




class StartAutoMode(QtWidgets.QMainWindow, forms.auto_mode.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        pixmap = QPixmap('icon/attention.png')
        self.label_2.setPixmap(pixmap)

        self.flag = False
        from threading import Thread
        self.thread1 = Thread(target=self.go_timer)
        self.thread1.start()

    def accept(self):
        self.flag = True
        window = MainWindow()
        window.db_tab.start_str2str()
        self.close()
        
    
    def reject(self):
        self.flag = True
        self.close()

    def go_timer(self):
        sec = list(range(0, 11))
        sec.reverse()
        
        for i in sec:
                self.label_time.setText(str(i)+'s')
                time.sleep(1)

                if self.flag:
                    break
                if i == 0:
                    self.accept()     
                
                

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    start_autoMode = StartAutoMode()
    start_autoMode.show()
        
    app.exec_()


if __name__ == '__main__':
    main()
