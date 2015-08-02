# -*- coding: utf-8 -*-
import scrapy

class CrawlerItem(scrapy.Item):
	referer = scrapy.Field()
	scripts = scrapy.Field()

class AlexaItem(scrapy.Item):
	page = scrapy.Field()
	sites = scrapy.Field()
