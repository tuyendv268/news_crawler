#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
import time
from codecs import open
from datetime import datetime
import re
import wget
import requests, zipfile, io

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
    'Sec-Fetch-User': '?1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}


class Tima(scrapy.Spider):
    '''Crawl tin tức từ https://vnexpress.net website
    '''
    name = "tima"
    folder_path = "tima"
    page_limit = None
    start_urls = ["https://tima.vn/tin-tuc/nguoi-vay"]

    def __init__(self, limit=None, *args, **kwargs):
        super(Tima, self).__init__(*args, **kwargs)
        if limit != None:
            self.page_limit = int(limit)

        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        self.count_page = 0


    def start_requests(self):
        url_file = open('/home/ngocpt/VIN-PROJECT/vnd-nlp-text-crawler/tima_urls.txt')
        article_list = url_file.readlines()
        article_list = [article.rstrip('\n') for article in article_list]
        self.start_urls = article_list
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_news)

    def parse_news(self, response):
        jsonData = self.extract_news(response)

        yield jsonData

        items = response.url.split('/')

        # Write to file
        filename = '%s.json' % (items[-1])
        with open(self.folder_path + "/" + filename, 'wb', encoding = 'utf-8') as fp:
            json.dump(jsonData, fp, ensure_ascii= False)
            self.log('Saved file %s' % filename)

    def extract_news(self, response):

        title = self.extract_title(response)
        content = self.extract_content(response)
        description = self.extract_description(response)

        jsonData = {
            'title': title,
            'link': response.url,
            'content': content,
            'description': description
        }

        return jsonData

    def extract_title(self, response):
        news = response.css("div div div div div div div div div#detailItem")
        title = news.css("h1::text").extract_first()
        return title

    def extract_description(self, response):
        news = response.css("div div div div div div div div div#detailItem")
        description = news.css("h2::text").extract_first()
        return description

    def extract_content(self, response):
        news = response.css("div div div div div div div div div#detailItem")
        list_contents = []
        for element in news.css("::text").getall()[:-2]:
            element = element.strip()
            if len(element.split()) > 15 and "line-height" not in element:
                list_contents.append(element)
        # p_elements = news.css("p")
        # list_contents = []
        # for p in p_elements:
        #     try:
        #         content = p.css("span span::text").getall()
        #     except:
        #         try:
        #             content = p.css("strong span span::text").getall()
        #         except:
        #             content = p.css("::text").getall()
        #     if content != []:
        #         list_contents.extend(content)

        contents = ' '.join(list_contents)
        return contents
