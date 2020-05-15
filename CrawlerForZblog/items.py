# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerforzblogItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItem(scrapy.item):
    collection = table = 'news'
    category = scrapy.Item()
    website = scrapy.Item()
    title = scrapy.Item()
    guid = scrapy.Item()
    news = scrapy.Item()
    url = scrapy.Item()
    plaintext = scrapy.Item()
