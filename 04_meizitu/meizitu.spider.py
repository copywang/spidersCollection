#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import os
from config import *
import pymongo


client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

url = 'http://www.mzitu.com/hot/'

def get_first_page(url):
    try:
        print('请求首页中')
        response = requests.get(url)
        if response.status_code == 200:
            print('请求首页成功')
            return response.text
    except RequestException:
        print('请求首页失败')

def parse_first_page(html):
    # 获取所有页码的链接，得到翻页的链接
    soup = BeautifulSoup(html,'lxml')
    page_num = soup.find_all(class_='page-numbers')
    # print(page_num[-2])
    pattern = re.compile('.*?/page/(\d+).*?')
    result = re.search(pattern,str(page_num[-2]))
    # print(result.group(1))
    print('一共有 ',result.group(1),'页')
    return result.group(1)

def get_more_page(page_num):
    temp_list = []
    for i in range(1,page_num+1):
        url = 'http://www.mzitu.com/page/' + str(page_num) +'/'
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            pins = soup.find_all(id='pins')
            str_pins = str(pins)
            pattern = re.compile('.*?<li><a href="(.*?)".*?', re.S)
            result = re.findall(pattern, str_pins)
            for i in result:
                temp_list.append(i)
        except RequestException:
            return None
    print('结果一共 ',len(temp_list),' 图片页')
    return temp_list

def save_to_mongo(title,url,count,image_url):
    if db[MONGO_TABLE].insert({'title':title,'url':url,'count':count,'image_url':image_url}):
        print('【',title,'】','第 ',count,' 张图存储到MongoDB成功')
        return True
    else:
        return False

def main(detail_url):
    try:
        # 获取详情页的页面
        response = requests.get(detail_url)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        page_num = soup.find_all(class_='pagenavi')
        pattern = re.compile('.*?<span>4</span>.*?<span>(\d+)</span>.*?', re.S)
        result = re.search(pattern, str(page_num))
        # 找出详情页一共有多少张图片
        int_result = int(result.group(1))
        for count in range(1,int_result+1):
            url_new = '{}/{}'.format(detail_url, count)
            response = requests.get(url_new)
            result = response.text
            # 找出标题和图片下载地址
            pattern = re.compile('<div class="main-image"><p><a href=.*?><img src="(.*?)".*?alt="(.*?)".*?')
            img = re.search(pattern,result)
            image_url = img.group(1)
            title = img.group(2)
            title = title.replace('?','_')
            dirName = u"jpg/【{}P】{}".format(int_result, title)
            save_path = '{0}/{1}'.format(os.getcwd(), dirName)
            if not os.path.exists(save_path):
                os.mkdir(dirName)
            header = {
                'Host': 'i.meizitu.net',
                'Pragma': 'no-cache',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': '{}'.format(image_url),
            }
            save_to_mongo(title, url_new,count,image_url)
            try:
                print('正在下载图片：', image_url)
                img_response = requests.get(image_url, headers=header)
                file_path = '{0}/{1}/{2}.{3}'.format(os.getcwd(), dirName, count, 'jpg')
                if img_response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                        print('下载图片 :', image_url, '成功')
                        f.close()
                else:
                    print('图片请求出错', image_url)
                    return None
            except RequestException:
                print('图片请求出错', image_url)
                return None
    except RequestException:
        print('请求图片页 ',detail_url,'失败')

if __name__ == '__main__':
    start = time.clock()
    # 获取第一页
    first_html = get_first_page(url)
    # 解析第一页，获取总页数
    total_page_num = parse_first_page(first_html)
    # 获取所有页
    int_total_page_num = int(total_page_num)
    print('一共有 ',int_total_page_num,'页数据')
    expect_page_num = input('请输入页码：')
    # detail_url_list = get_more_page(int_total_page_num)
    detail_url_list = get_more_page(int(expect_page_num))
    for detail_url in detail_url_list:
        main(detail_url)
        time.sleep(2)
    end = time.clock()
    print('运行时间：',end-start)




