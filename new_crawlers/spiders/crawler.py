import json
import os
import time
import scrapy

class NewCrawler(scrapy.Spider):
    name="crawler"
    base_url = "https://zingnews.vn"
    output_path = "datas"
    
    def start_requests(self):
        path = "C:/Users/tuyen/OneDrive/Documents/vndg/new_crawlers/urls.txt"
        with open(path, "r", encoding="utf-8")as tmp:
            urls = tmp.readlines()
            urls = [url.replace("\n","") for url in urls]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        articles = response.xpath('//*[@id="news-latest"]/section/div/article')
        for article in articles:
            url = article.xpath('p/a/@href').extract_first()
            abs_url = self.base_url+"/"+url
            time.sleep(0.5)
            yield scrapy.Request(url=abs_url, callback=self.parse_art)

    def parse_art(self, response):
        content = response.css('#page-article div.page-wrapper article section.main div.the-article-body p::text').getall()
        description = response.css('#page-article div.page-wrapper article section.main p.the-article-summary::text').get()
        title = response.css('#page-article div.page-wrapper article header.the-article-header h1.the-article-title::text').get()
        _id =response.css('#page-article div.page-wrapper article::attr(article-id)').get()
        
        res ={
            "title" : title,
            "description":description,
            "id":_id,
            "content":" ".join(content).replace("\n"," ")
        }
        
        file_name = str(response.url).split("/")[-1] + ".json"
        abs_path = os.path.join(self.output_path, file_name)
        
        with open(abs_path,"w", encoding="utf-8") as tmp:
            tmp.write(json.dumps(res, indent=3, ensure_ascii=False))
            print("saved : ", file_name)
