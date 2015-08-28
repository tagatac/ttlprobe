#!/usr/bin/env python3
# rmdups - remove all of the duplicate script URIs from one file and write the
# non-duplicates out to another file
import sys, json
if len(sys.argv) < 3:
	print('Usage: rmdups <jsonfile> <outfile>')
	sys.exit(1)
with open(sys.argv[1]) as f: jsondata = json.load(f)
for referer in jsondata:
	referer['scripts'] = list(set(referer['scripts']))
with open(sys.argv[2], 'w') as f: json.dump(jsondata, f, separators=(',\n', ': '))
