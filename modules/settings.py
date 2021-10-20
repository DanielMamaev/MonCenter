import smtplib
from email.mime.text import MIMEText
from email.header import Header

from ftplib import FTP
import yadisk
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import os.path

from modules.show_logs import ShowLogs

class Settings():
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.logs = ShowLogs(parent=main)

    def send_email(self, message):
        email = "moncenter.result@gmail.com"
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.starttls()
        smtp_obj.login(email, 'tsoekbtboewzuxyy')

        now = datetime.utcnow().strftime("%m.%d.%Y-%H:%M:%S")
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = Header(now, 'utf-8')
        msg['From'] = email
        msg['To'] = self.main.lineEdit_settings_email.text()
        if not self.main.lineEdit_settings_email.text() == "":
            smtp_obj.sendmail(
                msg['From'], self.main.lineEdit_settings_email.text(), msg.as_string())
            smtp_obj.quit()
        else:
            self.logs.show_logs(
                "Не указана электронная почта для отправки уведомлений.")
    
    def gdrive_connect(self, path):
        # Подключение к Google Drive

        SCOPES = ['https://www.googleapis.com/auth/drive']
        service_account_file = self.main.lineEdit_settings_google_json.text()
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=SCOPES)
        except Exception:
            self.logs.show_logs("Файл не найден, либо проблема с файлом json")
        else:
            service = build('drive', 'v3', credentials=credentials)
            # Список файлов на диске в корневой папке
            # results = service.files().list(pageSize=10,
            # fields="nextPageToken, files(id, name, mimeType, createdTime, quotaBytesUsed )", ).execute()
            # Создание папки
            folder_id = self.main.lineEdit_settings_google_id.text()
            today = datetime.utcnow().strftime("%m.%d.%y")
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
                    self.logs.show_logs("Не удалось создать новую папку")
                else:
                    folder_id = r['id']

            # Загрузка файла измерений
            self.logs.show_logs("Загрузка файла измерений")
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
                self.logs.show_logs("Не удалось загрузить файл измерений")
            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            except Exception:
                self.logs.show_logs("Неверный id папки")

            # Загрузка файла базы данных
            self.logs.show_logs("Загрузка файла базы данных")
            name = os.path.basename(self.main.lineEdit_db_con_path.text())
            file_path = self.main.lineEdit_db_con_path.text()
            file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
            media = ""
            try:
                media = MediaFileUpload(file_path, resumable=True)
            except Exception:
                self.logs.show_logs("Не удалось загрузить файл базы данных")

            try:
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            except Exception:
                self.logs.show_logs("Неверный id папки")

    # *************************** YA.DISK ***************************
    def yadisk_connect(self, path):
        ya = yadisk.YaDisk(token=self.main.lineEdit_settings_ya_token.text())
        if ya.check_token():
            try:
                a = list(ya.listdir(self.main.lineEdit_settings_ya_folder.text()))
            except Exception:
                self.logs.show_logs("Dir is not found!")

            else:
                today = datetime.utcnow().strftime("%m.%d.%y")
                date = str(today.day) + str(today.month) + str(today.year)
                try:
                    ya.mkdir(self.main.lineEdit_settings_ya_folder.text() + date + "/")
                except Exception:
                    pass

                try:
                    ya.upload(path, self.main.lineEdit_settings_ya_folder.text(
                    ) + date + "/" + os.path.basename(path))
                except Exception:
                    self.logs.show_logs("Загрузить не удалось!")
                else:
                    self.logs.show_logs(
                        "Загрузка " + os.path.basename(path) + " на Яндекс.Диск.")

                try:
                    ya.upload(self.main.lineEdit_db_con_path.text(),
                              self.main.lineEdit_settings_ya_folder.text() + date + "/" + "database.db")
                except Exception:
                    self.logs.show_logs("...")
                else:
                    self.logs.show_logs("Загрузка базы данных на Яндекс.Диск.")

    # *************************** FTP ***************************

    def ftp_connect(self, path):
        ftp = ''
        try:
            ftp = FTP(self.main.lineEdit_settings_ftp_host.text())
            ftp.login(self.main.lineEdit_settings_ftp_username.text(),
                      self.main.lineEdit_settings_ftp_password.text())
        except Exception as e:
            self.logs.show_logs("Проблема с подключением к FTP серверу " + str(e))
        else:
            self.logs.show_logs("К FTP серверу подключились.")
            # print(ftp.retrlines('LIST')) # отображение всех файлов в каталоге
            # print(ftp.pwd()) # текущий путь

            today = datetime.utcnow().strftime("%m.%d.%y")
            flag_dir = False
            try:
                ftp.mkd(today)  # создание папки
            except Exception as e:
                if str(e) == "550 Directory already exists":
                    self.logs.show_logs("Папка уже созадана: " + str(e))
                    flag_dir = True
                else:
                    self.logs.show_logs("Проблема с созданием папки: " + str(e))
                    return
            else:
                flag_dir = True
                self.logs.show_logs('Папка создана')
                # print(ftp.retrlines('LIST'))

            if flag_dir:
                try:
                    ftp.cwd('/' + today)
                except Exception as e:
                    self.logs.show_logs("Такой папки /" + today +
                                   "не существует: " + str(e))
                    return
                else:
                    try:
                        ftp.storbinary(
                            'STOR ' + os.path.basename(path), open(path, "rb"))
                    except Exception as e:
                        self.logs.show_logs("Проблема с загрузкой файла: " + str(e))

                try:
                    ftp.storbinary('STOR ' + os.path.basename(self.main.lineEdit_db_con_path.text()),
                                   open(self.main.lineEdit_db_con_path.text(), "rb"))
                except Exception as e:
                    self.logs.show_logs("Проблема с загрузкой БД: " + str(e))
        ftp.close()
