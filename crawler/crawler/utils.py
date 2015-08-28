from crawler.items import CrawlerItem
# valid URI characters according to http://tools.ietf.org/html/rfc3986#section-2
# (ignoring question marks as they can only be used in the query and fragment,
# and single quotes as they cause more trouble than they are worth)
URI_CHARS = '\w\-.~:/#\[\]@!$&()*+,;='
# regex matching JS file URIs
URI_REGEX = 'https?://['+URI_CHARS+']*\.js(?:\?['+URI_CHARS+'?]*)?'

# generic parsing function - uses a regex to extract JS file URIs from a
# response
def URIparse(self, response):
	i = CrawlerItem()
	i['referer'] = response.url.encode('utf8')
	i['scripts'] = list()
	for sel in response.xpath('//script'):
		for jsfile in sel.re(URI_REGEX):
			if jsfile not in i['scripts']:
				i['scripts'].append(jsfile.encode('utf8'))
	if i['scripts']: yield i
