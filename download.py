#!/usr/bin/env python

import httplib, urllib2, json

# adapted from http://stackoverflow.com/a/17882197
class HTTPHandler(urllib2.AbstractHTTPHandler):
	def http_open(self, req):
		return self.do_open(httplib.HTTPConnection, req)
	http_request = urllib2.AbstractHTTPHandler.do_request_

class LowLevelHTTPConnection(httplib.HTTPConnection):
	def connect(self):
		httplib.HTTPConnection.connect(self)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_TTL, 3)

class LowLevelHTTPHandler(HTTPHandler):
	def http_open(self, req):
		return self.do_open(LowLevelHTTPConnection, req)

urllib2.install_opener(urllib2.build_opener(LowLevelHTTPHandler))

with open('jsfiles.json', 'r') as fp:
	jsondata = json.load(fp)

for i in range(1):
	req = urllib2.Request('http://hm.baidu.com/h.js?4f1beaf39805550dd06b5cac412cd19b')
	req.add_header('Referer', 'http://www.7k7k.com/')
	r = urllib2.urlopen(req)
	#f = open('h' + str(i) + '.js', 'w')
	#f.write(r.read())
	#f.close()
	#if i % 10 == 0: print i
