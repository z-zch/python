#coding==utf-8
import requests
from bs4 import BeautifulSoup
import os
import re
import json
import random
import time

def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

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

# 获取经销商价格
def deliver_current_change(content):
    # print('调用了该函数')
    # print('content:',content)
    con = re.sub(r"LoadDealerPrice", "", str(content)) # 删除LoadDealerPrice
    # print('con:',con)
    con2 = con[1:-1] # 删除空格
    # print('con2:',con2)
    last = json.loads(con2) #转换成字典格式
    # print('last:',last)
    deliver_key = {}
    # 从中取出经销商价格
    for i in last['body']['item']:
        deliver_key[i["SpecId"]] = i["Price"]
    # print('deliver:',deliver_key)
    return deliver_key

# 获得经销商价格
def deliver_future_change(content):
    con = re.sub(r"LoadDealerPrice", "", str(content))
    con2 = con[1:-1]
    last = json.loads(con2)
    deliver_key = {}
    for i in last['body']['item']:
        deliver_key[i["SpecId"]] = i["Price"]
    # print(deliver_key)
    return deliver_key

def get_car_list(url):#得到车型的sid list
    content = htmlparser(url)
    soup = BeautifulSoup(content,"html.parser")
    car_list_soup = soup.find_all("div",class_= "list-cont")
    car_list = []
    for i in car_list_soup:
        car_id = i["data-value"]
        car_list.append(car_id)
    return car_list


car_total_name = " "

def current_spider(url):
    content = htmlparser(url)
    soup = BeautifulSoup(content, "html.parser")
    car_list = get_car_list(url)
    car_name2 = soup.find("h2",class_="fn-left cartab-title-name").get_text()
    # print('car_name2:',car_name2)
    # time.sleep(5)
    # print('url: ',url,'car_list:',car_list)
    for i in car_list:
        # 得到经销商报价
        headers = {'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': '__ah_uuid=C8A42CEE-5EF9-4CC8-9CE4-C03C70836956; fvlid=1539747194063t5CR8avRSl; sessionid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; ahpau=1; sessionuid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; Hm_lvt_9924a05a5a75caf05dbbfb51af638b07=1539747237; wwwjbtab=0%2C1; platformCityId=110100; jrsfvi=1539748349859eIR2ZhIQ2ij5%7Ccar.autohome.com.cn%7C2020994; jrslvi=2020994%7Ccar.autohome.com.cn%7C1539748349859eIR2ZhIQ2ij5; jpvareaid=2020994; nice_ida44a9a90-84e5-11e8-b395-81b8eb2a7c21=117f6dd2-d1c0-11e8-bb49-714fbbfd1285; cnversion=DhEYsPcmPRYbRzJlYmbtTSMsJyBr0d199UqHEkl91mdRAINtJaIKjChtSbYkI/Bn+M7EvJ8fRNwi4yKfYlGqGyQN8gaX92lRCcjTnjNfF5q6TuzfMgnpHA==; ahsids=692_588_4764_3201_237; sessionip=202.113.176.131; area=120112; ahpvno=72; Hm_lpvt_9924a05a5a75caf05dbbfb51af638b07=1539788829; sessionvid=F86D2D0A-780C-44C7-9975-55F132EB4942; ref=www.google.com.hk%7C0%7C0%7C0%7C2018-10-17+23%3A07%3A14.347%7C2018-10-17+11%3A33%3A14.782; ahrlid=15397888292466xBEHqnzRj-1539788837406',
                   'Host': 'carif.api.autohome.com.cn',
                   'Referer': 'https://car.autohome.com.cn/price/brand-33.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  # 加上header伪装成浏览器防止被封
        # 下面URL里面存了经销商报价，从网页请求中拿到
        deliver_url = "https://carif.api.autohome.com.cn/dealer/LoadDealerPrice.ashx?_callback=LoadDealerPrice&type=1&seriesid=" + i + "&city=120100"
        # print('deliver_url:',deliver_url)
        deliver_soup = requests.get(deliver_url, headers=headers)
        # 如果访问异常 raise_for_status就可以抛出异常
        deliver_soup.raise_for_status()
        # apparent_encoding防止乱码
        deliver_soup.encoding = deliver_soup.apparent_encoding
        # deliver文本内容
        deliver = deliver_soup.text
        # print('deliver: ',deliver)
        deliver_key = deliver_current_change(deliver)
        # print('deliver_key:',deliver_key)

        # 采集车的总型号
        car = soup.find("div", class_="list-cont", attrs={"data-value": i})
        car_name = car.find("div", class_="list-cont-main")
        car_name_only = car_name.find("div", class_="main-title").get_text()
        # print('car_name:',car_name)
        # print('car_name_only:',car_name_only)

        # 采集口碑信息
        url_koubei = 'https://k.autohome.com.cn/' + str(i)
        # print(url_koubei)
        content_koubei = htmlparser(url_koubei)
        soup_koubei = BeautifulSoup(content_koubei, "html.parser")
        car_koubei_soup = soup_koubei.find("ul", class_="score_tag__Wq2Z4")
        car_koubei_test = car_koubei_soup.get_text()
        # 将采集到的口碑信息转换成字典格式
        if car_koubei_test != '':
            car_koubei_test = car_koubei_test.replace('\xa0', '')
            car_koubei = []
            for j in car_koubei_test:
                car_koubei.append(j)
            car_koubei[0] = '{"' + car_koubei[0]
            car_koubei[-1] = car_koubei[-1] + '"}'
            for j in range(1, len(car_koubei) - 1):
                if is_Chinese(car_koubei[j]):
                    if not is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '":'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            for j in range(1, len(car_koubei) - 1):
                if not is_Chinese(car_koubei[j]):
                    if is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '",'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            car_koubei = ''.join(car_koubei)
            # car_koubei = eval(car_koubei)
        else:
            car_koubei = '暂无口碑数据' #没有口碑数据则输出暂无口碑数据
        print(car_koubei)

        # 下面采集车的具体型号信息
        car_model = soup.find("div", class_="intervalcont fn-hide", attrs={"id": "divSpecList" + i})
        for k in car_model.find_all("div", class_="interval01"):
            car_model_size = k.find("div", class_="interval01-title title-cont")  # 6.0升 517马力的父节点
            car_model_size_only = car_model_size.find("div", class_="interval01-list-cars").get_text()  # 6.0升 517马力
            print(car_model_size_only)
            car_model_size_value = k.find_all("ul", class_="interval01-list")  # 该属性的下属分类（具体类型）
            for g in car_model_size_value:
                for li in g.find_all("li"):
                    flag = False
                    for ke in deliver_key.keys():
                        key = ke
                        key = str(key)
                        if key == li["data-value"]:
                            flag = True
                            # 拼接写入data.txt
                            # print('car_model_size_only',car_model_size_only)
                            # print('str(deliver_key[ke])',str(deliver_key[ke]))
                            # print('li.find("div", class_="interval01-list-cars-infor").get_text()',li.find("div", class_="interval01-list-cars-infor").get_text())
                            # print('li.find("div", class_="interval01-list-guidance").get_text()',li.find("div", class_="interval01-list-guidance").get_text())
                            with open("data.txt", 'a', encoding="utf-8") as f:
                                f.write(
                                    car_total_name + "*" + car_name2 + "*" + car_name_only + "*在售*" + car_model_size_only + "*" +
                                    str(deliver_key[ke]) + "*" +
                                    li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                    li.find("div", class_="interval01-list-guidance").get_text() + "*"+ car_koubei
                                )
                            with open("data.txt","a",encoding="utf-8") as f:
                                f.write("\n")
                                print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ",
                                      str(deliver_key[ke]), " ", li.get_text()+ car_koubei)
                            break
                        else:
                            pass
                    if flag == False:
                        with open("data.txt", 'a', encoding="utf-8") as f:
                            f.write(
                                car_total_name + "*" + car_name2 + "*" + car_name_only + "*在售*" + car_model_size_only + "*" +
                                "暂无报价*" +
                                li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                li.find("div", class_="interval01-list-guidance").get_text() + "*"+ car_koubei
                            )
                        with open("data.txt", "a", encoding="utf-8") as f:
                            f.write("\n")
                        print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ", "暂无报价", " ",
                                      li.get_text()+ car_koubei)
                    else:
                        pass
    time.sleep(1)

def future_spider(url):
    content = htmlparser(url)
    soup = BeautifulSoup(content, "html.parser")
    car_list = get_car_list(url)
    car_name2 = soup.find("h2",class_="fn-left cartab-title-name").get_text()
    for i in car_list:
        # 得到经销商报价
        headers = {'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': '__ah_uuid=C8A42CEE-5EF9-4CC8-9CE4-C03C70836956; fvlid=1539747194063t5CR8avRSl; sessionid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; ahpau=1; sessionuid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; Hm_lvt_9924a05a5a75caf05dbbfb51af638b07=1539747237; wwwjbtab=0%2C1; platformCityId=110100; jrsfvi=1539748349859eIR2ZhIQ2ij5%7Ccar.autohome.com.cn%7C2020994; jrslvi=2020994%7Ccar.autohome.com.cn%7C1539748349859eIR2ZhIQ2ij5; jpvareaid=2020994; nice_ida44a9a90-84e5-11e8-b395-81b8eb2a7c21=117f6dd2-d1c0-11e8-bb49-714fbbfd1285; cnversion=DhEYsPcmPRYbRzJlYmbtTSMsJyBr0d199UqHEkl91mdRAINtJaIKjChtSbYkI/Bn+M7EvJ8fRNwi4yKfYlGqGyQN8gaX92lRCcjTnjNfF5q6TuzfMgnpHA==; ahsids=692_588_4764_3201_237; sessionip=202.113.176.131; area=120112; ahpvno=72; Hm_lpvt_9924a05a5a75caf05dbbfb51af638b07=1539788829; sessionvid=F86D2D0A-780C-44C7-9975-55F132EB4942; ref=www.google.com.hk%7C0%7C0%7C0%7C2018-10-17+23%3A07%3A14.347%7C2018-10-17+11%3A33%3A14.782; ahrlid=15397888292466xBEHqnzRj-1539788837406',
                   'Host': 'carif.api.autohome.com.cn',
                   'Referer': 'https://car.autohome.com.cn/price/brand-33.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  # 加上header伪装成浏览器防止被封
        deliver_url = "https://carif.api.autohome.com.cn/dealer/LoadDealerPrice.ashx?_callback=LoadDealerPrice&type=1&seriesid=" + i + "&city=0"
        deliver_soup = requests.get(deliver_url, headers=headers)
        deliver_soup.raise_for_status()
        deliver_soup.encoding = deliver_soup.apparent_encoding
        deliver = deliver_soup.text
        deliver_key = deliver_current_change(deliver)
        # print(deliver_key)

        # 采集车的总型号
        car = soup.find("div", class_="list-cont", attrs={"data-value": i})
        car_name = car.find("div", class_="list-cont-main")
        car_name_only = car_name.find("div", class_="main-title").get_text()
        # print(car_name_only)

        # 采集口碑信息
        url_koubei = 'https://k.autohome.com.cn/' + str(i)
        print(url_koubei)
        content_koubei = htmlparser(url_koubei)
        soup_koubei = BeautifulSoup(content_koubei, "html.parser")
        car_koubei_soup = soup_koubei.find("ul", class_="score_tag__Wq2Z4")
        car_koubei_test = car_koubei_soup.get_text()
        if car_koubei_test != '':
            car_koubei_test = car_koubei_test.replace('\xa0', '')
            car_koubei = []
            for j in car_koubei_test:
                car_koubei.append(j)
            car_koubei[0] = '{"' + car_koubei[0]
            car_koubei[-1] = car_koubei[-1] + '"}'
            for j in range(1, len(car_koubei) - 1):
                if is_Chinese(car_koubei[j]):
                    if not is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '":'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            for j in range(1, len(car_koubei) - 1):
                if not is_Chinese(car_koubei[j]):
                    if is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '",'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            car_koubei = ''.join(car_koubei)
            # car_koubei = eval(car_koubei)
        else:
            car_koubei = '暂无口碑数据'
        print(car_koubei)

        # 下面采集车的具体型号信息
        car_model = soup.find("div", class_="intervalcont fn-hide", attrs={"id": "divSpecList" + i})
        for k in car_model.find_all("div", class_="interval01"):
            car_model_size = k.find("div", class_="interval01-title title-cont")  # 6.0升 517马力的父节点
            car_model_size_only = car_model_size.find("div", class_="interval01-list-cars").get_text()  # 6.0升 517马力
            print(car_model_size_only)
            car_model_size_value = k.find_all("ul", class_="interval01-list")  # 该属性的下属分类（具体类型）
            for g in car_model_size_value:
                for li in g.find_all("li"):
                    flag = False
                    for ke in deliver_key.keys():
                        key = ke
                        key = str(key)
                        if key == li["data-value"]:
                            flag = True
                            with open("data.txt", 'a', encoding="utf-8") as f:
                                f.write(
                                    car_total_name + "*" + car_name2 + "*" + car_name_only + "*即将销售*" + car_model_size_only + "*" +
                                    str(deliver_key[ke]) + "*" +
                                    li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                    li.find("div", class_="interval01-list-guidance").get_text() + "*"+ car_koubei)
                            with open("data.txt","a",encoding="utf-8") as f:
                                f.write("\n")
                            print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ",
                                      str(deliver_key[ke]), " ", li.get_text()+ car_koubei)
                            break
                        else:
                            pass
                    if flag == False:
                        with open("data.txt", 'a', encoding="utf-8") as f:
                            f.write(
                                car_total_name + "*" + car_name2 + "*" + car_name_only + "*即将销售*" + car_model_size_only + "*" +
                               "暂无报价*" +
                                li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                li.find("div", class_="interval01-list-guidance").get_text() + "*" + car_koubei)
                        with open("data.txt", "a", encoding="utf-8") as f:
                            f.write("\n")
                        print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ", "暂无报价", " ",
                                      li.get_text()+ car_koubei)
                    else:
                        pass
    time.sleep(1)
def stop_spider(url):
    content = htmlparser(url)
    soup = BeautifulSoup(content, "html.parser")
    car_list = get_car_list(url)
    car_name2 = soup.find("h2",class_="fn-left cartab-title-name").get_text()
    for i in car_list:
        # 得到经销商报价
        headers = {'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Connection': 'keep-alive',
                   'Cookie': '__ah_uuid=C8A42CEE-5EF9-4CC8-9CE4-C03C70836956; fvlid=1539747194063t5CR8avRSl; sessionid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; ahpau=1; sessionuid=BD2C0F87-2785-46BC-B6B4-26659E736FF6%7C%7C2018-10-17+11%3A33%3A14.782%7C%7Cwww.google.com.hk; Hm_lvt_9924a05a5a75caf05dbbfb51af638b07=1539747237; wwwjbtab=0%2C1; platformCityId=110100; jrsfvi=1539748349859eIR2ZhIQ2ij5%7Ccar.autohome.com.cn%7C2020994; jrslvi=2020994%7Ccar.autohome.com.cn%7C1539748349859eIR2ZhIQ2ij5; jpvareaid=2020994; nice_ida44a9a90-84e5-11e8-b395-81b8eb2a7c21=117f6dd2-d1c0-11e8-bb49-714fbbfd1285; cnversion=DhEYsPcmPRYbRzJlYmbtTSMsJyBr0d199UqHEkl91mdRAINtJaIKjChtSbYkI/Bn+M7EvJ8fRNwi4yKfYlGqGyQN8gaX92lRCcjTnjNfF5q6TuzfMgnpHA==; ahsids=692_588_4764_3201_237; sessionip=202.113.176.131; area=120112; ahpvno=72; Hm_lpvt_9924a05a5a75caf05dbbfb51af638b07=1539788829; sessionvid=F86D2D0A-780C-44C7-9975-55F132EB4942; ref=www.google.com.hk%7C0%7C0%7C0%7C2018-10-17+23%3A07%3A14.347%7C2018-10-17+11%3A33%3A14.782; ahrlid=15397888292466xBEHqnzRj-1539788837406',
                   'Host': 'carif.api.autohome.com.cn',
                   'Referer': 'https://car.autohome.com.cn/price/brand-33.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}  # 加上header伪装成浏览器防止被封
        deliver_url = "https://carif.api.autohome.com.cn/che168/LoadUsedCarPrice.ashx?_callback=LoadUsedCarPriceGetUsedCarData&pid=120000&seriesid=" + i
        deliver_soup = requests.get(deliver_url, headers=headers)
        deliver_soup.raise_for_status()
        deliver_soup.encoding = deliver_soup.apparent_encoding
        deliver = deliver_soup.text
        con = re.sub(r"LoadUsedCarPriceGetUsedCarData", "", str(deliver))
        con2 = re.sub("," + i, "", str(con[-10:-1]))
        con3 = con[1:-10] + con2
        last = json.loads(con3)
        deliver_key = {}
        for ki in last['body']['items']:
            deliver_key[ki["specId"]] = ki["priceArea"]
        # print(deliver_key)

        # 采集车的总型号
        car = soup.find("div", class_="list-cont", attrs={"data-value": i})
        car_name = car.find("div", class_="list-cont-main")
        car_name_only = car_name.find("div", class_="main-title").get_text()

        # 采集口碑信息
        url_koubei = 'https://k.autohome.com.cn/' + str(i)
        print(url_koubei)
        content_koubei = htmlparser(url_koubei)
        soup_koubei = BeautifulSoup(content_koubei, "html.parser")
        car_koubei_soup = soup_koubei.find("ul", class_="score_tag__Wq2Z4")
        car_koubei_test = car_koubei_soup.get_text()
        if car_koubei_test != '':
            car_koubei_test = car_koubei_test.replace('\xa0', '')
            car_koubei = []
            for j in car_koubei_test:
                car_koubei.append(j)
            car_koubei[0] = '{"' + car_koubei[0]
            car_koubei[-1] = car_koubei[-1] + '"}'
            for j in range(1, len(car_koubei) - 1):
                if is_Chinese(car_koubei[j]):
                    if not is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '":'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            for j in range(1, len(car_koubei) - 1):
                if not is_Chinese(car_koubei[j]):
                    if is_Chinese(car_koubei[j + 1]):
                        car_koubei[j] = car_koubei[j] + '",'
                        car_koubei[j + 1] = '"' + car_koubei[j + 1]
            car_koubei = ''.join(car_koubei)
            # car_koubei = eval(car_koubei)
        else:
            car_koubei = '暂无口碑数据'
        print(car_koubei)


        # 下面采集车的具体型号信息
        car_model = soup.find("div", class_="intervalcont fn-hide", attrs={"id": "divSpecList" + i})
        for k in car_model.find_all("div", class_="interval01"):
            car_model_size = k.find("div", class_="interval01-title title-cont")  # 6.0升 517马力的父节点
            car_model_size_only = car_model_size.find("div", class_="interval01-list-cars").get_text()  # 6.0升 517马力
            print(car_model_size_only)
            car_model_size_value = k.find_all("ul", class_="interval01-list")  # 该属性的下属分类（具体类型）
            for g in car_model_size_value:
                for li in g.find_all("li"):
                    flag = False
                    for ke in deliver_key.keys():
                        key = ke
                        key = str(key)
                        if key == li["data-value"]:
                            flag = True  # 这里卡了一会儿bug，主要原因是：在字典中的数字被认为int型，不是str型
                            with open("data.txt", 'a', encoding="utf-8") as f:
                                f.write(
                                    car_total_name + "*" + car_name2 + "*" + car_name_only + "*停售*" + car_model_size_only + "*" +
                                    str(deliver_key[ke]) + "*" +
                                    li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                    li.find("div", class_="interval01-list-guidance").get_text() + "*" + car_koubei
                                )
                            with open("data.txt","a",encoding="utf-8") as f :
                                f.write("\n")
                            print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ",
                                      str(deliver_key[ke]), " ", li.get_text() + car_koubei)
                            break
                        else:
                            pass
                    if flag == False:
                        with open("data.txt", 'a', encoding="utf-8") as f:
                            f.write(
                                car_total_name + "*" + car_name2 + "*" + car_name_only + "*停售*" + car_model_size_only + "*" +
                                "暂无报价*" +
                                li.find("div", class_="interval01-list-cars-infor").get_text() + "*" +
                                li.find("div", class_="interval01-list-guidance").get_text() + "*"+ car_koubei
                                )
                        with open("data.txt", "a", encoding="utf-8") as f:
                            f.write("\n")
                        print(car_total_name, " ", car_name_only, " ", car_model_size_only, " ", "暂无报价", " ",
                                      li.get_text()+ car_koubei)
                    else:
                        pass
    time.sleep(1)

urls =[]
def spider(i):
    content = htmlparser(i)
    soup = BeautifulSoup(content, "html.parser")
    big_urls = soup.find_all("dl", class_="list-dl")
    for j in big_urls:
        big_url = j.find("dt")
        big_url_1 = big_url.find("a")
        big_url_2 = big_url_1["href"]
        content = htmlparser("https://car.autohome.com.cn" + big_url_2)
        soup = BeautifulSoup(content, "html.parser")
        sort_name_1 = soup.find("div", attrs={"class": "tab-nav border-t-no"})
        sort_name_3 = sort_name_1.find("ul", attrs={"data-trigger": "click"})
        # 查找在售，停售，即将销售
        for sort_name_2 in sort_name_3.find_all("a"):
            if (sort_name_2["title"] == "在售是指官方已经公布售价且正式在国内销售的车型"):
                sort_url_courrent = "https://car.autohome.com.cn" + sort_name_2["href"]
                urls.append(sort_url_courrent)  # zch:暂时没用
                print(sort_url_courrent)
                current_spider(sort_url_courrent)
                content = htmlparser(sort_url_courrent)
                soup = BeautifulSoup(content, "html.parser")
                # 判断是否有下一页
                div = soup.find("div", class_="price-page")
                if div == None:
                    pass
                else:
                    next_url = div.find("a", class_="page-item-next")
                    print(next_url["href"])
                    if next_url == None:
                        pass
                    else:
                        next_url = "https://car.autohome.com.cn" + next_url["href"]
                        current_spider(next_url)
                        time.sleep(1)
                        urls.append(next_url)
            if (sort_name_2["title"] == "即将销售是指近期即将在国内销售的车型"):
                sort_url_future = "https://car.autohome.com.cn" + sort_name_2["href"]
                urls.append(sort_url_future)
                future_spider(sort_url_future)
                content = htmlparser(sort_url_future)
                soup = BeautifulSoup(content, "html.parser")
                # 判断是否有下一页
                div = soup.find("div", class_="price-page")
                if div == None:
                    pass
                else:
                    next_url = div.find("a", class_="page-item-next")
                    print(next_url["href"])
                    if next_url == None:
                        pass
                    else:
                        next_url = "https://car.autohome.com.cn" + next_url["href"]
                        future_spider(next_url)
                        time.sleep(1)
                        urls.append(next_url)
            if (sort_name_2["title"] == "停售是指厂商已停产并且经销商处已无新车销售的车型"):
                sort_url_stop = "https://car.autohome.com.cn" + sort_name_2["href"]
                urls.append(sort_url_stop)
                stop_spider(sort_url_stop)
                content = htmlparser(sort_url_stop)
                soup = BeautifulSoup(content, "html.parser")
                # 判断是否有下一页
                div = soup.find("div", class_="price-page")
                if div == None:
                    pass
                else:
                    next_url = div.find("a", class_="page-item-next")
                    print(next_url["href"])
                    if next_url == None:
                        pass
                    else:
                        next_url = "https://car.autohome.com.cn" + next_url["href"]
                        stop_spider(next_url)
                        time.sleep(1)
                        urls.append(next_url)
def main():
    global urls
    with open("car_url.txt", "r") as f:
        url_list = f.readlines()
    with open("car_url_name.txt", 'r',encoding="utf-8") as f:
         last_url_name = f.readlines()
    count = 0

    for i in url_list:
        car_list =[]
        global car_total_name
        car_total_name = last_url_name[count]
        car_total_name = car_total_name.strip("\n")
        print(car_total_name)
        count = count + 1
        i = i.strip("\n")
        url = 'https://car.autohome.com.cn'+i
        spider(url)

main()