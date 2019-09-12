import urllib
from urllib import request
#import socks
#import socket
#import socket
#import argparse
import random
import sys
import re
import requests
import json
from datetime import datetime, date, time

#from PIL import Image
#from operator import itemgetter
#import hashlib
import time

login_status = False

#instaurl
url_insta = 'https://www.instagram.com/'
#instaurl_login
url_login = 'https://www.instagram.com/accounts/login/ajax/'
url_comment = 'https://www.instagram.com/web/comments/%s/add/'
url_tag = 'https://www.instagram.com/explore/tags/%s/?__a=1'
url_likes = 'https://www.instagram.com/web/likes/%s/like/'

stars_accounts = ['annaksyuk']
current_star = 0


ulogin = "LOGIN"
upass = "PASSWORD"
login_form = {
'username': ulogin,
'password': upass
}

s = requests.Session()

def printf(strin):
    print("")
    print(strin)

#УСПЕШНО ЗАХОДИТ!!!
def loginf():
    global s;
    global login_status;

    s.headers.update({
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'User-Agent': "" "",
        'X-Instagram-AJAX': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
    })

    r = s.get(url_insta)

    s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
    time.sleep(5 * random.random())

    #print(r)
    #print(s)

    print(login_form)

    login = s.post(url_login, data=login_form, allow_redirects=True)

    s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    csrftoken = login.cookies['csrftoken']
    #print(r.status_code, r.reason)

    s.cookies['ig_vw'] = '1536'
    s.cookies['ig_pr'] = '1.25'
    s.cookies['ig_vh'] = '772'
    s.cookies['ig_or'] = 'landscape-primary'

    time.sleep(5 * random.random())

    if login.status_code == 200:
        r = s.get('https://www.instagram.com/')
        finder = r.text.find(ulogin)
        login_status = True
        #print(r.text)
        if finder != -1:
            #ui = UserInfo()
            #user_id = ui.get_user_id_by_login(ulogin)
            #login_status = True
            log_string = '%s login success!' % (ulogin)
            print(log_string, login_status)
        else:
            login_status = False
            print('Login error! Check your login data!')
    else:
        print('Login error! Connection error!')


#РАБОТАЕТ!!!! Достает media_id и shortcode первых фоток и видео
#Если retpar == "media_id" (или ==1), или retpar == "shortcode" (или == 0)
def get_media_id_by_instaurl(cur_url_insta, retpar):
    printf("Обработка страницы, извлечение media_id и shorcode параметров!")
    print("go to url:", cur_url_insta)

    global s
    global login_status

    if login_status:

        #element = r'<img src=(.*)'  #модель поиска капчи по "<img src=(любые символы 0+)(пробел)alt"
        #match = re.search(element,sitehtml) #парсим элементы с моделью регулярного выражения element

        try:
            #MEDIA_ID
            r = s.get(cur_url_insta)
            element_media_id = r'"id":"\d{19}"'
            match_media_id = re.findall(element_media_id,r.text)

            #SHORTCODE
            element_shortcode = r'"shortcode":"\w{11}"'
            match_shortcode = re.findall(element_shortcode,r.text)

            if retpar == "media_id" or retpar == 1:
                print("MEDIA_ID")
                print(match_media_id)
                return match_media_id
            elif retpar == "shortcode" or retpar == 0:
                print("SHORTCODE")
                print(match_shortcode)
                return match_shortcode

        except:
            print("Ошибка в получении media_id по @ссылке профиля!")
    else:
        return 0

#РАБОТАЕТ!!!! Достает media_id из хештега
def get_media_id_by_tag(tag):
    """ Get media ID set, by your hashtag """

    global s
    global login_status
    global url_tag

    if login_status:
        log_string = "Гружу изображения по #хештегу: %s" % (tag)
        print(log_string)
        if login_status == 1:
            cur_url_tag = url_tag % (tag)
            try:
                r = s.get(cur_url_tag)
                #print(r.text) #все так же выводит в скриптах!!! значит значения media_id достаются ниже
                all_data = json.loads(r.text)
                #print(all_data)
                media_by_tag = list(all_data['graphql']['hashtag']['edge_hashtag_to_media']['edges'])
                #print("ПОСЛЕ ОБРАБОТКИ ТЕГОВ!!!")
                #print(media_by_tag)
            except:
                media_by_tag = []
                print("Ошибка в получении media_id по #хештегу!")
        else:
            return 0


#РАБОТАЕТ!!! Добавляет коментарий к записи по media_id
def commenting(media_id, comment_text):
    """ Send http request to comment """

    global url_comment
    global comments_counter

    print('Пишу комент...')
    if login_status:
        comment_post = {'comment_text': comment_text}
        #print(url_comment) #url_comment = 'https://www.instagram.com/web/comments/%s/add/'
        cur_url_comment = url_comment % (media_id)
        print(cur_url_comment)
        try:
            comment = s.post(cur_url_comment, data=comment_post)
            print(comment.status_code)
            comments_counter += 1
            """if comment.status_code == 200:
                comments_counter += 1
                log_string = 'Write: "%s". #%s.' % (comment_text, comments_counter)
                print(log_string)"""
        except request.exceptions.RequestException as e:
            print (e)
            print("Ошибка в добавлении коментария")
    return False

#Функция лайкинга по media_id
def liking (foto_media_id):
    global url_likes
    global login_status
    global s
    """ Send http request to like media by ID """
    if login_status:
        #url_likes = 'https://www.instagram.com/web/likes/%s/like/'
        url_like = url_likes % (foto_media_id)
        print(url_like) #https://www.instagram.com/web/likes/1784843649801078818/like/
        try:
            like = s.post(url_like)
            print("Like = ", like)
            #last_liked_media_id = media_id
        except:
            logging.exception("Except on like!")
            #like = 0
        return like

#https://www.instagram.com/p/BiFMtoZB7L6/?taken-by=annaksyuk
#РАБОТАЕТ!!! ДОСТАЕТ Никнеймы людей написавших коментарии к фото!
def get_users_from_foto(foto_url):
    print("Читаем коментарии!")
    global s
    global login_status

    if login_status:
        try:
            r = s.get(foto_url)
            #print(r.text)
            #,"username":"kachenok.live"}
            element_users = r'"username":"([ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_]*)"'
            match_users = re.findall(element_users,r.text)
            print(match_users)
            return match_users

        except:
            print("Пользователи не найдены, либо допущена ошибка!")
    else:
        return 0

#из строки shortcode:blablabla делает ['shortcode',':','blablabla']
def parser2param (strin):
    elements = ['','','']
    cur = 0
    col = 0
    for i in range(len(strin)):
        #print (i, strin[i], cur, col)
        #записывая попались на 2-ю ", перестаем записывать в elements
        if strin[i] == '"' and col == 1:
            cur += 1
            col -= 1
        #записывать когда прошли знак "
        if strin[i] != '"' and col == 1:
            elements[cur] = elements[cur] + strin[i]
        #если нашли первую "
        if strin[i] == '"' and col == 0:
            col += 1
    return elements

#------------------------TODAY COMMENTING USERS------------------------------------#
#подготовка к запоминанию (записыванию) людей которым уже оставили комент
#time
time_in_day = 24 * 60 * 60
comments_per_day = 30
comments_delay = 20
comments_counter = 0

common_delay = 5

#TODAY - работал ли сегодня бот
#проверка дня, делал ли сегодня робот свою работу
f = open("today","r+")
curtime = datetime.today() #текущее время
booltoday = False #работал ли сегодня работо
curtime = str(curtime.day) + " " + str(curtime.month) + " " + str(curtime.year) + "\n"
todayuser = []

#читаем файл, в котором в первой строке записана дата, а потом пользователи кому уже написали
checkcurtime = f.readline() #читаем первую строчку и првоеряем работали ли сегодня

#проверяет запускали ли мы скрипт больше одного раза
#или же, сегодня другой день и пора вести список с начала
if curtime == checkcurtime:
    booltoday = True
else:
    f.close()
    open('today', 'w').close()
    f = open("today","r+")
    f.write(curtime)


#------------------------TODAY COMMENTING USERS------------------------------------#

#проверяет если данный юзер в списке уже прокоментированных
def checkuser (cur_user):
    global todayusers
    for i in range (0,len(todayusers)):
        if todayusers[i] == cur_user + "\n" or todayusers[i] == cur_user:
            return False
    return True

#----------------------COMMENTS_SHABLON--------------------------#
all_comments = ["Привет, отличное фото! Заходи к нам"]


def time_delay():
    global common_delay
    time.sleep(common_delay+random.randint(1,5))

#функция модов работы бота
def timing_mode(smode):
    #with open('data.txt', 'r') as myfile:
        #data=myfile.read().replace('\n', '')

    print("Timming mode")

    global f
    global todayusers
    global comments_counter
    global stars_accounts
    global url_insta
    global current_star
    url_star = url_insta
    url_star = url_star + stars_accounts[current_star]
    print(url_star)

    todayusers = f.readlines()

    print(todayusers)

    #https://www.instagram.com/p/BiFzdPyBJdh/?taken-by=annaksyuk
    #smode == 0, 30 коментариев.
    f.close()

    if smode == 0:
        #ТАЙМИНГ
        #-------------------
        time_delay()
        #входим
        loginf()

        cur_img = 0
        #сначала мне нужно получить ссылки на фотки,
        #и потом в одной из них списать всех кто писал коменты под фото
        #ТАЙМИНГ
        #-------------------
        time_delay()
        shortcode = get_media_id_by_instaurl(url_star,'shortcode')

        #media_id = get_media_id_by_instaurl(url_star,'media_id')
        rshot = parser2param(shortcode[0]) #rshot = results of shortcode, разбив на два параметра
        url_foto = "%sp/%s/?taken-by=%s" % (url_insta, rshot[2],stars_accounts[current_star])
        print(url_foto)

        #ТАЙМИНГ
        #-------------------
        time_delay()
        users = get_users_from_foto(url_foto)

        print (users)


        for i in range(1,len(users)-1): #примерно 30-50 прочитает за раз
            #print(users[i])
            #открываем и закрываем для того что бы записывать в случае прерывания алгоритма
            f = open("today","r+")

            if comments_counter == 40:
                break
            url_user = "%s%s" % (url_insta, users[i])
            printf("Берем media_id из полученных ссылок пользователей")

            try:
                print(users[i])
                if checkuser(users[i]):
                    #-------------------
                    time_delay()
                    usermedia_id = get_media_id_by_instaurl(url_user,'media_id')

                    print("Добавляем коментарий в первую фотку пользователя")

                    actionsmedia_id = parser2param(usermedia_id[0])
                    print(actionsmedia_id) #['id', ':', '1787931110044816588']
                    #ТАЙМИНГ
                    #-------------------
                    time_delay()
                    commenting(actionsmedia_id[2],'Nice photo!!!') #оставляем коментариий
                    #-------------------
                    #time_delay()
                    print("Ставим лайк")
                    #-------------------
                    time_delay()
                    print("liking", actionsmedia_id[2])
                    liking(actionsmedia_id[2])

                    #если пользователя не было, мы сделаем все действия и добавим его в список
                    todayusers.append(users[i])
                    f.write(users[i])
                    f.write('\n')

                    print("-----------todayusers---------")
                    print(todayusers)
                    f.close()
                else:
                    print ("Этому пользователю уже оставляли лайк и коментарий")
                    f.close()

            except:
                print("Ошибка в добавлении обработке событий")
            #print(url_user)


#loginf() #входим в акк
#print(login_status)    #проверка логин статуса

#get_media_id_by_instaurl('https://www.instagram.com/annaksyuk/','media_id')
#get_media_id_by_tag('thankgodandmyniggas')
#comment('1767044738994968417','Eee');  #тестирование коментария на фотку
#get_users_from_foto('https://www.instagram.com/p/BiFMtoZB7L6/?taken-by=annaksyuk')
#get_users_from_foto('https://www.instagram.com/p/BiD8ETYBtpR/?taken-by=annaksyuk')
timing_mode(0)
f.close()
#exit()
