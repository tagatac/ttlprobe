# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from crawler.items import CrawlerItem

class TopChinese(CrawlSpider):
    name = 'topchinese'
    allowed_domains = ['baidu.com']
    start_urls = ['http://www.baidu.com/']
    #custom_settings = {'DEPTH_LIMIT': 1}

    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
	i = CrawlerItem()
	i['url'] = response.url
	yield i
