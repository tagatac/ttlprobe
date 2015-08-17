#!/usr/bin/env python3
import socket, select, argparse, os, sys, json, concurrent.futures, urllib.parse
import threading, shutil
from utils import *

REPEAT_COUNT = 5
FILE_LIST = 'jsfiles.json'
STORAGE_DIR = 'gcprobefiles'
SUSPICIOUS_DIR = 'suspicious'
RESULTS_FILE = 'gcprobe.json'
TIMEOUT = 3 #seconds
MAX_WORKERS = 512 #ThreadPool size

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
	except: return None
	s.setblocking(False)
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

# Probe one domain ('domain'), identifying the minimum TTL required in the HTTP
# request to download each of the JS files from 'script_list', and writing the
# results to the results file
def probe_domain(domain, script_list, outfile_lock):
	distance = traceroute(domain)
	if distance == None: return
	for script_info in script_list:

		# setup
		result = dict()
		tls = script_info[0]
		protocol = {True: 'https://', False: 'http://'}[tls]
		host = script_info[1]
		request = script_info[2]
		filename = script_info[3]
		referer = script_info[4]
		script = urllib.parse.urljoin(protocol+host, request)
		result['script'] = script
		result['referer'] = referer
		result['traceroute'] = distance
		message = gen_message(host, request, referer)

		# do the probe (start with a range of possible TTL values from
		# lowerbound to upperbound; when the file is received, decrease
		# the upperbound; when it is not, increase the lowerbound; set
		# the TTL value in the middle of the range and repeat until the
		# range has size zero)
		print('Probing for ' + script + ', referred by ' + referer)
		sys.stdout.flush()
		upperbound = distance + 3
		lowerbound = 0
		downloaded = False
		while lowerbound != upperbound:
			ttl = int((upperbound - lowerbound) / 2 + lowerbound)
			print("%s\tlowerbound:%d\tupperbound:%d\tttl:%d" %
			      (script, lowerbound, upperbound, ttl))
			downloaded_this_ttl = False
			for i in range(args.repeat):
				response = issue_request(host, message, tls,
							 ttl)
				if response:
					# file received - save it
					save_file(args.dir, host, filename,
						  response)
					downloaded = downloaded_this_ttl = True
					if upperbound == ttl: upperbound -= 1
					else: upperbound = ttl
					break
			if not downloaded_this_ttl:
				if lowerbound == ttl: lowerbound += 1
				else: lowerbound = ttl + 1

		# record the result
		result['ttlrequired'] = lowerbound
		earlyby = distance - lowerbound
		result['earlyby'] = earlyby
		result['downloaded'] = downloaded
		with outfile_lock:
			with open(args.outfile, 'a') as f:
				json.dump(result, f)
				f.write(',\n')
		if earlyby > 3:
			# file received with a request sent 3 hops or more short
			# of the traceroute value - save it separately
			path = os.path.join(args.dir, SUSPICIOUS_DIR, host)
			if not os.path.isdir(path): os.makedirs(path)
			shutil.copy(os.path.join(args.dir, host, filename),
				    path)

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
with open(args.filelist) as f: jsondata = json.load(f)

# parse the URIs and refactor the list of JS files by domain
list_by_domain = dict()
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
		if not host in list_by_domain: list_by_domain[host] = list()
		list_by_domain[host].append((tls, host, request, filename,
					     referer['referer']))

# probe all of the JS files in domain-specific threads (concurrently by domain,
# serially by script)
with open(args.outfile, 'w') as f: f.write('[')
outfile_lock = threading.Lock()
futures = list()
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
	for domain in list_by_domain:
		futures.append(executor.submit(probe_domain, domain,
				    list_by_domain[domain], outfile_lock))
concurrent.futures.wait(futures)
with open(args.outfile, 'a') as f: f.write(']')
