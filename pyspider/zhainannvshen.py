#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-27 19:31:47
# Project: zhainannvshen

from pyspider.libs.base_handler import *
import os


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        # self.crawl('https://www.nvshens.com/tag/new/', callback=self.index_page, validate_cert=False)
        for i in range(1, 16):
            next_page = 'https://www.nvshens.com/tag/new/' + str(i) + '.html'
            self.crawl(next_page, callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('strong > a').items():
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        pic_url = response.doc(
            '#post > div:nth-child(8) > div > div.post_entry > ul > li > div.igalleryli_div > a').attr.href
        print(pic_url)
        self.crawl(pic_url, callback=self.picture_page, validate_cert=False)
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "pic_url": response.doc(
                '#post > div:nth-child(8) > div > div.post_entry > ul > li > div.igalleryli_div > a').attr('href')
        }

    def picture_page(self, response):
        title = response.doc('#htilte').text().replace(" ", "_")
        print('title:', title)
        dirName = u"pyspider\【{}】".format(title)
        print('dirName:', dirName)
        dir_path = '{0}\{1}'.format(os.getcwd(), dirName)
        print('dir_path: ', dir_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        if os.path.exists(dir_path):
            for img in response.doc('#hgallery > img').items():
                url = img.attr.src
                if url:
                    file_name = '{0}\{1}'.format(dir_path, url.split('/')[-1])
                    print('file_name: ', file_name)
                    self.crawl(url, callback=self.save_img,
                               save={'file_name': file_name, 'dir_path': dir_path}, validate_cert=False)
            next = response.doc('#pages > a:nth-child(10)').attr.href
            self.crawl(next, callback=self.picture_page, validate_cert=False)

    def save_img(self, response):
        content = response.content
        file_name = response.save['file_name']
        print('dir_path in save_img: ', response.save['dir_path'])
        path = os.path.exists(response.save['dir_path'])
        print(path)
        if response.status_code == 200:
            if os.path.exists(path):
                f = open(file_name, 'wb')
                f.write(content)
                print('save image ok: ', file_name)
                f.close()
            else:
                print('dir not exist: ', path)
        else:
            print('save failed: ', file_name)


