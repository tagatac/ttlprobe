#!/usr/bin/env python3
"""
Make a histogram of the difference between the traceroute result and the TTL
value required to request each file.
"""
import json, sys
import matplotlib as mpl
import matplotlib.pyplot as plt

if len(sys.argv) < 3:
	print('Usage: gen_figs.py')
	sys.exit()
results_file = sys.argv[1]
plot_file = sys.argv[2]

with open(results_file) as f: jsondata = json.load(f)
x = list()
for script in jsondata:
	if script['downloaded'] == True: x.append(script['earlyby'])

font = {'size':16}
mpl.rc('font', **font)
bins = max(x) - min(x) + 1
histrange = (min(x) - 0.5, max(x) + 0.5)
plt.hist(x, bins, range=histrange, log=True)
plt.xlabel('Difference Between the traceroute result and\nthe TTL Value Required to Request the File (# of hops)')
plt.ylabel('Frequency (count)')
plt.savefig(plot_file, bbox_inches='tight', format='png')
