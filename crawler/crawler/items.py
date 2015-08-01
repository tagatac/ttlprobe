# -*- coding: utf-8 -*-

import scrapy

class CrawlerItem(scrapy.Item):
    referer = scrapy.Field()
    scripts = scrapy.Field()
