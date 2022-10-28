import requests
from bs4 import BeautifulSoup
import os
import re
import json
import random
import time

def LoadUserAgents(uafile):#从user_agents.txt文件里面随机选择一个user_agent,防封
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas
uas = LoadUserAgents("user_agents.txt")

def htmlparser(url):#解析网页的函数
    ua = random.choice(uas)
    user_agent = ua
    headers = {'User-agent': user_agent,
               'Referer': 'https://car.autohome.com.cn.html',}#加上header伪装成浏览器防止被封
    r = requests.get(url, headers=headers)#get请求
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    content = r.text
    return content


def koubei(car_list):
    for i in car_list:
        url = 'https://k.autohome.com.cn/' + str(i)
        print(url)
        content = htmlparser(url)
        # print(content)
        soup = BeautifulSoup(content, "html.parser")
        car_koubei_soup = soup.find("ul", class_="score_tag__Wq2Z4")
        car_koubei_test = car_koubei_soup.get_text()
        if car_koubei_test != '':
            car_koubei_test = car_koubei_test.replace('\xa0','')
            car_koubei = []
            for j in car_koubei_test:
                car_koubei.append(j)
            car_koubei[0] = '{"'+car_koubei[0]
            car_koubei[-1] = car_koubei[-1]+'"}'
            for j in range(1,len(car_koubei)-1):
                if is_Chinese(car_koubei[j]):
                    if not is_Chinese(car_koubei[j+1]):
                        car_koubei[j] = car_koubei[j]+'":'
                        car_koubei[j+1] = '"'+car_koubei[j+1]
            for j in range(1,len(car_koubei)-1):
                if not is_Chinese(car_koubei[j]):
                    if is_Chinese(car_koubei[j+1]):
                        car_koubei[j] = car_koubei[j]+'",'
                        car_koubei[j+1] = '"'+car_koubei[j+1]
            car_koubei = ''.join(car_koubei)
            car_koubei = eval(car_koubei)
        else:
            car_koubei = '暂无口碑数据'
        print(car_koubei)


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

koubei([4196,4199])