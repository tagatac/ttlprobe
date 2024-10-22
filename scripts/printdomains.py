#!/usr/bin/env python3
import os, sys, json, operator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
					     os.path.pardir)))
from utils import *
if len(sys.argv) < 2:
	print('Usage: printdomains <jsonfile>')
	sys.exit(1)
with open(sys.argv[1]) as f: jsondata = json.load(f)
domain_counts = dict()
for referer in jsondata:
	for script in referer['scripts']:
		try: tls, domain, request, filename = parseURI(script)
		except: continue
		if domain in domain_counts: domain_counts[domain] += 1
		else: domain_counts[domain] = 1
for domain in sorted(domain_counts.items(), key=operator.itemgetter(1),
		     reverse=True):
	print(domain[0]+':', domain[1])
