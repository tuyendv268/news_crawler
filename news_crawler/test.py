# import scrapy
# class Test(scrapy.Spider):
#     name = "test"

#     start_urls = [
#         "https://yts-subs.net/subtitle/sing-2-vietnamese-307933",
#     ]

#     def parse(self, response):
#         filename = response.url.split("/")[-1] + '.html'
#         with open(filename, 'wb') as f:
#             f.write(response.body)
import requests, zipfile, io
r = requests.get("https://yifysubtitles.org/subtitle/sing-2-2021-vietnamese-yify-380411.zip")
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("content")