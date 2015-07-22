#!/usr/bin/env python

import urllib2

for i in range(1000):
	req = urllib2.Request('http://hm.baidu.com/h.js?4f1beaf39805550dd06b5cac412cd19b')
	req.add_header('Referer', 'http://www.7k7k.com/')
	r = urllib2.urlopen(req)
	f = open('h' + str(i) + '.js', 'w')
	f.write(r.read())
	f.close()
	if i % 10 == 0: print i
