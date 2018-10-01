import csv
import os
import re
import datetime
import pandas as pd
#from collections import OrderedDict
#import xlsxwriter
#import openpyxl

#from sqlalchemy import create_engine

solve_begin = {} #хранится сумма всех пассажиров начинающих с одной и той же зоны
solve_end = {} #хранится сумма всех пассажиров заканчивающих в определенной зоне
district = {} #креспонденция районов и зон
matrix = {} #матрица районов

path_chaspik = 'chaspik.csv'
path_district = 'district.csv'

count_days = 0
current_day = ""
count = 0

"""def dict_toarray(dict):
    arr = []
    #print(dict)
    for i in dict:
        print(i)
        arr.append(dict[i])
    return arr"""

def parsetime(time):
    regular = r'\d{1,4}'
    match = re.findall(regular,time)
    return match

#работает с данными из parsetime()
def datein_minutes(time):
    minutes = int(time[2])*12*30*24*60 + int(time[1])*30*24*60 + int(time[0])*24*60 + int(time[3])*60 + int(time[4])
    return minutes

def parse_timehours(time):
    regular = r'\d\d:\d\d'
    match = re.findall(regular,time)
    return match[0]

def parsedate(time):
    regular = r'\d\d\d\d.\d\d.\d\d'
    match = re.match(regular,time)
    return match[0]

def csv_writer_zone(zone, data, path):
    global count_days
    with open(path, 'a') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n', delimiter=';')
        #header = ["Зона", "Время(наземный транспорт)", "Кол-во(наземный транспорт)", "Время(метро)", "Кол-во(метро)"]
        #writer.writerow(header)
        arr = [zone, data['time_S1'], data['cnt'], data['time_S2'], data['cnt_metro'],data['cnt']/count_days,data['cnt_metro']/count_days]
        writer.writerow(arr)

def csv_writer(data, path):
    with open(path, 'a') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n', delimiter=';')
        writer.writerow(data)

#csv_writer_district(finish,time,start,matrix[finish][time][start])
def csv_writer_district(finish, time, start, data, path):
    with open(path, 'a') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n', delimiter=';')
        #time,start,finish,cnt,cnt_metro
        arr = [time, start, finish, data['cnt'], data['cnt_metro']]
        writer.writerow(arr)

def main():
    with open('Zones.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
        cnt = 0
        for row in csv_reader:
            if cnt > 0:
                a = (', '.join(row)).split(";")
                district[a[0]] = a[1]
            cnt += 1
        #print(district)

    chunksize = 10 ** 6
    global count
    global matrix
    global count_days
    global current_day

    #arrout = {'time':[],
            #'start_district':[],
            #'finish_district':[],
            #'custromers_count':[],
            #'custromers_count_metro':[],}
    #arrout = []
    cur_day = ""

    for chunk in pd.read_csv('Matrix.csv', chunksize=chunksize):
        for row in chunk:
            for i in chunk[row]:
                param = i.split(";")
                #param[0] = ts, param[1] = departure_zid, param[2] = arrival_zid, param[3] = cust_cnt, param[4] = cust_metro
                time = param[0]
                start = param[1]
                finish = param[2]
                cnt = int(param[3])
                cnt_metro = int(param[4])

                #print(param)
                #if count == 100000:
                    #return
                if count % 1000000 == 0:
                    print(count, " ", datetime.datetime.now())
                    #if count/3500000 == 1:
                        #return
                if current_day != parsedate(time):
                    count_days += 1
                    current_day = parsedate(time)

                #создаем матрицу креспонденций между районами города
                if cur_day == "":
                    cur_day = parsedate(time)
                elif cur_day != parsedate(time):
                    cur_day = parsedate(time)
                    matrix = {}

                if finish in district and start in district and not district[finish] in matrix and cnt + cnt_metro > 0:
                    matrix[district[finish]] = matrix.get(district[finish], {})
                    matrix[district[finish]][time] = matrix[district[finish]].get(time, {})
                    matrix[district[finish]][time][district[start]] = {'cnt':cnt,'cnt_metro':cnt_metro}
                elif finish in district and start in district and district[finish] in matrix and time not in matrix[district[finish]] and cnt + cnt_metro > 0:
                    matrix[district[finish]][time] = matrix[district[finish]].get(time, {})
                    matrix[district[finish]][time][district[start]] = {'cnt':cnt,'cnt_metro':cnt_metro}
                elif finish in district and start in district and district[finish] in matrix and time in matrix[district[finish]] and start not in matrix[district[finish]][time] and cnt + cnt_metro > 0:
                    #matrix[district[finish]][time] = matrix[district[finish]].get(time, {})
                    matrix[district[finish]][time][district[start]] = {'cnt':cnt,'cnt_metro':cnt_metro}
                elif finish in district and start in district and district[finish] in matrix and time in matrix[district[finish]] and start in matrix[district[finish]][time] and cnt + cnt_metro > 0:
                    matrix[district[finish]][time][start]['cnt'] += cnt
                    matrix[district[finish]][time][start]['cnt_metro'] += cnt_metro


                #Расчитываем перемещения пассажиров по городу относительно зон
                if count > 0:
                    if finish not in solve_end:
                        solve_end[finish] = solve_end.get(finish,{})
                        solve_end[finish][time] = [int(cnt),int(cnt_metro)]
                    elif time in solve_end[finish]:
                        solve_end[finish][time][0] += int(cnt)
                        solve_end[finish][time][1] += int(cnt_metro)
                    else:
                        solve_end[finish][time] = [int(cnt),int(cnt_metro)]
                    if start not in solve_begin:
                        solve_begin[start] = solve_begin.get(start,{})
                        solve_begin[start][time] = [int(cnt),int(cnt_metro)]
                    elif time in solve_begin[start]:
                        solve_begin[start][time][0] += int(cnt)
                        solve_begin[start][time][1] += int(cnt_metro)
                    else:
                        solve_begin[start][time] = [int(cnt),int(cnt_metro)]

                #os.system("pause")
                #print(count)
                count += 1

def chaspik():
    global count
    global count_days
    global path_chaspik
    global path_district
    count = 0
    piktime_endzones = {} # содержит 1-зону(ключ), 2-время (00:00), 3- и кол-во пассажиров на наземном и метро,
                                        #за все дни, которые прошли в этой зоне за текущее время
    chaspik_zone = {} # содержит зону(ключ) и ее часпик наземного транспорта, а так же часпик на метро
    chaspik_city = {} # содержит время(ключ) 2-кол-во на наземном, 3- кол-во на метро
    timeof_chaspik_city = {'cnt':0, 'time_S1':"", 'cnt_metro':0, 'time_S2':""}

    #print("----------------------------------------------------")
    print("-------------------piktime_endzones----------------------")
    #print("----------------------------------------------------")

    for zone in solve_end:
        if not zone in piktime_endzones:
            piktime_endzones[zone] = piktime_endzones.get(zone,{})
        for time in solve_end[zone]:
            if not time in piktime_endzones[zone]:
                piktime_endzones[zone][parse_timehours(time)] = {'cnt':0, 'cnt_metro':0}
            #если 1 элемент, просто запоминаем его и начинаем подсчет со второго
            piktime_endzones[zone][parse_timehours(time)]['cnt'] += solve_end[zone][time][0]
            piktime_endzones[zone][parse_timehours(time)]['cnt_metro'] += solve_end[zone][time][1]

    #выведем для зоны часпик наземного и подзменого транспорта (подсчитав за все дни)
    for zone in piktime_endzones: #piktime_endzones[zone][parse_timehours(time)]
        for time in piktime_endzones[zone]:
            #подсчет часпика для всего города
            if not time in chaspik_city:
                chaspik_city[time] = {'cnt':0,'cnt_metro':0}
            chaspik_city[time]['cnt'] += piktime_endzones[zone][time]['cnt']
            chaspik_city[time]['cnt_metro'] += piktime_endzones[zone][time]['cnt_metro']
            #подсчет часпика для каждой зоны
            if not zone in chaspik_zone:
                chaspik_zone[zone] = {'cnt':0, 'time_S1':"", 'cnt_metro':0, 'time_S2':""}
            if chaspik_zone[zone]['cnt'] < piktime_endzones[zone][time]['cnt']:
                chaspik_zone[zone]['cnt'] = piktime_endzones[zone][time]['cnt']
                chaspik_zone[zone]['time_S1'] = time
            if chaspik_zone[zone]['cnt_metro'] < piktime_endzones[zone][time]['cnt_metro']:
                chaspik_zone[zone]['cnt_metro'] = piktime_endzones[zone][time]['cnt_metro']
                chaspik_zone[zone]['time_S2'] = time

    for time in chaspik_city:
        if timeof_chaspik_city['cnt'] < chaspik_city[time]['cnt']:
            timeof_chaspik_city['cnt'] = chaspik_city[time]['cnt']
            timeof_chaspik_city['time_S1'] = time
        if timeof_chaspik_city['cnt_metro'] < chaspik_city[time]['cnt_metro']:
            timeof_chaspik_city['cnt_metro'] = chaspik_city[time]['cnt_metro']
            timeof_chaspik_city['time_S2'] = time

    header = ["Часпик города(наземный транспорт)","Кол-во людей(наземный транспорт)","Часпик города(метро)","Кол-во людей(метро)","Среднее кол-во людей(наземный [Общее кол-во/Кол-во дней])","Среднее кол-во людей(метро [Общее кол-во/Кол-во дней])","Кол-во дней"]
    arrout = [timeof_chaspik_city['time_S1'],timeof_chaspik_city['cnt'],timeof_chaspik_city['time_S2'],timeof_chaspik_city['cnt_metro'],timeof_chaspik_city['cnt']/count_days,timeof_chaspik_city['cnt_metro']/count_days,count_days]
    csv_writer(header,path_chaspik)
    csv_writer(arrout,path_chaspik)
    header = ["Зона", "Часпик передвижения в указанную зону(наземный транспорт)", "Кол-во перемещавшихся людей за все дни в данную зону(наземный транспорт)", "Часпик передвижения людей в указанную зону(метро)", "Кол-во перемещавшихся людей за все дни в данную зону(метро)", "Среднее знач. наземный транспорт (Кол-во людей за все дни/Кол-во дней)","Среднее знач метро (Кол-во людей за все дни/Кол-во дней)"]
    csv_writer(header,path_chaspik)
    for zone in chaspik_zone:
            csv_writer_zone(zone, chaspik_zone[zone],path_chaspik)

    #print(datetime.datetime.now())

    arrout = {"time":[],
            "start_district":[],
            "finish_district":[],
            "custromers_count":[],
            "custromers_count_metro":[]}

    #output district
    for finish in matrix:
        for time in matrix[finish]:
            for start in matrix[finish][time]:
                count += 1

                #txt = '%s,%s,%s,%s,%s\n' % (time,start,finish,matrix[finish][time][start]['cnt'],matrix[finish][time][start]['cnt_metro'])
                #print(txt)
                #with open(path_district, 'ab') as csv_file:
                    #csv_file.write(txt)
                #arrout.append({'time':time, 'start_district':start, 'finish_district':finish, 'custromers_count': matrix[finish][time][start]['cnt'], 'custromers_count_metro':matrix[finish][time][start]['cnt']})

                arrout["time"].append(time)
                arrout["start_district"].append(start)
                arrout["finish_district"].append(finish)
                arrout["custromers_count"].append(matrix[finish][time][start]['cnt'])
                arrout["custromers_count_metro"].append(matrix[finish][time][start]['cnt_metro'])

                #arrout.append({'time':time,'start_district':start,'finish_district':finish,'custromers_count':matrix[finish][time][start]['cnt'],'custromers_count_metro':matrix[finish][time][start]['cnt_metro']})

                if count > 0 and count % 10000 == 0:
                    df = pd.DataFrame(data=arrout, columns=["time","start_district","finish_district","custromers_count","custromers_count_metro"])
                    arrout = {"time":[],
                            "start_district":[],
                            "finish_district":[],
                            "custromers_count":[],
                            "custromers_count_metro":[]}
                    df.to_csv(path_district, line_terminator='\n', mode='a', index=False, quoting=csv.QUOTE_NONE, sep=';')

#start program
with open(path_chaspik, 'w') as csv_file:
    print("clear true")
with open(path_district, 'w') as csv_file:
    print("clear true")

print(datetime.datetime.now())
main()
chaspik()
print(datetime.datetime.now())
#print(datein_minutes(parsetime("01.08.2014  0:00:00")))
#print(datein_minutes(parsetime("01.08.2014  7:30:00")))
