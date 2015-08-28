# homepages.py - Crawler to find JavaScript file URIs on the homepages of the
# top Chinese sites (according to Alexa)
import scrapy, json, crawler.utils

SITES_FILE = 'alexalist.json'
# valid URI characters according to http://tools.ietf.org/html/rfc3986#section-2
# (ignoring question marks as they can only be used in the query and fragment,
# and single quotes as they cause more trouble than they are worth)
URI_CHARS = '\w\-.~:/#\[\]@!$&()*+,;='

class HomepagesSpider(scrapy.Spider):
	name = "homepages"
	with open(SITES_FILE, 'r') as f: jsondata = json.load(f)
	allowed_domains = list()
	for page in jsondata:
		allowed_domains += map(lambda site: site.lower(), page['sites'])
	start_urls = list('http://www.' + domain.lower() for domain in allowed_domains)

	parse = crawler.utils.URIparse
