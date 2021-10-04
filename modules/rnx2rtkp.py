from modules.show_logs import ShowLogs
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QUrl
import os, time

class Rnx2Rtkp():
    def __init__(self, main):
        self.main = main
        self.logs = ShowLogs(parent=main)

    def conf_file_check(self, state):
        if state != self.main.checkBox_rnx2rtkp_conf.isChecked():
            self.main.lineEdit_rnx2rtkp_conf.setEnabled(True)
        else:
            self.main.lineEdit_rnx2rtkp_conf.setEnabled(False)

    def time_start_check(self, state):
        if state != self.main.checkBox_rnx2rtkp_time_start.isChecked():
            self.main.dateTimeEdit_rnx2rtkp_start.setEnabled(True)
        else:
            self.main.dateTimeEdit_rnx2rtkp_start.setEnabled(False)

    def time_end_check(self, state):
        if state != self.main.checkBox_rnx2rtkp_time_end.isChecked():
            self.main.dateTimeEdit_rnx2rtkp_end.setEnabled(True)
        else:
            self.main.dateTimeEdit_rnx2rtkp_end.setEnabled(False)

    def input_conf(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_rnx2rtkp_conf.setText(fname)

    def input_rover(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        if fname == "":
            return
        self.main.lineEdit_rnx2rtkp_rover.setText(fname)

        p = QUrl.fromLocalFile(fname)
        p = p.fileName()
        p = p.rsplit('.', 1)
        if len(p) == 2:
            self.logs.show_logs(str(p))
            fname_input = p[0]
            pa = fname
            fname_path = pa.replace(fname_input + '.' + p[1], "")
            fname_output_pos = fname_path + fname_input + ".pos"
            self.main.lineEdit_rnx2rtkp_output.setText(fname_output_pos)
        else:
            self.logs.show_logs("Specify the extension!")

    def input_base(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_rnx2rtkp_base.setText(fname)

    def input_nav(self):
        fname, _ = QFileDialog.getOpenFileName(None)
        self.main.lineEdit_rnx2rtkp_nav.setText(fname)

    def output(self):
        fname = QFileDialog.getExistingDirectory(None)
        self.main.lineEdit_rnx2rtkp_output.setText(fname)

    def start(self):
        command_rnx2rtkp = "RTKLIB-2.4.3-b33/app/rnx2rtkp/gcc/rnx2rtkp"
        if self.main.checkBox_rnx2rtkp_conf.isChecked():
            command_rnx2rtkp += " -k " + self.main.lineEdit_rnx2rtkp_conf.text()
        else:
            if self.main.checkBox_rnx2rtkp_time_start.isChecked():
                dt = self.main.dateTimeEdit_rnx2rtkp_start.text()
                dts = dt.rsplit(" ")
                command_rnx2rtkp += " -ts " + str(dts[0]) + " " + str(dts[1])

            if self.main.checkBox_rnx2rtkp_time_end.isChecked():
                dt = self.main.dateTimeEdit_rnx2rtkp_end.text()
                dts = dt.rsplit(" ")
                command_rnx2rtkp += " -te " + str(dts[0]) + " " + str(dts[1])

            command_rnx2rtkp += " -p " + \
                str(self.main.comboBox_rnx2rtkp_pos_mode.currentIndex())
            command_rnx2rtkp += " -m " + self.main.lineEdit_rnx2rtkp_mask.text()
            command_rnx2rtkp += " -f " + \
                str(self.main.comboBox_rnx2rtkp_freq.currentIndex() + 1)

            if self.main.comboBox_rnx2rtkp_sol_format.currentIndex() == 1:
                command_rnx2rtkp += " -g"
            elif self.main.comboBox_rnx2rtkp_sol_format.currentIndex() == 2:
                command_rnx2rtkp += " -e"
            elif self.main.comboBox_rnx2rtkp_sol_format.currentIndex() == 3:
                command_rnx2rtkp += " -a"
            elif self.main.comboBox_rnx2rtkp_sol_format.currentIndex() == 4:
                command_rnx2rtkp += " -n"

            if self.main.comboBox_rnx2rtkp_time_format.currentIndex() == 0:
                command_rnx2rtkp += " -t"

            command_rnx2rtkp += " -d " + self.main.lineEdit_rnx2rtkp_dec.text()

            if self.main.comboBox_rnx2rtkp_base.currentIndex() == 0:
                command_rnx2rtkp += " -l " + str(self.main.lineEdit_rnx2rtkp_1.text()) + " " + str(
                    self.main.lineEdit_rnx2rtkp_2.text()) + " " + str(self.main.lineEdit_rnx2rtkp_3.text())
            else:
                command_rnx2rtkp += " -r " + str(self.main.lineEdit_rnx2rtkp_1.text()) + " " + str(
                    self.main.lineEdit_rnx2rtkp_2.text()) + " " + str(self.main.lineEdit_rnx2rtkp_3.text())

        command_rnx2rtkp += " -o " + self.main.lineEdit_rnx2rtkp_output.text().replace(" ", '\\ ')
        command_rnx2rtkp += " " + self.main.lineEdit_rnx2rtkp_rover.text().replace(" ", '\\ ')
        command_rnx2rtkp += " " + self.main.lineEdit_rnx2rtkp_base.text().replace(" ", '\\ ')
        command_rnx2rtkp += " " + self.main.lineEdit_rnx2rtkp_nav.text().replace(" ", '\\ ')

        self.logs.show_logs(command_rnx2rtkp)
        os.system(command_rnx2rtkp)
        time.sleep(1)

        if os.path.exists(self.main.lineEdit_rnx2rtkp_output.text()):
            self.logs.show_logs("ok")
        else:
            self.logs.show_logs(self.main.lineEdit_rnx2rtkp_output.text() + " Not Found")
            return