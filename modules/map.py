import io
import folium # pip install folium
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine
import sqlite3
from modules.show_logs import ShowLogs


class OpenMap(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.logs = ShowLogs(parent=main)

        self.setWindowTitle('Map')
        self.window_width, self.window_height = 800, 800
        self.setMinimumSize(self.window_width, self.window_height)

        self.open_db = sqlite3.connect("")
        self.connect()
        cursor = self.open_db.cursor()

        sql = 'SELECT * from POINTS'
        cursor.execute(sql)
        out = cursor.fetchall()
        
        coordinate = {}
        for point in out:
            coordinate[point[4]] = [point[1], point[2]]
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        try:
            m = folium.Map(
                zoom_start=12,
                location=coordinate[list(coordinate.keys())[0]]
            )
        except:
            self.logs.show_logs('(Map) No Coordinates.')
            m = folium.Map(zoom_start=12)

        folium.raster_layers.TileLayer('Open Street Map').add_to(m)
        folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
        folium.raster_layers.TileLayer('Stamen Toner').add_to(m)
        folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m)
        folium.raster_layers.TileLayer('CartoDB Positron').add_to(m)
        folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m)
        folium.LayerControl().add_to(m)
        
        sql = 'SELECT name_r_base, name_r_rover FROM BASELINES WHERE enable = 1'
        cursor.execute(sql)
        out = cursor.fetchall()
        #print(out)
        #print(coordinate)
        for item in out:
            info = f'{item[0]} , {coordinate[item[0]]}'
            folium.Marker(location=coordinate[item[0]], tooltip=item[0], popup=info, icon=folium.Icon(color = 'red')).add_to(m)
            
            info = f'{item[1]} , {coordinate[item[1]]}'
            folium.Marker(location=coordinate[item[1]], tooltip=item[1], popup=info, icon=folium.Icon(color = 'green')).add_to(m)
            
            loc = (coordinate[item[0]], coordinate[item[1]])
            folium.PolyLine(locations=loc, color="blue", weight=3, opacity=1, tooltip=f'{item[0]} -> {item[1]}').add_to(m)
                
        data = io.BytesIO()
        m.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        layout.addWidget(webView)


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