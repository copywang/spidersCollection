# -*- coding: utf-8 -*-
import requests
import time
import re
from urllib.parse import urlencode
from selenium import webdriver
import os
import pymongo
from multiprocessing import Pool,Lock

browser = webdriver.PhantomJS()
client = pymongo.MongoClient('localhost', connect=False)
db = client['xiachufang']

def get_one_page(url,header,offset):
    response = requests.get(url, headers=header, allow_redirects=True)
    if response.status_code == 404:
        pass
    else:
        html = response.text
        return html

def parse_one_page(html):
    #菜谱链接，图片地址，菜名，材料，七天内多少人做过，作者
    # pattern = re.compile('<li>.*?<a href="/recipe/(\d+)/".*?target="_blank">.*?<div class="cover pure-u">.*?<img src.*?data-src="(.*?)" width.*?alt="(.*?)".*?"ing ellipsis">(.*?)</p>.*?"bold">(\d+)</span>.*?"gray-font">(.*?)</span>.*?</p>.*?</li>', re.S)
    pattern = re.compile(
        '<li>.*?<a href="/recipe/(\d+)/".*?target="_blank">.*?<div class="cover pure-u">.*?<img.*?src.*?data-src="(.*?)" width.*?alt="(.*?)".*?"ing ellipsis">(.*?)</p>.*?"bold score">(\d+)</span>.*?"gray-font">(.*?)</span>.*?</p>.*?</li>',
        re.S)
    items = re.findall(pattern,html)
    # print(type(items),len(items))
    for item in items:
        yield {
            'detail_url': 'http://www.xiachufang.com/recipe/'+ item[0],
            'image_url': item[1],
            'name': item[2].replace("?","").replace(":","").replace("\\","").replace("/","").replace("*","").replace("<","").replace(">","").replace("|",""),
            'material': item[3].replace("\n","").strip(), #去掉空格和换行符,
            'used': item[4],
            'author': item[5]
        }

def parse_detail_page(keyword,detail_url,dish_name):
    # 获取网页并截图保存
    dish_name = detail_url.split('/')[-1] + '_' + dish_name
    path = u"{0}/{1}/{2}/{3}".format(os.getcwd(),'data',keyword,dish_name)
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = '{0}/{1}.{2}'.format(path,dish_name,'png')

    browser.get(detail_url)
    element = browser.find_element_by_xpath('//div[@class="block recipe-show"]')
    element.screenshot(file_name)
    print('saved',keyword,'dish_name',dish_name,'ok')

def save_to_mongo(keyword,data):
    if db[keyword].insert(data):
        return True
    else:
        return False

def main(offset):
    url = 'http://www.xiachufang.com/search/?'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
    b_url = 'http://www.xiachufang.com/category/40071/' + '?page=' + str(offset)
    # http://www.xiachufang.com/category/40071/?page=2
    print('page url is', b_url)
    print('now getting', '早餐', 'page', offset, 'content')
    html = get_one_page(b_url, header, offset)
    parse_one_page(html)
    for i in parse_one_page(html):
        save_to_mongo('早餐', i)
        parse_detail_page('早餐', i['detail_url'], i['name'])
    print('parse', '早餐', 'page', offset, 'done')

    keywords = ['午餐', '晚餐']
    for keyword in keywords:
        data = {
            'keyword': keyword,
            'cat': '1001',
            'page': offset
        }
        url_new = url + urlencode(data)
        print('page url is',url_new)
        print('now getting',keyword,'page',offset,'content')
        html = get_one_page(url_new,header,offset)
        parse_one_page(html)
        for i in parse_one_page(html):
            save_to_mongo(keyword,i)
            parse_detail_page(keyword,i['detail_url'],i['name'])
        print('parse',keyword,'page',offset,'done')


if __name__ == "__main__":
    start = time.clock()
    pool = Pool()
    # for i in range(1,6):
    #     main(i)

    pool.map(main,[i for i in range(1,6)])
    print('all done')
    end = time.clock()
    print('total time', end-start)
	browser.close()
	



