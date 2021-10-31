from datetime import datetime
import forms.main_form as main_form

class ShowLogs(main_form.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        
    
    def show_logs(self, text):
        print("\n" + text)
        today = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
        self.parent.plainTextEdit_logs.appendPlainText(str(today) + " -> " + text)
        f = open("logs/program/logs.txt", "a")
        f.write(str(today) + " -> " + text + "\n")
        f.close()