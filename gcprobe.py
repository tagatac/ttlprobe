#!/usr/bin/env python3
import socket, select, argparse, os, sys, json
from utils import *

REPEAT_COUNT = 5
FILE_LIST = 'jsfiles.json'
STORAGE_DIR = 'gcprobefiles'
RESULTS_FILE = 'gcprobe.json'
TIMEOUT = 6.318 #seconds

# Issue the HTTP GET request repeatedly for a given referer, script, and ttl
# value, recording the amount of time it takes for each
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
	while True:
		ready = select.select([s], [], [], TIMEOUT)
		if ready[0]:
			response = s.recv(BUFSIZE)
			if response: full_response += response
			else: break
		else:
			break
	s.close()
	return full_response

# commandline argument parser
parser = argparse.ArgumentParser(description='Determine the smallest TTL required to download various JS files from China.')
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
with open('jsfiles.json') as f: jsondata = json.load(f)

# parse the URIs, generate the request messages, and issue the requests
distance_table = dict() #number of hops to each host
with open(args.outfile, 'w') as f: f.write('[')
for referer in jsondata:
	for script in referer['scripts']:
		result = dict()
		result['referer'] = referer['referer']
		result['script'] = script
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
		message = gen_message(host, request, referer['referer'])
		print('Probing for ' + script + ', referred by ' +
		      referer['referer'])
		sys.stdout.flush()
		if host not in distance_table:
			distance_table[host] = traceroute(host)
		result['traceroute'] = distance_table[host]
		upperbound = distance_table[host] + 3
		lowerbound = 0
		downloaded = False
		while lowerbound != upperbound:
			ttl = int((upperbound - lowerbound) / 2 + lowerbound)
			print(lowerbound, upperbound, ttl)
			downloaded_this_ttl = False
			for i in range(args.repeat):
				response = issue_request(host, message, tls,
							 ttl)
				if response:
					save_file(os.path.join(args.dir, 'ttl' +
							       str(ttl)),
						  host, filename, i,
						  response.split(b'\r\n')[-1])
					downloaded = downloaded_this_ttl = True
					if upperbound == ttl: upperbound -= 1
					else: upperbound = ttl
					break
			if not downloaded_this_ttl:
				if lowerbound == ttl: lowerbound += 1
				else: lowerbound = ttl + 1
		result['lowerbound'] = lowerbound
		result['downloaded'] = downloaded
		with open(args.outfile, 'a') as f:
			json.dump(result, f)
			f.write(',\n')
with open(args.outfile, 'a') as f: f.write(']')
