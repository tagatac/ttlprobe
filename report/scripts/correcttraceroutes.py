#!/usr/bin/env python3
"""
Modify a GC probe JSON results file by rerunning tcptraceroute for cases where
the result was recorded as 30. (Must be run on the same system/configurations
as gcprobe.py.)
"""
import json, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
					     os.path.pardir, os.path.pardir)))
from utils import *

OLD_TRACEROUTE_MAX = 30

if len(sys.argv) < 2: print('Usage: correcttraceroutes.py <JSON results file>')
results_file = sys.argv[1]

with open(results_file) as f: jsondata = json.load(f)
problem_domains = dict()
for entry in jsondata:
	tls, host, request, filename = parseURI(entry['script'])
	if entry['traceroute'] in [None, TRACEROUTE_MAX, OLD_TRACEROUTE_MAX] and host not in problem_domains:
		problem_domains[host] = rerun_traceroute(host)
		print('New traceroute result for '+host+':', problem_domains[host])
	if host in problem_domains:
		if not problem_domains[host]:
			entry['traceroute'] = None
			entry['traceroutefailed'] = True
			entry.pop('earlyby', None)
		else:
			entry['traceroute'] = problem_domains[host]
			entry['earlyby'] = entry['traceroute'] - entry['ttlrequired']

with open(os.path.join(os.path.dirname(results_file), 'modified.json'), 'w') as f:
	json.dump(jsondata, f)
