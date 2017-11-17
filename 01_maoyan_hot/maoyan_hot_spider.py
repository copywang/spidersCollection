#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
from requests.exceptions import RequestException
import json
from multiprocessing import Pool
from functools import reduce

def get_one_page(url,header):
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    #排名，图片链接，片名，主演，上映时间，本月新增想看加密字符，总想看加密字符
    #由于有换行符，要加re.S参数
    patten = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?'
                        'title="(.*?)".*?"star">(.*?)</p>.*?"releasetime">(.*?)'
                        '</p>.*?"stonefont">(.*?);<.*?"stonefont">(.*?);',re.S)
    items = re.findall(patten, html)
    for item in items:
        yield {
            'index': item[0],
            'image-link': item[1],
            'title': item[2],
            'actors': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            # 根据映射表转换成实际数字
            'month-increase-want-to-watch': item[5],
            'total-want-to-watch': item[6]
        }

def write_to_file(content,offset):
    #print(offset)
    with open('result.log', 'a', encoding='utf-8') as f: #a参数表示往后追加
        f.write(json.dumps(content, ensure_ascii=False) + '\n') #dict转string用json.dumps
        f.close()


def main(offset):
    url = 'http://maoyan.com/board/6?offset=' + str(offset)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    header = {'User-Agent': user_agent}
    html = get_one_page(url,header)
    #print(html)
    for item in parse_one_page(html):
        s = item['month-increase-want-to-watch'].split(';')
        write_to_file(item,offset)

if __name__ == "__main__":

    # main(0)
    # 循环抓取
    for i in range(10):
        main(i*10)

    # 多线程抓取
    # pool = Pool()
    # pool.map(main, [i*10 for i in range(10)])
