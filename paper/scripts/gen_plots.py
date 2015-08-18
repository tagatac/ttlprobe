#!/usr/bin/env python3
"""
Make a histogram of the difference between the traceroute result and the TTL
value required to request each file.
"""
import json, sys
import matplotlib.pyplot as plt

with open('../results/best/gcprobe.json') as f: jsondata = json.load(f)
x = list()
for script in jsondata:
	if script['downloaded'] == True: x.append(script['earlyby'])
bins = max(x) - min(x) + 1
histrange = (min(x) - 0.5, max(x) + 0.5)
plt.hist(x, bins, range=histrange, log=True)
plt.xlabel('Difference Between the traceroute result and\nthe TTL Value Required to Request the File (# of hops)')
plt.ylabel('Frequency (count)')
plt.savefig('figures/gcprobe-histogram.png', bbox_inches='tight', format='png')
