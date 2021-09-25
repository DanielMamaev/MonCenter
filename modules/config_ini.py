import design
import configparser
import sys
import os

from modules.show_logs import ShowLogs

class ConfigIni():

    def __init__(self, main):
        super().__init__()
        self.main = main

        self.path_ini = "conf.ini"
        self.logs = ShowLogs(parent=main)

    def save_exit(self):
        self.save()
        sys.exit()

    def reset(self):
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
            self.logs.show_logs("The file conf.ini is corrupted or not found.")
        else:
            with open(self.path_ini, "w") as config_file:
                config.write(config_file)
            self.start()

    def save(self):
        config = configparser.ConfigParser()
        try:
            config.read(self.path_ini)
            config.set("STR2STR", "create_folder", str(
                self.main.action_create_folder.isChecked()))
            config.set("STR2STR", "autoclose_xterm", str(
                self.main.action_autoclose_xterm.isChecked()))
            config.set("CONVBIN", "check_start", str(
                self.main.checkBox_time_start.isChecked()))
            config.set("CONVBIN", "check_end", str(
                self.main.checkBox_time_end.isChecked()))
            config.set("CONVBIN", "format", self.main.comboBox_format.currentText())
            config.set("CONVBIN", "rinex", self.main.comboBox_rinex.currentText())
            config.set("CONVBIN", "frequencies",
                       self.main.comboBox_freq.currentText())
            config.set("CONVBIN", "sat_gps", str(
                self.main.checkBox_gps.isChecked()))
            config.set("CONVBIN", "sat_glo", str(
                self.main.checkBox_glo.isChecked()))
            config.set("CONVBIN", "sat_galileo", str(
                self.main.checkBox_galileo.isChecked()))
            config.set("CONVBIN", "sat_qzss", str(
                self.main.checkBox_qzss.isChecked()))
            config.set("CONVBIN", "sat_sbas", str(
                self.main.checkBox_sbas.isChecked()))
            config.set("CONVBIN", "sat_beidou", str(
                self.main.checkBox_beidou.isChecked()))
            config.set("CONVBIN", "check_obs", str(
                self.main.checkBox_convbin_obs.isChecked()))
            config.set("CONVBIN", "check_nav", str(
                self.main.checkBox_convbin_nav.isChecked()))
            config.set("CONVBIN", "check_gnav", str(
                self.main.checkBox_convbin_gnav.isChecked()))
            config.set("CONVBIN", "check_hnav", str(
                self.main.checkBox_convbin_hnav.isChecked()))
            config.set("CONVBIN", "check_qnav", str(
                self.main.checkBox_convbin_qnav.isChecked()))
            config.set("CONVBIN", "check_lnav", str(
                self.main.checkBox_convbin_lnav.isChecked()))
            config.set("CONVBIN", "check_sbas", str(
                self.main.checkBox_convbin_sbas.isChecked()))
            config.set("RNX2RTKP", "pos_mode",
                       self.main.comboBox_rnx2rtkp_pos_mode.currentText())
            config.set("RNX2RTKP", "frequencies",
                       self.main.comboBox_rnx2rtkp_freq.currentText())
            config.set("RNX2RTKP", "sol_format",
                       self.main.comboBox_rnx2rtkp_sol_format.currentText())
            config.set("RNX2RTKP", "time_format",
                       self.main.comboBox_rnx2rtkp_time_format.currentText())
            config.set("RNX2RTKP", "mask", self.main.lineEdit_rnx2rtkp_mask.text())
            config.set("RNX2RTKP", "decimals",
                       self.main.lineEdit_rnx2rtkp_dec.text())
            config.set("RNX2RTKP", "base_station",
                       self.main.comboBox_rnx2rtkp_base.currentText())
            config.set("RNX2RTKP", "edit1", self.main.lineEdit_rnx2rtkp_1.text())
            config.set("RNX2RTKP", "edit2", self.main.lineEdit_rnx2rtkp_2.text())
            config.set("RNX2RTKP", "edit3", self.main.lineEdit_rnx2rtkp_3.text())
            config.set("COM", "speed", self.main.comboBox_speed.currentText())
            config.set("COM", "autoscroll", str(
                self.main.checkBox_scroll.isChecked()))
            config.set("COM", "time", str(self.main.checkBox_time.isChecked()))
            config.set("DATABASE", "time_reset", str(
                self.main.checkBox_db_reset.isChecked()))
            config.set("DATABASE", "time_post", str(
                self.main.checkBox_db_post.isChecked()))
            config.set("DATABASE", "last_post", str(
                self.main.checkBox_db_lastpost.isChecked()))
            config.set("DATABASE", "connect_to",
                       self.main.lineEdit_db_con_path.text())
            config.set("DATABASE", "save_to", self.main.lineEdit_db_save.text())
            config.set("DATABASE", "delta", self.main.lineEdit_db_delta.text())
            config.set("SETTINGS", "email",
                       self.main.lineEdit_settings_email.text())
            config.set("SETTINGS", "ftp_host",
                       self.main.lineEdit_settings_ftp_host.text())
            config.set("SETTINGS", "ftp_username",
                       self.main.lineEdit_settings_ftp_username.text())
            config.set("SETTINGS", "ftp_password",
                       self.main.lineEdit_settings_ftp_password.text())
            config.set("SETTINGS", "ftp_autoconnect", str(
                self.main.checkBox_settings_ftp_autoconnect.isChecked()))
            config.set("SETTINGS", "ya_token",
                       self.main.lineEdit_settings_ya_token.text())
            config.set("SETTINGS", "ya_folder",
                       self.main.lineEdit_settings_ya_folder.text())
            config.set("SETTINGS", "ya_autoconnect", str(
                self.main.checkBox_settings_ya_autoconnect.isChecked()))
            config.set("SETTINGS", "google_json",
                       self.main.lineEdit_settings_google_json.text())
            config.set("SETTINGS", "google_id",
                       self.main.lineEdit_settings_google_id.text())
            config.set("SETTINGS", "google_autoconnect", str(
                self.main.checkBox_settings_google_autoconnect.isChecked()))
            config.set("SETTINGS", "output_str_active", str(
                self.main.action_debug_stream.isChecked()))
        except Exception:
            self.logs.show_logs("The file conf.ini is corrupted or not found.")
        else:
            with open(self.path_ini, "w") as config_file:
                config.write(config_file)

    def start(self):
        if not os.path.exists(self.path_ini):
            self.logs.show_logs("The file conf.ini does not exist!")

            return

        config = configparser.ConfigParser()
        config.read(self.path_ini)

        try:
            # --- STR2STR
            self.main.action_create_folder.setChecked(
                config.getboolean("STR2STR", "create_folder"))
            self.main.action_autoclose_xterm.setChecked(
                config.getboolean("STR2STR", "autoclose_xterm"))

            # --- CONVBIN
            self.main.checkBox_time_start.setChecked(
                config.getboolean("CONVBIN", "check_start"))
            self.main.checkBox_time_end.setChecked(
                config.getboolean("CONVBIN", "check_end"))
            self.main.comboBox_format.setCurrentText(
                config.get("CONVBIN", "format"))
            self.main.comboBox_rinex.setCurrentText(config.get("CONVBIN", "rinex"))
            self.main.comboBox_freq.setCurrentText(
                config.get("CONVBIN", "frequencies"))

            self.main.checkBox_gps.setChecked(
                config.getboolean("CONVBIN", "sat_gps"))
            self.main.checkBox_glo.setChecked(
                config.getboolean("CONVBIN", "sat_glo"))
            self.main.checkBox_galileo.setChecked(
                bool(config.getboolean("CONVBIN", "sat_galileo")))
            self.main.checkBox_qzss.setChecked(
                bool(config.getboolean("CONVBIN", "sat_qzss")))
            self.main.checkBox_sbas.setChecked(
                bool(config.getboolean("CONVBIN", "sat_sbas")))
            self.main.checkBox_beidou.setChecked(
                bool(config.getboolean("CONVBIN", "sat_beidou")))

            self.main.checkBox_convbin_obs.setChecked(
                config.getboolean("CONVBIN", "check_obs"))
            self.main.checkBox_convbin_nav.setChecked(
                config.getboolean("CONVBIN", "check_nav"))
            self.main.checkBox_convbin_gnav.setChecked(
                config.getboolean("CONVBIN", "check_gnav"))
            self.main.checkBox_convbin_hnav.setChecked(
                config.getboolean("CONVBIN", "check_hnav"))
            self.main.checkBox_convbin_qnav.setChecked(
                config.getboolean("CONVBIN", "check_qnav"))
            self.main.checkBox_convbin_lnav.setChecked(
                config.getboolean("CONVBIN", "check_lnav"))
            self.main.checkBox_convbin_sbas.setChecked(
                config.getboolean("CONVBIN", "check_sbas"))

            # --- RNX2RTKP
            self.main.comboBox_rnx2rtkp_pos_mode.setCurrentText(
                config.get("RNX2RTKP", "pos_mode"))
            self.main.comboBox_rnx2rtkp_freq.setCurrentText(
                config.get("RNX2RTKP", "frequencies"))
            self.main.comboBox_rnx2rtkp_sol_format.setCurrentText(
                config.get("RNX2RTKP", "sol_format"))
            self.main.comboBox_rnx2rtkp_time_format.setCurrentText(
                config.get("RNX2RTKP", "time_format"))
            self.main.lineEdit_rnx2rtkp_mask.setText(config.get("RNX2RTKP", "mask"))
            self.main.lineEdit_rnx2rtkp_dec.setText(
                config.get("RNX2RTKP", "decimals"))
            self.main.comboBox_rnx2rtkp_base.setCurrentText(
                config.get("RNX2RTKP", "base_station"))
            self.main.lineEdit_rnx2rtkp_1.setText(config.get("RNX2RTKP", "edit1"))
            self.main.lineEdit_rnx2rtkp_2.setText(config.get("RNX2RTKP", "edit2"))
            self.main.lineEdit_rnx2rtkp_3.setText(config.get("RNX2RTKP", "edit3"))

            # --- COM
            self.main.comboBox_speed.setCurrentText(config.get("COM", "speed"))
            self.main.checkBox_scroll.setChecked(
                config.getboolean("COM", "autoscroll"))
            self.main.checkBox_time.setChecked(config.getboolean("COM", "time"))

            # --- DATABASE
            self.main.checkBox_db_reset.setChecked(
                config.getboolean("DATABASE", "time_reset"))
            self.main.checkBox_db_post.setChecked(
                config.getboolean("DATABASE", "time_post"))
            self.main.checkBox_db_lastpost.setChecked(
                config.getboolean("DATABASE", "last_post"))
            self.main.lineEdit_db_con_path.setText(
                config.get("DATABASE", "connect_to"))
            self.main.lineEdit_db_save.setText(config.get("DATABASE", "save_to"))
            self.main.lineEdit_db_delta.setText(config.get("DATABASE", "delta"))
            if self.main.checkBox_db_reset.isChecked():
                self.main.timeEdit_db.setEnabled(True)

            # --- SETTINGS
            self.main.lineEdit_settings_email.setText(
                config.get("SETTINGS", "email"))
            self.main.lineEdit_settings_ftp_host.setText(
                config.get("SETTINGS", "ftp_host"))
            self.main.lineEdit_settings_ftp_username.setText(
                config.get("SETTINGS", "ftp_username"))
            self.main.lineEdit_settings_ftp_password.setText(
                config.get("SETTINGS", "ftp_password"))
            self.main.checkBox_settings_ftp_autoconnect.setChecked(
                config.getboolean("SETTINGS", "ftp_autoconnect"))
            self.main.lineEdit_settings_ya_token.setText(
                config.get("SETTINGS", "ya_token"))
            self.main.lineEdit_settings_ya_folder.setText(
                config.get("SETTINGS", "ya_folder"))
            self.main.checkBox_settings_ya_autoconnect.setChecked(
                config.getboolean("SETTINGS", "ya_autoconnect"))
            self.main.lineEdit_settings_google_json.setText(
                config.get("SETTINGS", "google_json"))
            self.main.lineEdit_settings_google_id.setText(
                config.get("SETTINGS", "google_id"))
            self.main.checkBox_settings_google_autoconnect.setChecked(
                config.getboolean("SETTINGS", "google_autoconnect"))
            self.main.action_debug_stream.setChecked(
                config.getboolean("SETTINGS", "output_str_active"))
        except Exception:
            self.logs.show_logs("The file conf.ini is corrupted.")