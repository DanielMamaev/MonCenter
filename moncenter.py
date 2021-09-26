from re import S
from modules.str2str import Str2Str
from modules.convbin import ConvBin
from modules.rnx2rtkp import Rnx2Rtkp
from modules.database import DataBase
from modules.com_port import ComPort
from modules.settings import Settings
from modules.config_ini import ConfigIni
from modules.filter_sdf import FilterSDF


from PyQt5 import QtWidgets
import design




# ******************************************* MAIN *******************************************
class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
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
        self.Button_db_start.clicked.connect(self.db_tab.start_str2str)
        self.Button_db_save.clicked.connect(self.db_tab.dir_save)
        self.Button_db_stop.clicked.connect(self.db_tab.stop)
        self.checkBox_db_reset.stateChanged.connect(self.db_tab.check_str2str)
        self.checkBox_db_post.stateChanged.connect(self.db_tab.check_post)
        self.Button_db_timepost_ok.clicked.connect(self.db_tab.posttime)
        self.Button_db_sql.clicked.connect(self.db_tab.sql_command)

        # ------------- COM
        self.com_port = ComPort(main=self)
        self.com_port.update()
        self.action_refresh_ports.triggered.connect(self.com_port.update)
        self.pushButton_connect.clicked.connect(self.com_port.connect)
        self.pushButton_refresh.clicked.connect(self.com_port.refresh)
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



def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
