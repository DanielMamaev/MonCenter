import os, time
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QUrl, QDateTime
from modules.show_logs import ShowLogs

class ConvBin():
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.logs = ShowLogs(parent=main)

        self.format = ['rtcm2', 'rtcm3', 'nov', 'oem3', 'ubx', 'ss2', 'hemis', 'stq', 'javad', 'nvs', 'binex', 'rinex',
                       'rt17']
        self.main.comboBox_format.addItems(self.format)

        self.rinex_ver = ['3.03', '3.02', '3.01',
                          '3.0', '2.12', '2.11', '2.10']
        self.main.comboBox_rinex.addItems(self.rinex_ver)

        self.freq_list = ['1', '2']
        self.main.comboBox_freq.addItems(self.freq_list)

        self.fname_input = ""
    
    def check_obs(self, state):
        if state != self.main.checkBox_convbin_obs.isChecked():
            self.main.lineEdit_obs.setEnabled(True)
            self.main.Button_obs.setEnabled(True)
        else:
            self.main.lineEdit_obs.setEnabled(False)
            self.main.Button_obs.setEnabled(False)

    def check_nav(self, state):
        if state != self.main.checkBox_convbin_nav.isChecked():
            self.main.lineEdit_nav.setEnabled(True)
            self.main.Button_nav.setEnabled(True)
        else:
            self.main.lineEdit_nav.setEnabled(False)
            self.main.Button_nav.setEnabled(False)

    def check_gnav(self, state):
        if state != self.main.checkBox_convbin_gnav.isChecked():
            self.main.lineEdit_convbin_gnav.setEnabled(True)
            self.main.Button_convbin_gnav.setEnabled(True)
        else:
            self.main.lineEdit_convbin_gnav.setEnabled(False)
            self.main.Button_convbin_gnav.setEnabled(False)

    def check_hnav(self, state):
        if state != self.main.checkBox_convbin_hnav.isChecked():
            self.main.lineEdit_convbin_hnav.setEnabled(True)
            self.main.Button_convbin_hnav.setEnabled(True)
        else:
            self.main.lineEdit_convbin_hnav.setEnabled(False)
            self.main.Button_convbin_hnav.setEnabled(False)

    def check_qnav(self, state):
        if state != self.main.checkBox_convbin_qnav.isChecked():
            self.main.lineEdit_convbin_qnav.setEnabled(True)
            self.main.Button_convbin_qnav.setEnabled(True)
        else:
            self.main.lineEdit_convbin_qnav.setEnabled(False)
            self.main.Button_convbin_qnav.setEnabled(False)

    def check_lnav(self, state):
        if state != self.main.checkBox_convbin_lnav.isChecked():
            self.main.lineEdit_convbin_lnav.setEnabled(True)
            self.main.Button_convbin_lnav.setEnabled(True)
        else:
            self.main.lineEdit_convbin_lnav.setEnabled(False)
            self.main.Button_convbin_lnav.setEnabled(False)

    def check_sbas(self, state):
        if state != self.main.checkBox_convbin_sbas.isChecked():
            self.main.lineEdit_convbin_sbas.setEnabled(True)
            self.main.Button_convbin_sbas.setEnabled(True)
        else:
            self.main.lineEdit_convbin_sbas.setEnabled(False)
            self.main.Button_convbin_sbas.setEnabled(False)

    def check_time_start(self, state):
        if state != self.main.checkBox_time_start.isChecked():
            self.main.dateTimeEdit_start.setEnabled(True)
        else:
            self.main.dateTimeEdit_start.setEnabled(False)

    def check_time_end(self, state):
        if state != self.main.checkBox_time_end.isChecked():
            self.main.dateTimeEdit_end.setEnabled(True)
        else:
            self.main.dateTimeEdit_end.setEnabled(False)

    def convert(self):
        command_convbin = "RTKLIB-2.4.3-b33/app/convbin/gcc/convbin"
        command_convbin += " -r " + self.main.comboBox_format.currentText()
        command_convbin += " -f " + self.main.comboBox_freq.currentText()
        command_convbin += " -v " + self.main.comboBox_rinex.currentText()
        command_convbin += " -os -od"
        if self.main.checkBox_time_start.isChecked():
            command_convbin += " -ts "
            command_convbin += self.main.dateTimeEdit_start.text()
        if self.main.checkBox_time_end.isChecked():
            command_convbin += " -te "
            command_convbin += self.main.dateTimeEdit_end.text()

        if not self.main.checkBox_gps.isChecked():
            command_convbin += " -y G"
        if not self.main.checkBox_glo.isChecked():
            command_convbin += " -y R"
        if not self.main.checkBox_galileo.isChecked():
            command_convbin += " -y E"
        if not self.main.checkBox_qzss.isChecked():
            command_convbin += " -y J"
        if not self.main.checkBox_sbas.isChecked():
            command_convbin += " -y S"
        if not self.main.checkBox_beidou.isChecked():
            command_convbin += " -y C"

        if self.main.lineEdit_obs.text() != "" and self.main.checkBox_convbin_obs.isChecked():
            command_convbin += " -o " + self.main.lineEdit_obs.text().replace(" ", '\\ ')
        if self.main.lineEdit_nav.text() != "" and self.main.checkBox_convbin_nav.isChecked():
            command_convbin += " -n " + self.main.lineEdit_nav.text().replace(" ", '\\ ')
        if self.main.lineEdit_convbin_gnav.text() != "" and self.main.checkBox_convbin_gnav.isChecked():
            command_convbin += " -g " + self.main.lineEdit_convbin_gnav.text().replace(" ", '\\ ')
        if self.main.lineEdit_convbin_hnav.text() != "" and self.main.checkBox_convbin_hnav.isChecked():
            command_convbin += " -h " + self.main.lineEdit_convbin_hnav.text().replace(" ", '\\ ')
        if self.main.lineEdit_convbin_qnav.text() != "" and self.main.checkBox_convbin_qnav.isChecked():
            command_convbin += " -q " + self.main.lineEdit_convbin_qnav.text().replace(" ", '\\ ')
        if self.main.lineEdit_convbin_lnav.text() != "" and self.main.checkBox_convbin_qnav.isChecked():
            command_convbin += " -l " + self.main.lineEdit_convbin_qnav.text().replace(" ", '\\ ')
        if self.main.lineEdit_convbin_sbas.text() != "" and self.main.checkBox_convbin_sbas.isChecked():
            command_convbin += " -s " + self.main.lineEdit_convbin_sbas.text().replace(" ", '\\ ') 

        command_convbin += " " + self.main.lineEdit_input.text().replace(" ", '\\ ')
        self.logs.show_logs(command_convbin)
        os.system("\n" + command_convbin)
        time.sleep(1)

    def input_path(self):
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
                self.main.dateTimeEdit_start.setDateTime(time_start)
                self.logs.show_logs("")
                self.logs.show_logs(str(time_start))
                self.main.checkBox_time_start.setChecked(True)
        else:
            self.main.checkBox_time_start.setChecked(False)

        self.main.lineEdit_input.setText(fname)

        self.main.lineEdit_obs.setText(self.main.lineEdit_input.text() + ".obs")
        self.main.lineEdit_nav.setText(self.main.lineEdit_input.text() + ".nav")
        self.main.lineEdit_convbin_gnav.setText(
            self.main.lineEdit_input.text() + ".gnav")
        self.main.lineEdit_convbin_hnav.setText(
            self.main.lineEdit_input.text() + ".hnav")
        self.main.lineEdit_convbin_qnav.setText(
            self.main.lineEdit_input.text() + ".qnav")
        self.main.lineEdit_convbin_lnav.setText(
            self.main.lineEdit_input.text() + ".lnav")
        self.main.lineEdit_convbin_sbas.setText(
            self.main.lineEdit_input.text() + ".sbas")

    def output_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        self.main.lineEdit_output.setText(path)

    def obs_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.obs'
        self.main.lineEdit_obs.setText(path)

    def nav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.nav'
        self.main.lineEdit_nav.setText(path)

    def gnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.gnav'
        self.main.lineEdit_convbin_gnav.setText(path)

    def hnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.hnav'
        self.main.lineEdit_convbin_hnav.setText(path)

    def qnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.qnav'
        self.main.lineEdit_convbin_qnav.setText(path)

    def lnav_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.lnav'
        self.main.lineEdit_convbin_lnav.setText(path)

    def sbas_path(self):
        path = QFileDialog.getExistingDirectory(None)
        if path == "":
            return
        path += '/' + self.fname_input + '.sbas'
        self.main.lineEdit_convbin_sbas.setText(path)