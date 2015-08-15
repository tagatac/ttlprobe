# -*- coding: utf-8 -*-
import scrapy, json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import CrawlerItem

# valid URI characters according to http://tools.ietf.org/html/rfc3986#section-2
# (ignoring question marks as they can only be used in the query and fragment,
# and single quotes as they cause more trouble than they are worth)
URI_CHARS = '\w\-.~:/#\[\]@!$&()*+,;='

class TopChinese(CrawlSpider):
	name = 'topchinese'
	with open('alexalist.json', 'r') as f: jsondata = json.load(f)
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
			for jsfile in sel.re('https?://['+URI_CHARS+']*\.js(?:\?['+URI_CHARS+'?]*)?'):
				i['scripts'].append(jsfile)
		if i['scripts']: yield i
