from PyQt5.QtWidgets import QFileDialog
import os
from modules.show_logs import ShowLogs

class Str2Str():

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.logs = ShowLogs(parent=main)    
    
    def flag_output1(self, state):
        if state == self.main.checkBox_str2str_out1.isChecked():
            self.main.tab_output1.setEnabled(False)
        else:
            self.main.tab_output1.setEnabled(True)
            self.main.tabWidget_str2str_out.setCurrentIndex(0)

    def flag_output2(self, state):
        if state == self.main.checkBox_str2str_out2.isChecked():
            self.main.tab_output2.setEnabled(False)
        else:
            self.main.tab_output2.setEnabled(True)
            self.main.tabWidget_str2str_out.setCurrentIndex(1)

    def flag_output3(self, state):
        if state == self.main.checkBox_str2str_out3.isChecked():
            self.main.tab_output3.setEnabled(False)
        else:
            self.main.tab_output3.setEnabled(True)
            self.main.tabWidget_str2str_out.setCurrentIndex(2)

    def check_outputflile(self, state):
        if state != self.main.checkBox_str2str_file.isChecked():
            self.main.lineEdit_str2str_outputfile.setEnabled(True)
            self.main.Button_str2str_outputfile.setEnabled(True)
        else:
            self.main.lineEdit_str2str_outputfile.setEnabled(False)
            self.main.Button_str2str_outputfile.setEnabled(False)

    def outputfile_path(self):
        path, _ = QFileDialog.getSaveFileName()
        self.main.lineEdit_str2str_out_file.setText(path + ".log")

    def outputfile_path_2(self):
        path, _ = QFileDialog.getSaveFileName()
        self.main.lineEdit_str2str_out_file_2.setText(path + ".log")

    def outputfile_path_3(self):
        path, _ = QFileDialog.getSaveFileName()
        self.main.lineEdit_str2str_out_file_3.setText(path + ".log")

    def inputfile_path(self):
        path, _ = QFileDialog.getOpenFileName()
        self.main.lineEdit_str2str_in_file.setText(path + ".log")

    def start(self):
        command_str2str = "xterm -e \"/bin/bash -c '" + os.getcwd() + "/RTKLIB-2.4.3-b33/app/str2str/gcc/" + \
                          "str2str' -in "
        if self.main.tabWidget_str2str_in.currentIndex() == 0:
            command_str2str += "serial://"
            command_str2str += self.main.comboBox_str2str_in_ser_port.currentText().replace('/dev/', '')
            command_str2str += ":" + self.main.comboBox_str2str_in_ser_speed.currentText()
            command_str2str += ":" + self.main.comboBox_str2str_in_ser_bsize.currentText()
            command_str2str += ":" + self.main.comboBox_str2str_in_ser_parity.currentText()
            command_str2str += ":" + self.main.comboBox_str2str_in_ser_stopb.currentText()
            command_str2str += ":" + self.main.comboBox_str2str_in_ser_fctr.currentText()

        elif self.main.tabWidget_str2str_in.currentIndex() == 1:
            command_str2str += "tcpsvr://:"
            command_str2str += self.main.lineEdit_str2str_in_tcpsvr_port.text()

        elif self.main.tabWidget_str2str_in.currentIndex() == 2:
            command_str2str += "tcpcli://"
            command_str2str += self.main.lineEdit_str2str_in_tcpcli_host.text()

        elif self.main.tabWidget_str2str_in.currentIndex() == 3:
            command_str2str += "ntrip://"
            command_str2str += self.main.lineEdit_str2str_in_ntrip_userid.text() + ":" + \
                self.main.lineEdit_str2str_in_ntrip_pass.text()

            command_str2str += "@" + self.main.lineEdit_str2str_in_ntrip_host.text() + "/" + \
                               self.main.lineEdit_str2str_in_ntrip_mountpoint.text()

        elif self.main.tabWidget_str2str_in.currentIndex() == 4:
            command_str2str += "file://"
            command_str2str += self.main.lineEdit_str2str_in_file.text()

        # ПЕРВАЯ ФОРМА
        if self.main.checkBox_str2str_out1.isChecked():
            command_str2str += " -out "
            if self.main.tabWidget_str2str_out_1.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.main.comboBox_str2str_out_ser_port.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_speed.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_bsize.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_parity.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_stopb.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_fctr.currentText()

            if self.main.tabWidget_str2str_out_1.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.main.lineEdit_str2str_out_tcpsvr_port.text()

            if self.main.tabWidget_str2str_out_1.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.main.lineEdit_str2str_out_tcpcli_host.text()

            if self.main.tabWidget_str2str_out_1.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.main.lineEdit_str2str_out_ntrip_userid.text() + ":" + \
                    self.main.lineEdit_str2str_out_ntrip_pass.text()

                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrip_host.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrip_mountpoint.text()

            if self.main.tabWidget_str2str_out_1.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.main.lineEdit_str2str_out_ntrips_pass.text()
                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrips_host.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrips_mountpoint.text()

            if self.main.tabWidget_str2str_out_1.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.main.lineEdit_str2str_out_file.text().replace(" ", '\\ ')

        # ВТОРАЯ ФОРМА
        if self.main.checkBox_str2str_out2.isChecked():
            command_str2str += " -out "
            if self.main.tabWidget_str2str_out_2.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.main.comboBox_str2str_out_ser_port_2.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_speed_2.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_bsize_2.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_parity_2.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_stopb_2.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_fctr_2.currentText()

            if self.main.tabWidget_str2str_out_2.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.main.lineEdit_str2str_out_tcpsvr_port_2.text()

            if self.main.tabWidget_str2str_out_2.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.main.lineEdit_str2str_out_tcpcli_host_2.text()

            if self.main.tabWidget_str2str_out_2.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.main.lineEdit_str2str_out_ntrip_userid_2.text() + ":" + \
                    self.main.lineEdit_str2str_out_ntrip_pass_2.text()

                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrip_host_2.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrip_mountpoint_2.text()

            if self.main.tabWidget_str2str_out_2.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.main.lineEdit_str2str_out_ntrips_pass_2.text()
                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrips_host_2.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrips_mountpoint_2.text()

            if self.main.tabWidget_str2str_out_2.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.main.lineEdit_str2str_out_file_2.text().replace(" ", '\\ ')

        # ТРЕТЬЯ ФОРМА
        if self.main.checkBox_str2str_out3.isChecked():
            command_str2str += " -out "
            if self.main.tabWidget_str2str_out_3.currentIndex() == 0:
                command_str2str += "serial://"
                command_str2str += self.main.comboBox_str2str_out_ser_port_3.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_speed_3.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_bsize_3.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_parity_3.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_stopb_3.currentText()
                command_str2str += ":" + self.main.comboBox_str2str_out_ser_fctr_3.currentText()

            if self.main.tabWidget_str2str_out_3.currentIndex() == 1:
                command_str2str += "tcpsvr://:"
                command_str2str += self.main.lineEdit_str2str_out_tcpsvr_port_3.text()

            if self.main.tabWidget_str2str_out_3.currentIndex() == 2:
                command_str2str += "tcpcli://"
                command_str2str += self.main.lineEdit_str2str_out_tcpcli_host_3.text()

            if self.main.tabWidget_str2str_out_3.currentIndex() == 3:
                command_str2str += "ntrip://"
                command_str2str += self.main.lineEdit_str2str_out_ntrip_userid_3.text() + ":" + \
                    self.main.lineEdit_str2str_out_ntrip_pass_3.text()

                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrip_host_3.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrip_mountpoint_3.text()

            if self.main.tabWidget_str2str_out_3.currentIndex() == 4:
                command_str2str += "ntrips://"
                command_str2str += ":" + self.main.lineEdit_str2str_out_ntrips_pass_3.text()
                command_str2str += "@" + self.main.lineEdit_str2str_out_ntrips_host_3.text() + "/" + \
                                   self.main.lineEdit_str2str_out_ntrips_mountpoint_3.text()

            if self.main.tabWidget_str2str_out_3.currentIndex() == 5:
                command_str2str += "file://"
                command_str2str += self.main.lineEdit_str2str_out_file_3.text().replace(" ", '\\ ')

        command_str2str += "\"&"
        self.logs.show_logs(command_str2str)
        os.system(command_str2str)

    def stop(self):
        os.system("killall str2str")

    def stop_xterm(self):
        os.system("killall xterm")