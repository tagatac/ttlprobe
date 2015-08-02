# -*- coding: utf-8 -*-
import scrapy
from crawler.items import AlexaItem

class AlexaSpider(scrapy.Spider):
	name = "alexa"
	allowed_domains = ["alexa.com"]
	start_urls = tuple('http://www.alexa.com/topsites/countries;'+str(j)+'/CN' for j in range(20))

	def parse(self, response):
		i = AlexaItem()
		i['page'] = response.url
		i['sites'] = list()
		for sel in response.xpath('//li[@class="site-listing"]//a/text()'):
			i['sites'].append(sel.extract())
		yield i

