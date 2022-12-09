#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
# from ip import Master
import os
import time
import json
from codecs import open
from datetime import datetime
import re

# master = Master("bedf715e1b6830a6dc61ac805aafcee0","tmproxy")
URL = 'https://vnexpress.net/'

# Hash table chưa tên chủ đề, để tạo thư mục
CATEGORIES = {
    'giao-duc': 'Giáo dục',
    'suc-khoe': 'Sức khoẻ',
    'khoa-hoc': 'Khoa học',
    'giai-tri': 'Giải trí',
    'the-thao': 'Thể thao',
    'doi-song': 'Đời sống',
    'du-lich': 'Du lịch',
    'the-gioi': 'Thế Giới',
    'thoi-su': 'Thời sự',
    'phap-luat': 'Pháp Luật',
    'kinh-doanh': 'Kinh doanh',

}

CATEGORIES_COUNTER = {
    'giao-duc': 0,
    'suc-khoe': 0,
    'khoa-hoc': 0,
    'so-hoa': 0,
    'giai-tri': 0,
    'the-thao': 0,
    'doi-song': 0,
    'du-lich': 0,
}

class VnExpress(scrapy.Spider):
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
    name = "vnexpress"
    folder_path = "vnexpress"
    page_limit = None
    start_urls = [
    ]

    def __init__(self, category=None, limit=None, *args, **kwargs):
        super(VnExpress, self).__init__(*args, **kwargs)
        if limit != None:
            self.page_limit = int(limit)

        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        if category in CATEGORIES:
            folders_path = self.folder_path + '/' + CATEGORIES[category]
            if not os.path.exists(folders_path):
                os.makedirs(folders_path)
            self.start_urls = [URL + category + '-p2']
        else:
            for CATEGORY in CATEGORIES:
                folders_path = self.folder_path + '/' + CATEGORIES[CATEGORY]
                if not os.path.exists(folders_path):
                    os.makedirs(folders_path)
                self.start_urls.append(URL + CATEGORY + '-p2')

    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url=url, callback=self.parse_list_news)
            # request.meta["proxy"] = master.random_ip()
            yield scrapy.Request(url=url, callback=self.parse_list_news)

    def parse_list_news(self, response):
        category = self.get_category_from_url(response.url)
        if (CATEGORIES_COUNTER[category] >= self.page_limit or self.page_limit <= 0) and self.page_limit is not None:
            return

        # Get first article
        list_articles = response.css("article")
        for article in list_articles:
            time.sleep(1)
            relative_url = article.css('div.thumb-art a::attr(href)').get()
            abs_url = response.urljoin(relative_url)
            if "https://vnexpress.net" in abs_url:
                yield scrapy.Request(abs_url, callback=self.parse_news)



        next_page_url = self.extract_next_page_url(response)

        if category in CATEGORIES and next_page_url is not None:
            CATEGORIES_COUNTER[category] = CATEGORIES_COUNTER[category] + 1
            # Đệ qui để crawl trang kế tiếp
            new_request = scrapy.Request(response.urljoin(next_page_url), callback=self.parse_list_news)
            # new_request.meta["proxy"] = master.random_ip()
            yield new_request
        else:
            return

                
    def extract_next_page_url(self, response):
        next_page_url = response.xpath('//*[@id="pagination"]/div/a[5]/@href').extract_first()
        return next_page_url

    def parse_news(self, response):

        jsonData = self.extract_news(response)

        # yield jsonData

        items = response.url.split('/')

        # Write to file
        filename = '%s.json' % (items[-1])
        with open(self.folder_path + "/" + filename, 'wb', encoding = 'utf-8') as fp:
            json.dump(jsonData, fp, ensure_ascii= False)
            self.log('Saved file %s' % filename)


    def get_category_from_url(self, url):
        items = url.split('/')
        category = None
        if len(items) >= 4:
            category = re.sub(r'-p[0-9]+', '', items[3])
        return category

    def extract_news(self, response):

        date = self.extract_date(response)
        title = self.extract_title(response)
        content = self.extract_content(response)
        author = self.extract_author(response)
        description = self.extract_description(response)

        jsonData = {
            'date': date,
            'title': title,
            'link': response.url,
            'content': content,
            'author': author,
            'description': description
        }

        return jsonData

    def extract_title(self, response):
        news = response.css("section div div")
        title = news.css("h1::text").extract_first()
        return title

    def extract_description(self, response):
        news = response.css("section div div")
        description = news.css("p::text").extract_first()
        return description

    def extract_content(self, response):
        news = response.css("section div div")
        p_elements = news.css("article p")
        list_contents = []
        for p in p_elements:
            content = p.css("::text").getall()
            list_contents.extend(content)

        contents = ''.join(list_contents)
        return contents

    def extract_date(self, response):
        news = response.css("section div div")
        date = news.css("div span.date::text").extract_first()
        return date
    
    def extract_author(self, response):
        news = response.css("section div div")
        author = news.css("article p strong::text").extract_first()
        if author is None:
            author = news.css("p.Normal strong::text").extract_first()
        if author is None:
            author = response.css("section section p.Normal strong::text").extract_first()
        return author