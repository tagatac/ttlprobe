#!/usr/bin/env python3
"""
Modify a GC probe JSON results file by updating tcptraceroute (and earlyby)
results for cases where the original result was determined by hand to be too big
"""
import json, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
					     os.path.pardir, os.path.pardir)))
from utils import *

if len(sys.argv) < 4: print('Usage: correcttraceroutes.py <JSON results file> <domain> <new distance>')
results_file = sys.argv[1]
domain = sys.argv[2]
newdistance = int(sys.argv[3])

with open(results_file) as f: jsondata = json.load(f)
for entry in jsondata:
	tls, host, port, request, filename = parseURI(entry['script'])
	if host == domain:
		entry['traceroute'] = newdistance
		entry['earlyby'] = newdistance - entry['ttlrequired']

with open(os.path.join(os.path.dirname(results_file), 'modified.json'), 'w') as f:
	json.dump(jsondata, f, separators=(',\n', ': '))
