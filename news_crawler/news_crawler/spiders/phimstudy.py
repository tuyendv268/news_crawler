#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import os
import json
from codecs import open
from datetime import datetime
import re

URL = 'https://www.studyphim.vn/'
COUNT_PAGE = 0
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


class PhimStudy(scrapy.Spider):
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
    name = "phimstudy"
    folder_path = "phimstudy"
    page_limit = None
    start_urls = [
    ]

    def __init__(self, limit=None, *args, **kwargs):
        super(PhimStudy, self).__init__(*args, **kwargs)
        if limit != None:
            self.page_limit = int(limit)

        # Tạo thư mục
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)

        self.start_urls.append(URL + 'movies/search?sortBy=recommended&page=1')

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_list_movie)

    def parse_list_movie(self, response):
        global COUNT_PAGE
        if (COUNT_PAGE >= self.page_limit or self.page_limit <= 0) and self.page_limit is not None:
            return

        # Get first article
        row_movies = response.css("div div div div div div div.movie-row")
        for row in row_movies:
            for movie in row.css("div div.col-md-15"):     
                relative_url = movie.css('div div div.movie-img a::attr(href)').get()
                abs_url = response.urljoin(relative_url)
                if abs_url:
                    yield scrapy.Request(abs_url, callback=self.parse_moive)
                break

            break


        next_page_url = self.extract_next_page_url(response)
        # print(next_page_url)
        if next_page_url is not None:
            COUNT_PAGE = COUNT_PAGE + 1
            # Đệ qui để crawl trang kế tiếp
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_list_movie)
        else:
            return

                
    def extract_next_page_url(self, response):
        next_page_element = response.css('div div div div div div ul li')
        next_page_url = next_page_element.css('a::attr(href)').get()
        return next_page_url

    def parse_moive(self, response):
        episodes = response.css("div div div div.col-md-6 div a.btn")
        episodes_urls = episodes.css('::attr(href)').getall()
        for url in episodes_urls:
            url_split = url.split('?')
            url_play = url_split[0] + '/play?' + url_split[1]
            if url_play:
                yield scrapy.Request(url_play, callback=self.parse_moive)

        jsonData = self.extract_news(response)

        # yield jsonData

        items = response.url.split('/')

        # Write to file
        filename = '%s.json' % (items[-1])
        with open(self.folder_path + "/" + filename, 'wb', encoding = 'utf-8') as fp:
            json.dump(jsonData, fp, ensure_ascii= False)
            self.log('Saved file %s' % filename)


    def extract_movie(self, response):

        date = self.extract_date(response)
        title = self.extract_title(response)
        content = self.extract_content(response)
        author = self.extract_author(response)
        description = self.extract_description(response)

        jsonData = {
            'title': title,
            'link': response.url,
            'content': content,
            'author': author,
            'description': description
        }

        return jsonData

    def extract_title(self, response):
        title = response.css("div div div div div h3 small.text-muted::text").extract_first()
        return title

    def extract_description(self, response):
        description = response.css("div div div div div div div.article::text").extract_first()
        return description

    def extract_subscript(self, response):
        subscript = response.css("div div div div div.show-sub span")
        p_elements = news.css("article p")
        list_contents = []
        for p in p_elements:
            content = p.css("::text").getall()
            list_contents.extend(content)

        contents = ''.join(list_contents)
        return contents

    # def extract_date(self, response):
    #     news = response.css("section div div")
    #     date = news.css("div span.date::text").extract_first()
    #     return date
    
    # def extract_author(self, response):
    #     news = response.css("section div div")
    #     author = news.css("article p strong::text").extract_first()
    #     if author is None:
    #         author = news.css("p.Normal strong::text").extract_first()
    #     if author is None:
    #         author = response.css("section section p.Normal strong::text").extract_first()
    #     return author