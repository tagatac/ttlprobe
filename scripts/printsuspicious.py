#!/usr/bin/env python3
import sys, json
if len(sys.argv) < 3:
	print('Usage: printsuspicious <jsonfile> <suspicion threshold>')
	sys.exit(1)
with open(sys.argv[1]) as f: jsondata = json.load(f)
threshold = int(sys.argv[2])
for entry in jsondata:
	if 'earlyby' not in entry and entry['traceroute'] and 'traceroutefailed' not in entry:
		entry['earlyby'] = entry['traceroute'] - entry['ttlrequired']
	if 'earlyby' in entry and entry['earlyby'] > threshold: print(entry)
