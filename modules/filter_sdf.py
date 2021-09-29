import os
import time
from datetime import datetime, timedelta
import design
from PyQt5.QtWidgets import QFileDialog
import pathlib

class FilterSDF(design.Ui_MainWindow):

    def __init__(self, main):
        super().__init__()
        self.main = main

    #173-193 #111 #304 общ

    def temp_path_list(self):
        path_list = []
        for i in range(173, 478):
            exit_c = False
            for j in range(0, 25):
                if i > 366:
                    t = '/home/danisimo/Рабочий стол/R1_post_kinem/r001' + str(i-366).zfill(3) + str(j) + '.21pos'
                else:
                    t = '/home/danisimo/Рабочий стол/R1_post_kinem/r001' + str(i).zfill(3) + str(j) + '.20pos'
                if os.path.exists(t):
                    path_list.append(t)
                    exit_c = False
                    break
                else:
                    exit_c = True
            if exit_c:
                path_list.append('')
               
        return path_list

    def input_path(self):
        self.main.lineEdit_filterSDF_inputPath.setText(
            QFileDialog.getExistingDirectory(None))

    def output_path(self):
        self.main.lineEdit_filterSDF_outputPath.setText(
            QFileDialog.getExistingDirectory(None))

    def start(self):

        dir_in = self.main.lineEdit_filterSDF_inputPath.text()
        day_start = self.main.dateEdit_filterSDF_startDate.date()
        day_end = self.main.dateEdit_filterSDF_endDate.date()
        delta = ((day_end.toPyDate() - day_start.toPyDate())).days - \
            int(self.main.spinBox_filterSDF_numDays.text()) + 2

        # составление списка файлов
        path_list = []
        for i in range(((day_end.toPyDate() - day_start.toPyDate())).days + 1):
            temp_date = day_start.addDays(i)
            t = dir_in + '/' + str(temp_date.month()).zfill(2) + '.' + str(temp_date.day()).zfill(
                2) + '.' + str(temp_date.year())[-2:] + '/' + self.main.lineEdit_filterSDF_namePoint.text() + '/'
            if os.path.exists(t):
                for path in pathlib.Path(t).rglob('*.*pos'):
                    path_list.append(str(path))
            else:
                print('Not found: ' + t)
                path_list.append('')

        #path_list = self.temp_path_list()
        
        coord_n_day = []
        if self.main.checkBox_filterSDF_meanDay.isChecked:
            f = open(self.main.lineEdit_filterSDF_outputPath.text() + '/all' + '.sdf', 'w')
            f.write('date dx dy dz n std_dx std_dy std_dz time')
            f.write('\n')
            f.close()


        for j in range(delta):  # цикл ко-ва окон
            timer_start = time.perf_counter()
           
            # цикл добавления данных размером окна
            for i in range(int(self.main.spinBox_filterSDF_numDays.text())):
                print(path_list[i+j])
                if path_list[i+j] == '':
                    coord_n_day.append('')
                    continue
                f = open(path_list[i+j], "r")
                new_coord = []
                for line in f:
                    value_list = line.split(" ")

                    while "" in value_list:
                        value_list.remove("")

                    if value_list[0] != "%" and value_list[0] != "%\n":
                        value_list[len(
                            value_list)-1] = value_list[len(value_list)-1].replace("\n", "")
                        if int(value_list[5]) == 1:
                            temp_list = [
                                value_list[0], 
                                value_list[1],
                                value_list[2], 
                                value_list[3], 
                                value_list[4],
                                value_list[7],
                                value_list[8],
                                value_list[9],
                                ]
                            new_coord.append(temp_list)
                
                work_time = 0
                for q in range(len(new_coord)):
                    temp_time = new_coord[q][1].split(":")
                    temp_seconds = temp_time[2].split(
                        ".")
                    next_time1 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                        temp_seconds[0])

                    if q < len(new_coord) - 1:
                        temp_time = new_coord[q + 1][1].split(":")
                        temp_seconds = temp_time[2].split(
                            ".")
                        next_time2 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                            temp_seconds[0])

                        delta = next_time2 - next_time1
                        if 0 <= delta <= 60:
                                work_time += delta
                    
                      
                if work_time < 2400:
                    coord_n_day.append('')
                else:
                    coord_n_day.append(new_coord)
                day_start = day_start.addDays(1)
            
            
            mean_list = []
            last_index = []
            for w in range(len(coord_n_day)-1):
                last_index.append(0)

            # цикл прохода по эпохам первого дня
            for age_index in range(len(coord_n_day[0])):
                # текущая эпоха первого дня
                age_first = coord_n_day[0][age_index][1]
                date_list = []
                date_list.append(coord_n_day[0][age_index][0])
                date_list.append(coord_n_day[0][age_index][1])
                date_list.append([
                    coord_n_day[0][age_index][2], 
                    coord_n_day[0][age_index][3], 
                    coord_n_day[0][age_index][4],
                    coord_n_day[0][age_index][5],
                    coord_n_day[0][age_index][6],
                    coord_n_day[0][age_index][7]
                    ])

                # цикл поиска эпох в других днях
                for day_index_next in range(len(coord_n_day)-1):

                    if coord_n_day[day_index_next+1] == '':
                        continue

                    age_first_temp = age_first.split(':')
                    age_first_temp[2] = age_first_temp[2].split('.')

                    temp_time = datetime(2010, 10, 10, int(age_first_temp[0]), int(
                        age_first_temp[1]), int(age_first_temp[2][0]))
                    delta_4 = timedelta(minutes=4 * (day_index_next+1))
                    temp_time = temp_time + delta_4

                    age_first_temp = str(temp_time.hour).zfill(2) + ':' + str(temp_time.minute).zfill(
                        2) + ':' + str(temp_time.second).zfill(2) + '.' + age_first_temp[2][1]

                    # цикл поиска эпох в дне
                    for age_next_index in range(last_index[day_index_next], len(coord_n_day[day_index_next+1])):
                        age_next = coord_n_day[day_index_next +
                                               1][age_next_index][1]

                        if age_first_temp == age_next:  # если нашли сразу время, то ура
                            date_list.append([
                                coord_n_day[day_index_next+1][age_next_index][2], 
                                coord_n_day[day_index_next+1][age_next_index][3], 
                                coord_n_day[day_index_next+1][age_next_index][4],
                                coord_n_day[day_index_next+1][age_next_index][5], 
                                coord_n_day[day_index_next+1][age_next_index][6],
                                coord_n_day[day_index_next+1][age_next_index][7]])
                            last_index[day_index_next] = age_next_index
                            break
                        else:                           # иначе ищем близжайшее значение
                            age_first_t = age_first.split(':')
                            age_first_t[2] = age_first_t[2].split('.')
                            temp_time_first = int(
                                age_first_t[0])*3600 + int(age_first_t[1])*60 + int(age_first_t[2][0])

                            try:
                                age_next_temp1 = coord_n_day[day_index_next +
                                                             1][age_next_index+1][1]
                                age_next_temp2 = coord_n_day[day_index_next +
                                                             1][age_next_index-1][1]
                            except Exception:
                                pass
                            else:

                                # заканчивать цикл поиска, если ушли за +4*(day_index_next+1) минуту поиска
                                age_next = age_next.split(':')
                                age_next[2] = age_next[2].split('.')
                                time_5min = int(
                                    age_next[0])*3600 + int(age_next[1])*60 + int(age_next[2][0])
                                del_5min = time_5min - temp_time_first
                                if del_5min > 240 * ((day_index_next+1)) + 60:
                                    break

                                # поиск близжайшего значения с разбросом +-2 секунды
                                age_next_temp1 = age_next_temp1.split(':')
                                age_next_temp1[2] = age_next_temp1[2].split(
                                    '.')
                                temp_time_next1 = int(
                                    age_next_temp1[0])*3600 + int(age_next_temp1[1])*60 + int(age_next_temp1[2][0])

                                age_next_temp2 = age_next_temp2.split(':')
                                age_next_temp2[2] = age_next_temp2[2].split(
                                    '.')
                                temp_time_next2 = int(
                                    age_next_temp2[0])*3600 + int(age_next_temp2[1])*60 + int(age_next_temp2[2][0])

                                del_temp1 = temp_time_next1 - temp_time_first
                                if del_temp1 < 0:
                                    del_temp1 = temp_time_first - temp_time_next1

                                del_temp2 = temp_time_next2 - temp_time_first
                                if del_temp2 < 0:
                                    del_temp2 = temp_time_first - temp_time_next2

                                if del_temp1 < del_temp2:
                                    if 240*(day_index_next+1)-2 < del_temp2 < 240*(day_index_next+1)+2:
                                        date_list.append([
                                            coord_n_day[day_index_next+1][age_next_index-1][2], 
                                            coord_n_day[day_index_next+1][age_next_index-1][3], 
                                            coord_n_day[day_index_next+1][age_next_index-1][4],
                                            coord_n_day[day_index_next+1][age_next_index-1][5],
                                            coord_n_day[day_index_next+1][age_next_index-1][6],
                                            coord_n_day[day_index_next+1][age_next_index-1][7]
                                                         ])
                                        last_index[day_index_next] = age_next_index
                                        break

                                if del_temp2 < del_temp1:
                                    if 240*(day_index_next+1)-2 < del_temp1 < 240*(day_index_next+1)+2:
                                        date_list.append([
                                            coord_n_day[day_index_next+1][age_next_index+1][2], 
                                            coord_n_day[day_index_next+1][age_next_index+1][3], 
                                            coord_n_day[day_index_next+1][age_next_index+1][4],
                                            coord_n_day[day_index_next+1][age_next_index+1][5],
                                            coord_n_day[day_index_next+1][age_next_index+1][6],
                                            coord_n_day[day_index_next+1][age_next_index+1][7]
                                                        ])
                                        last_index[day_index_next] = age_next_index
                                        break

                mean_list.append(date_list)

            # нахождение дельты между координатами исходного дня и координатами sdf 
            if mean_list != []:
                mean_coord_final = []
                for elem in mean_list:
                    if len(elem) == 3:
                        #mean_coord_final.append([elem[0], elem[1], ['0', '0', '0']])
                        continue
                    else:
                        mean_coord = []
                        for coord in range(3):
                            coord_sum = 0
                            mean_std = 0
                            for day_index in range(2, len(elem)):
                                coord_sum += float(elem[day_index][coord])
                                mean_std += float(elem[day_index][coord+3]) ** 2
                            mean_coord.append(
                                str(round(float(elem[2][coord]) - round(coord_sum / (len(elem)-2), 4), 4)))
                            mean_coord.append(str(round((mean_std / (len(elem)-2))**0.5, 4)))

                        mean_coord_final.append([elem[0], elem[1], mean_coord])

                f = open(self.main.lineEdit_filterSDF_outputPath.text()+'/' +
                        os.path.basename(path_list[j]) + '.sdf', 'w')
                for elem in mean_coord_final:
                    f.write(elem[0] + ' ' + elem[1] + ' ' + elem[2][0] + ' ' + elem[2][1] + ' ' + elem[2][2])
                    f.write('\n')
                f.close()
                
                #среднее значение за день
                if self.main.checkBox_filterSDF_meanDay.isChecked:
                    if not mean_coord_final == []:
                        # расчет среднего
                        mean_delta_x = 0.0
                        mean_delta_y = 0.0
                        mean_delta_z = 0.0
                        for elem in mean_coord_final:
                            mean_delta_x += float(elem[2][0])
                            mean_delta_y += float(elem[2][1])
                            mean_delta_z += float(elem[2][2])            
                        mean_delta_x = round(mean_delta_x / len(mean_coord_final), 4)
                        mean_delta_y = round(mean_delta_y / len(mean_coord_final), 4)
                        mean_delta_z = round(mean_delta_z / len(mean_coord_final), 4)

                        #расчет ско
                        std_x_temp = 0.0
                        std_y_temp = 0.0
                        std_z_temp = 0.0
                        for elem in mean_coord_final:
                            std_x_temp += (float(elem[2][0]) - mean_delta_x) ** 2
                            std_y_temp += (float(elem[2][1]) - mean_delta_y) ** 2
                            std_z_temp += (float(elem[2][2]) - mean_delta_z) ** 2     
                        std_x = round(std_x_temp / (len(mean_coord_final)-1), 4)
                        std_y = round(std_y_temp / (len(mean_coord_final)-1), 4)
                        std_z = round(std_z_temp / (len(mean_coord_final)-1), 4)

                        #выбор лучшей эпохи из дня
                        best_age = []
                        min = 0
                        frs = True
                        for elem in mean_coord_final:
                            d = float(elem[2][3]) ** 2 + float(elem[2][4]) ** 2 + float(elem[2][5]) ** 2
                            if frs:
                                best_age = elem
                                min = d
                                frs = False
                            if d < min:
                                best_age = elem
                                min = d
                        
                        #время сеанса по sdf
                        work_time = 0
                        for q in range(len(mean_coord_final)):
                            temp_time = mean_coord_final[q][1].split(":")
                            temp_seconds = temp_time[2].split(
                                ".")
                            next_time1 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                                temp_seconds[0])

                            if q < len(mean_coord_final) - 1:
                                temp_time = mean_coord_final[q + 1][1].split(":")
                                temp_seconds = temp_time[2].split(
                                    ".")
                                next_time2 = int(temp_time[0]) * 3600 + int(temp_time[1]) * 60 + int(
                                    temp_seconds[0])

                                delta = next_time2 - next_time1
                                if 0 <= delta <= 60:
                                    work_time += delta
                                

                        f = open(self.main.lineEdit_filterSDF_outputPath.text() + '/all' + '.sdf', 'a')
                        f_write = elem[0] + ' '
                        f_write += str(best_age[2][0]) + ' '
                        f_write += str(best_age[2][1]) + ' '
                        f_write += str(best_age[2][2]) + ' '
                        f_write += str(len(mean_coord_final)) + ' '
                        f_write += str(std_x) + ' '
                        f_write += str(std_y) + ' '
                        f_write += str(std_z) + ' '
                        f_write += str(timedelta(seconds=work_time))
                        f.write(f_write)
                        f.write('\n')
                        f.close()
            
            
            mean_list = []
            coord_n_day = []
            day_start = day_start.addDays(
                -(int(self.main.spinBox_filterSDF_numDays.text())-1))
            
            timer_end = time.perf_counter()
            print('time iter ' + str(j) + ' is ' + str(timer_end-timer_start))
            
      