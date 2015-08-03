# -*- coding: utf-8 -*-
import scrapy, json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import CrawlerItem

class TopChinese(CrawlSpider):
	name = 'topchinese'
	with open('alexalist.json', 'r') as fp:
		jsondata = json.load(fp)
	allowed_domains = list()
	for page in jsondata:
		allowed_domains += map(lambda site: site.lower(), page['sites'])
	start_urls = list('http://www.' + domain.lower() for domain in allowed_domains)
	#custom_settings = {'DEPTH_LIMIT': 1}

	rules = (
		Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item', follow=True),
	)

	def parse_item(self, response):
		i = CrawlerItem()
		i['referer'] = response.url
		i['scripts'] = list()
		for sel in response.xpath('//script'):
			# valid URI characters according to
			# http://tools.ietf.org/html/rfc3986#section-2
			for jsfile in sel.re('http[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\-._~:/?#\[\]@!$&\'()*+,;=]*\.js'):
				i['scripts'].append(jsfile)
		if i['scripts']: yield i
