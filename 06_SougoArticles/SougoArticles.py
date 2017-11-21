#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from requests.exceptions import ConnectionError
from urllib.parse import urlencode
from pyquery import PyQuery as pq

base_url = 'http://weixin.sogou.com/weixin?'
keyword = '碧缇福'

headers = {
    # 'Cookie':'IPLOC=CN4401; SUID=9FB420792513910A000000005A139321; SUV=1511232289693643; ABTEST=0|1511232292|v1; weixinIndexVisited=1; JSESSIONID=aaaVUmFEv71Ix6KV1Gv8v; ld=Qyllllllll2z9i21lllllVoF6TylllllWvj1XZllll9lllllVylll5@@@@@@@@@@; LSTMV=237%2C147; LCLKINT=2924; sct=6; PHPSESSID=3r1cuarlouqqbuulg19p993o10; SUIR=3F1581D8A1A4FFD58F52C657A1367E87; SNUID=2B0094CAB4B1EAC2C984B645B4C0EF85; ppinf=5|1511238526|1512448126|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo3NTolRTglQjUlQjAlRTglQkYlOUIlRTYlOTYlQjAlRTYlOTclQjYlRTQlQkIlQTMlMjAlRTclOEUlOEIlRTUlOEElQTAlRTklOTElQUJ8Y3J0OjEwOjE1MTEyMzg1MjZ8cmVmbmljazo3NTolRTglQjUlQjAlRTglQkYlOUIlRTYlOTYlQjAlRTYlOTclQjYlRTQlQkIlQTMlMjAlRTclOEUlOEIlRTUlOEElQTAlRTklOTElQUJ8dXNlcmlkOjQ0Om85dDJsdU02aENQSEFBbU1DUXNicTJfTVJLS2tAd2VpeGluLnNvaHUuY29tfA; pprdig=MZAQebubSYhSbvdpuFDFo8seHoi9h6qe_rJ6SQe3QGfOvE8M-0pkN1YAR6IohP9v2eIgEfl8omfq6pum9KOC_HamDBDMjpusGoS92wj_7n6RfPJ7bmX5R7MwYhubWZ4Rj46EDM8ldnSpylPGHvKALjefigu8eJux3XdmpPGfUtQ; sgid=20-32073949-AVoTq340B42SSv8EfEuhCZg; ppmdig=1511238526000000f44c21ed022991dd3d7f94eb34294393',
    'Cookie': 'IPLOC=CN4401; SUID=9FB420792513910A000000005A139321; SUV=1511232289693643; ABTEST=0|1511232292|v1; weixinIndexVisited=1; JSESSIONID=aaaVUmFEv71Ix6KV1Gv8v; ld=Qyllllllll2z9i21lllllVoF6TylllllWvj1XZllll9lllllVylll5@@@@@@@@@@; LSTMV=237%2C147; LCLKINT=2924; sct=6; PHPSESSID=3r1cuarlouqqbuulg19p993o10; SUIR=3F1581D8A1A4FFD58F52C657A1367E87; ppinf=5|1511240049|1512449649|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo3NTolRTglQjUlQjAlRTglQkYlOUIlRTYlOTYlQjAlRTYlOTclQjYlRTQlQkIlQTMlMjAlRTclOEUlOEIlRTUlOEElQTAlRTklOTElQUJ8Y3J0OjEwOjE1MTEyNDAwNDl8cmVmbmljazo3NTolRTglQjUlQjAlRTglQkYlOUIlRTYlOTYlQjAlRTYlOTclQjYlRTQlQkIlQTMlMjAlRTclOEUlOEIlRTUlOEElQTAlRTklOTElQUJ8dXNlcmlkOjQ0Om85dDJsdU02aENQSEFBbU1DUXNicTJfTVJLS2tAd2VpeGluLnNvaHUuY29tfA; pprdig=JEeIzQs2q4CH7FQGgCbgg-CH6duFuEFwFUlYgo2pzztpfMkkLUXfYgjoG6BF3yrboxfNfu-SGAu2SWem6cmHSQPMOZOg06qKFJt1wPdq9GJUkIhkJE-yvw1N70uAYN44XRXyAbH3vhfarW1vOYEUkswSHmJHOA8C7XK_TVBUSdA; sgid=20-32073949-AVoTsXF0UBDiauB0LnCaX33U; ppmdig=1511240049000000f4f36b4c91ab34c32296487a1c4ecf84; seccodeErrorCount=2|Tue, 21 Nov 2017 04:59:17 GMT; SNUID=7044CF96F0EAB198F0651628F0DB480D; seccodeRight=success; successCount=1|Tue, 21 Nov 2017 04:59:47 GMT',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}

proxy_pool_url = 'http://127.0.0.1:5000/get'
proxy = None
maxcount = 5

def get_proxy_ip():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('crawling',url)
    print('trying count',count)
    global proxy
    if count >= maxcount:
        print('Tried too many counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, headers=headers, allow_redirects=False, proxies=proxies)
        else:
            response = requests.get(url, headers=headers, allow_redirects=False)

        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # need change IP
            print('302')
            proxy = get_proxy_ip()
            if proxy:
                print('using proxy:', proxy)
                return get_html(url)
            else:
                print('get proxy ip failed')
                return None
    except ConnectionError as e:
        print('Error Occured', e.args)
        proxy = get_proxy_ip()
        count += 1
        return get_html(url,count)

# 构造请求参数
def get_index(keyword,page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    query = urlencode(data)
    url = base_url + query

    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')
def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('#js_profile_qrcode > div >strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

import pymongo
client = pymongo.MongoClient('localhost')
db = client['weixin-bitifu']
def save_to_mongo(data):
    if db['articles'].update({'title':data['title']},{'$set': data},True):
        print('Save to Mongo successfully', data['title'])
    else:
        print('Save to Mongo failed', data['title'])

def main():
    for page in range(1,101):
        html = get_index(keyword,page)
        # print(html)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    save_to_mongo(article_data)
                    # print(article_data)

if __name__ == '__main__':
    main()

