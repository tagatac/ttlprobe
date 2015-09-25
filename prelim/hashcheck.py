#!/usr/bin/env python

import hashlib

HASHREF = "3e8ee05a04bf606ef4e430fa9c8d367d"

for i in range(1000):
	f = open('h' + str(i) + '.js', 'r')
	if hashlib.md5(f.read()).hexdigest() != HASHREF:
		print i
	f.close()
