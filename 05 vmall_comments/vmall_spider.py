#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
from requests.exceptions import RequestException
import json
from functools import reduce
import time
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

def parse_all_url(html):
    pattern = re.compile('<div class="pro-panels">.*?<a target="_blank" href="(.*?)".*?'
                         'title="(.*?)".*?src="(.*?)".*?<p class="p-price">.*?(\d+).*?</div>',re.S)
    results = re.findall(pattern,html)

    for result in results:
        # print(result)
        yield {
            'product-link': 'https://www.vmall.com' + result[0],
            'title': result[1],
            'image_link': result[2],
            'price': result[3]
        }

def get_comments(url,title,price):

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
    try:
        print('正在请求',title,'的评论页')
        html = requests.get(url,headers = header)
        if html.status_code == 200:
            result = html.text
            id_pattern = re.compile('https://.*?/(\d+).html',re.S)
            product_ids = re.findall(id_pattern,url)
            for product_id in product_ids:
                find_total_page = re.compile('.*?,"totalPage":(\d+),"', re.S)
                first_page = 'https://remark.vmall.com/remark/queryEvaluate.json?pid=' + product_id + '&pageNumber=1'
                first_comment_page = requests.get(first_page, headers=header)
                total_page = int(re.findall(find_total_page,first_comment_page.text)[0])
                print('一共有',total_page,'页评论')

                for count in range(1,total_page + 1):
                    print('正在请求', title, '产品ID：', product_id, '的第', count, '页评论数据')
                    url_comment = 'https://remark.vmall.com/remark/queryEvaluate.json?pid=' + product_id + '&pageNumber=' + str(
                        count)
                    print('请求页面：', url_comment)
                    comments = requests.get(url_comment, headers=header)
                    check_pattern = re.compile('.*?"content":"(.*?)"', re.S)

                    if re.findall(check_pattern, comments.text):
                        print('再请求1次')
                        time.sleep(0.1)
                        comments = requests.get(url_comment, headers=header)
                        if comments.status_code == 200:
                            print('请求评论页：', url_comment, '成功')
                            comments_pattern = re.compile(
                                '.*?"content":"(.*?)","createDate":"(.*?)","custId":(.*?),"custName":"(.*?)","custNameStatus":(.*?),"gradeCode":(.*?),"id":(.*?),"labelList":(.*?),"msgReplyList":(.*?),"productId":"(.*?)","remarkLevel":"(.*?)","score":(\d+)',
                                re.S)
                            items = re.findall(comments_pattern, comments.text)
                            print('请求第 ', count, '页内容评论')
                            for item in items:
                                item_list = list(item)
                                temp_dict = {}
                                temp_dict = {
                                    'title': title,
                                    'price': price,
                                    'comment': item_list[0],
                                    'date': item_list[1],
                                    'user-id': item_list[2],
                                    'user-name': item_list[3],
                                    'id': item_list[4],
                                    'label': item_list[5],
                                    'remarkLevel': item_list[-2],
                                    'score': item_list[-1]
                                }
                                save_to_mongo(temp_dict)
                    else:
                        print('不存在评论页', count, '跳过')
                        break
        else:
            return None
    except RequestException:
        return None

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print(result.get('title'),'存储到MongoDB成功')
    else:
        return None

def main():
    url = 'https://www.vmall.com/list-111'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    }
    try:
        html = requests.get(url,headers = header)
        if html.status_code == 200:
            result = html.text
            all_url = parse_all_url(result)
            for item in all_url:
                print('正在请求',item['product-link'])
                comments = get_comments(item['product-link'],item['title'],item['price'])
        else:
            return None
    except RequestException:
        return None

if __name__ == '__main__':
    start = time.clock()
    main()
    end = time.clock()
    print('总运行时间',end-start)



