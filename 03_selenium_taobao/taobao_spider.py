#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from pyquery import PyQuery as pq
import pymongo
from config import *

browser = webdriver.Firefox()
client = pymongo.MongoClient(MONGO_URL)#连接MONGODB
db = client[MONGO_DB]

def search(key_word):
    try:
        browser.get('https://www.taobao.com')
        # 输入框加载完成
        input = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#q'))
        )
        # 搜索按钮加载完成
        submit = WebDriverWait(browser,10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button'))
        )
        input.send_keys(key_word)
        submit.click()
        # 获取一共有多少页结果
        total_page = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'div.total'))
        )

        get_products(1)
        # 打印一共有多少页结果
        return total_page.text
    except TimeoutError:
        # 出现错误，重新请求一次
        return search()

def next_page(page_num):
    try:
        print('跳转到: 第', page_num,'页')
        # 输入框加载完成
        input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        # 搜索按钮加载完成
        submit = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        # 清空后输入
        input.clear()
        input.send_keys(page_num)
        submit.click()

        finish_load = WebDriverWait(browser, 10).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num))
        )
        if finish_load:
            print('第 ',page_num,' 页加载完成')
            get_products(page_num)
    except TimeoutError:
        next_page(page_num)

def get_products(page_num):
    print('开始采集第 ',page_num,' 页信息')
    WebDriverWait(browser,10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))
    )
    html = browser.page_source
    doc = pq(html)

    items = doc('#mainsrp-itemlist .items .item').items()
    index = 0
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        save_to_mongo(index,product,page_num)
        index = index + 1
def save_to_mongo(index,result,page_num):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存第 ',page_num,'页 第',index,'条信息到MONGODB成功')
    except Exception:
        print('保存第 ',page_num,'页 第',index,'条信息到MONGODB成功')

def main(key_word):
    try:
        print('开始采集 ',key_word,' 信息')
        total_page = search(key_word)
        total_page = int(re.compile('.*?(\d+).*?').search(total_page).group(1))
        print('一共有',total_page,'页数据')
        for i in range(2,total_page+1):
            next_page(i)
    except TimeoutError:
        print('error')
    finally:
        browser.close()

if __name__ == '__main__':
    main(key_word)
