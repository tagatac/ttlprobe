#!/usr/bin/env python3
import sys, json
if len(sys.argv) < 2:
	print('Usage: printscripts <jsonfile>')
	sys.exit(1)
with open(sys.argv[1]) as f: jsondata = json.load(f)
scripts = set()
for referer in jsondata:
	for script in referer['scripts']: scripts.add(script)
for script in scripts:
	print(script)