#!/usr/bin/env python3
import argparse, os, sys, json, random, statistics, socket
from utils import *

NUM_FILES = 100
REPEAT_COUNT = 3
FILE_LIST = 'jsfiles.json'
STORAGE_DIR = 'timeouttestfiles'
RESULTS_FILE = 'timeouttest.json'

# Issue the HTTP GET request repeatedly for a given referer and script,
# recording the amount of time it takes for each
def issue_request(host, message, tls=False, ttl=None):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if tls:
		s = SSL_CONTEXT.wrap_socket(s, server_hostname=host)
		port = 443
	else:
		port = 80
	try: s.connect((host, port))
	except: return None, None
	if ttl: s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	s.send(message)
	full_response = b''
	time_before = time.time()
	while True:
		try:
			response = s.recv(BUFSIZE)
			if response: full_response += response
			else: break
		except:
			break
	download_time = time.time() - time_before
	s.close()
	return full_response, download_time

# commandline argument parser
parser = argparse.ArgumentParser(description='Test the time required to download each of several files.')
parser.add_argument('-n', '--numfiles', default=NUM_FILES, type=int, help='the number of files to download')
parser.add_argument('-r', '--repeat', default=REPEAT_COUNT, type=int, help='the number of times to download each file')
parser.add_argument('-f', '--filelist', default=FILE_LIST, type=str, help='the path to the file containing the list of candidate files to be downloaded')
parser.add_argument('-d', '--dir', default=STORAGE_DIR, type=str, help='the path at which to store the downloaded files')
parser.add_argument('-o', '--outfile', default=RESULTS_FILE, type=str, help='the path of the file in which to store the results')
args = parser.parse_args()

# make sure the download folder and results file don't exist yet
if os.path.exists(args.dir):
	print('ERROR: Download directory ' + args.dir  + '  already exists')
	sys.exit()
if os.path.exists(args.outfile):
	print('ERROR: Outfile ' + args.outfile  + '  already exists')
	sys.exit()

# get the list of JS files
with open(args.filelist) as infile: jsondata = json.load(infile)

# select numfiles of them at random for downloading
files = list()
for referer in jsondata:
	for f in referer['scripts']:
		files.append(f)
download_files = list()
for i in range(args.numfiles):
	while True:
		next_file = files[random.randint(0, len(files)-1)]
		if next_file in download_files:
			continue
		else:
			download_files.append(next_file)
			break

# parse the URIs, generate the request messages, and issue the requests
all_times = dict()
flattened_times = list()
for f in download_files:
	try:
		tls, host, request, filename = parseURI(f)
	except URIError as e:
		print('The URI ' + f + ' is malformed. ' +
		      'There should be at least 4 slash-delimited ' +
		      'segments, but there are only ' + str(e.numsegs))
		continue
	except ProtocolError as e:
		print('Protocol ' + e.prtcl +
		      ' is not allowed. Skipping file: ' + f)
		continue
	message = gen_message(host, request, referer['referer'])
	print('Requesting ' + f + ' ' + str(args.repeat)
	      + ' times, referred by ' + referer['referer'])
	these_times = list()
	for i in range(args.repeat):
		response, download_time = issue_request(host, message, tls)
		if response:
			save_file(args.dir, host, filename, response, i)
			these_times.append(download_time)
	all_times[f] = these_times
	print(f, all_times[f])
	flattened_times += all_times[f]
with open(args.outfile, 'w') as outfile: json.dump(all_times, outfile)

# generate some statistics about the results
print('Mean:', statistics.mean(flattened_times))
print('Median:', statistics.median(flattened_times))
try: print('Mode:', statistics.mode(flattened_times))
except statistics.StatisticsError as e: print('Mode: ', e)
print('Standard Deviation:', statistics.stdev(flattened_times))
print('Minimum:', min(flattened_times))
print('Maximum:', max(flattened_times))
