#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import time
import re
from pprint import pprint
from config import *
import pymongo
import os
from  hashlib import md5
import os
from multiprocessing import Pool

cur_directory = os.getcwd()
if os.path.exists(cur_directory + '/jpg/'):
    pass
else:
    os.mkdir(cur_directory + '/jpg/')

# 声明一个MONGODB对象
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print(result.get('title'),'save to MongoDB successfully')
        return True
    else:
        return False

# 获取一个网页
def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3'
    }
    # 请求的url后面是需要把data编码，然后构建成一个完整的url
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('get index error url is: ',url)
        return None

# 解析1个网页
# 请求网页后返回的response是一串字符串格式，通过json.loads方法转换成JSON变量
# 定义一个生成器，放入url
def parse_one_page_index(html):
    try:
        data = json.loads(html)
# 查询是否有data和data的键名存在，并取出其中article_url
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except:
        pass
# 获取详情页的内容
def get_detail_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print('请求详情页错误',url)

# 解析详情页
def parse_detail_page(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.select('title')[0].get_text()
    # print(title)
    pattern = re.compile('gallery: JSON.parse\((.*?)\),\n', re.S) #
    result = re.search(pattern, html)
    # print(result.string)
    if result:
        data = json.loads(json.loads(result.group(1)))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            # print(type(images))

            for image in images:
                download_img(image)
                return {
                    'title': title,
                    'url': url,
                    'image': images
                }

        # print(type(data))
        # print(data)
        # print('*'*100)

def download_img(url):
    print('downloading image',url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # return response.content
            save_image_local(response.content,url)
        else:
            return None
    except RequestException:
        print('图片请求出错',url)
        return None

def save_image_local(content,url):
    # 文件路径，文件名，文件名后缀
    file_path = '{0}/{1}/{2}.{3}'.format(os.getcwd(),'jpg', md5(content).hexdigest(), 'jpg')

    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()
    else:
        print('image already download: ',url)

def main(offset):
    html = get_page_index(offset,keyword)
    for url in parse_one_page_index(html):
        detailhtml = get_detail_page(url)
        if detailhtml:
            result = parse_detail_page(detailhtml,url)
            # print(result)
            if result:
                save_to_mongo(result)

if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START,GROUP_END + 1)]
    pool = Pool()
    pool.map(main,groups)
    # for i in range(1,20):
    #     main(i*20)








