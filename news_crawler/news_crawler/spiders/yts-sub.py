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


class YTSSubs(scrapy.Spider):
    '''Crawl tin tức từ https://vnexpress.net website
    ### Các tham số:
        category: Chủ đề để crawl, có thể bỏ trống. Các chủ đề
                 * giao-duc
                 * suc-khoe
                 * khoa-hoc
                 * so-hoa
                 * giai-tri
                 * the-thao
                 * doi-song
                 * du-lich
        limit: Giới hạn số trang để crawl, có thể bỏ trống.
    '''
    name = "yts-sub"
    folder_path = "yts-sub"
    page_limit = None
    start_urls = ["https://yts-subs.net/language/vietnamese"]

    def __init__(self, limit=None, *args, **kwargs):
        super(YTSSubs, self).__init__(*args, **kwargs)
        if limit != None:
            self.page_limit = int(limit)

        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        self.count_page = 0


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_list_movie)

    def parse_list_movie(self, response):
        if (self.count_page >= self.page_limit or self.page_limit <= 0) and self.page_limit is not None:
            return

        # Get first article
        movie_list = response.css("div div div ul.media-list")
        for row in movie_list:
            for movie in row.css("li.media"):     
                relative_url = movie.css('div.media-body a::attr(href)').get()
                abs_url = response.urljoin(relative_url)
                if abs_url:
                    yield scrapy.Request(abs_url, callback=self.parse_moive)


        time.sleep(5)
        next_page_url = self.extract_next_page_url(response)
        # print(next_page_url)
        if next_page_url is not None:
            self.count_page = self.count_page + 1
            # Đệ qui để crawl trang kế tiếp
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_list_movie)
        else:
            return

                
    def extract_next_page_url(self, response):
        next_page_element = response.css('div div div ul.pagination')
        next_page_url = next_page_element.css('li a::attr(href)').getall()
        return next_page_url[-2]

    def parse_moive(self, response):
        languages_subs = response.css("div div div div table tbody")
        vietnamese_subs = languages_subs.css('tr')[-1]
        vietnamese_subs_url = vietnamese_subs.css('td.download-cell a::attr(href)').get()
        vietnamese_subs_url = response.urljoin(vietnamese_subs_url)
        if vietnamese_subs_url:
            yield scrapy.Request(vietnamese_subs_url, callback=self.parse_subs)


    def parse_subs(self, response):
        movie_name = response.xpath('/html/body/div[3]/div/div[1]/div[3]/h2/text()').extract_first()
        movie_name = movie_name + '.zip'
        document_function = response.xpath('/html/body/script[2]/text()').extract_first()
        document_function_split = [i.strip() for i in document_function.split('\r\n')]
        dl = document_function_split[3].split('=')[-1].strip()
        t = document_function_split[4].split('=')[-1].strip()
        subs_url = t[1:-2] + dl[1:-2] + '.zip'
        output_url = os.path.join(self.folder_path, movie_name)
        r = requests.get(subs_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(os.path.join(self.folder_path, movie_name))


 