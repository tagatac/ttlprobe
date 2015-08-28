# topchinese.py - Crawler to find JavaScript file URIs on the top Chinese sites.
import scrapy, json, crawler.utils
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

SITES_FILE = 'alexalist.json'

class TopChinese(CrawlSpider):
	name = 'topchinese'
	with open(SITES_FILE, 'r') as f: jsondata = json.load(f)
	allowed_domains = list()
	for page in jsondata:
		allowed_domains += map(lambda site: site.lower(), page['sites'])
	start_urls = list('http://www.' + domain.lower() for domain in allowed_domains)
	custom_settings = {
		# crawl in BFO
		'DEPTH_PRIORITY': 1,
		'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
		'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
		# use a persistent job queue on disk
		'JOBDIR': name + 'state'
	}

	rules = (Rule(LinkExtractor(allow_domains=allowed_domains),
				    callback='parse_start_url', follow=True),)

	parse_start_url = crawler.utils.URIparse
