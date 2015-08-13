#!/usr/bin/env python3
import argparse, os, sys, json
from utils import *

REPEAT_COUNT = 1000
FILE_LIST = 'jsfiles.json'
STORAGE_DIR = 'downloadfiles'

# commandline argument parser
parser = argparse.ArgumentParser(description='Determine the smallest TTL required to download various JS files from China.')
parser.add_argument('-r', '--repeat', default=REPEAT_COUNT, type=int, help='the number of times to download each file')
parser.add_argument('-f', '--filelist', default=FILE_LIST, type=str, help='the path to the file containing the list of candidate files to be downloaded')
parser.add_argument('-d', '--dir', default=STORAGE_DIR, type=str, help='the path at which to store the downloaded files')
#parser.add_argument('-o', '--outfile', default=RESULTS_FILE, type=str, help='the path of the file in which to store the results')
args = parser.parse_args()

# make sure the download folder and results file don't exist yet
if os.path.exists(args.dir):
	print('ERROR: Download directory ' + args.dir  + '  already exists')
	sys.exit()
#if os.path.exists(args.outfile):
#	print('ERROR: Outfile ' + args.outfile  + '  already exists')
#	sys.exit()

# get the list of JS files
with open('jsfiles.json') as f: jsondata = json.load(f)

# parse the URIs, generate the request messages, and issue the requests
distance_table = dict() #number of hops to each host
for referer in jsondata:
	for script in referer['scripts']:
		try:
			tls, host, request, filename = parseURI(script)
		except URIError as e:
			print('The URI ' + script + ' is malformed. ' +
			      'There should be at least 4 slash-delimited ' +
			      'segments, but there are only ' + str(e.numsegs))
			continue
		except ProtocolError as e:
			print('Protocol ' + e.prtcl +
			      ' is not allowed. Skipping file: ' + script)
			continue
		if host not in distance_table:
			distance_table[host] = traceroute(host)
		ttl = distance_table[host] - 1
		message = gen_message(host, request, referer['referer'])
		print('Requesting ' + script + ' ' + str(args.repeat)
		      + ' times, referred by ' + referer['referer'] +
		      ', with TTL=' + str(ttl))
		sys.stdout.flush()
		for i in range(args.repeat):
			response, dowload_time = issue_request(host, message,
							       tls, ttl)
			if response: save_file(args.dir, host, filename, i,
					       response.split(b'\r\n')[-1])
