# topchinese.py - Crawler to find JavaScript file URIs on the top Chinese sites.
import scrapy, json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import CrawlerItem

SITES_FILE = 'alexalist.json'
# valid URI characters according to http://tools.ietf.org/html/rfc3986#section-2
# (ignoring question marks as they can only be used in the query and fragment,
# and single quotes as they cause more trouble than they are worth)
URI_CHARS = '\w\-.~:/#\[\]@!$&()*+,;='

class TopChinese(CrawlSpider):
	name = 'topchinese'
	with open(SITES_FILE, 'r') as f: jsondata = json.load(f)
	allowed_domains = list()
	for page in jsondata:
		allowed_domains += map(lambda site: site.lower(), page['sites'])
	start_urls = list('http://www.' + domain.lower() for domain in allowed_domains)
	custom_settings = {
		# only crawl the homepages
		'DEPTH_LIMIT': 1,
		## crawl in BFO
		#'DEPTH_PRIORITY': 1,
		#'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
		#'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
		## use a persistent job queue on disk
		#'JOBDIR': name + 'state'
	}

	rules = (Rule(LinkExtractor(allow_domains=allowed_domains),
				    callback='parse_item', follow=True),)

	def parse_item(self, response):
		i = CrawlerItem()
		i['referer'] = response.url.encode('utf8')
		i['scripts'] = list()
		for sel in response.xpath('//script'):
			for jsfile in sel.re('https?://['+URI_CHARS+']*\.js(?:\?['+URI_CHARS+'?]*)?'):
				i['scripts'].append(jsfile.encode('utf8'))
		if i['scripts']: yield i
