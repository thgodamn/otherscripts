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

stars_accounts = ['oiiikrisiiio']
current_star = 0


ulogin = "LOGIN"
upass = "PASSWORD"
login_form = {
'username': ulogin,
'password': upass
}

s = requests.Session()

common_delay = 5

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

def time_delay(add_delay = 0):
    global common_delay
    time.sleep(common_delay+random.randint(1,5)+add_delay)

def follow_read (check_account):
    global s
    global login_status

    if login_status:
        try:
            print(check_account)
            r = s.get(check_account)
            #time_delay(-5)
            #print (r.text)

            time_delay()
            all_data = json.loads(re.search('{"activity.+show_app', r.text, re.DOTALL).group(0)+'":""}')['entry_data']['ProfilePage'][0]
            user_info = all_data['graphql']['user']

            #print(user_info)

            follows = user_info['edge_follow']['count']
            follower = user_info['edge_followed_by']['count']

            print("------------------follows---------------------")
            print(follows)

            print("------------------follower---------------------")
            print(follower)

        except:
            print ("Ошибка в прочтении фолловеров данного аккаунта")

loginf()
follow_read('https://www.instagram.com/thankgodandmyniggas/following/')
