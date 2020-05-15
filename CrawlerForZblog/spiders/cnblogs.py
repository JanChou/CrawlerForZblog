# -*- coding: utf-8 -*-
import scrapy
from CrawlerForZblog.items import ArticleItem


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    start_urls = ['https://www.cnblogs.com/cate/dotnetcore/']

    def parse(self, response: scrapy.http.HtmlResponse):
        pass
