#!/usr/bin/env python3
import argparse, json, random, socket, ssl, time, os, statistics

NUM_FILES = 100
REPEAT_COUNT = 3
FILE_LIST = 'jsfiles.json'
BUFSIZE = 4096
STORAGE_DIR = 'timeouttestfiles'
RESULTS_FILE = 'timeouttest.json'
TTL = 64
CTX = ssl.create_default_context()

class URIError(Exception):
	"""Exception raised for a malformed URI.

	Attributes:
		numsegs -- the number of slash-delimited segments in the
			   malformed URI
	"""
	def __init__(self, numsegs):
		self.numsegs = numsegs

class ProtocolError(Exception):
	"""Exception raised when an unsupported protocol is used.

	Attributes:
		prtcl -- the unsupported protocol
	"""
	def __init__(self, prtcl):
		self.prtcl = prtcl

# Parse a JS file URI, and return whether TLS is used, the host, and the path to
# the JS file.
def parseURI(URI):
	splitURI = URI.split('/')
	if len(splitURI) < 4: raise URIError(len(splitURI))
	if splitURI[0] == 'https:': tls = True
	elif splitURI[0] == 'http:': tls = False
	else: raise ProtocolError(splitURI[0])
	host = splitURI[2]
	request = '/' + '/'.join(splitURI[3:])
	filename = splitURI[-1]
	return tls, host, request, filename

# Construct the HTTP GET request string.
def gen_message(host, request, referer):
	message = 'GET /' + request + ' HTTP/1.1\r\n'
	message += 'Host: ' + host + '\r\n'
	message += 'Connection: close\r\n'
	message += 'Cache-Control: max-age=0\r\n'
	message += 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4)'
	message += ' AppleWebKit/537.36 (KHTML, like Gecko) '
	message += 'Chrome/44.0.2403.125 Safari/537.36\r\n'
	message += 'Referer: ' + referer + '\r\n'
	message += 'Accept-Encoding: identity\r\n'
	message += 'Accept-Language: en-US,en;q=0.8\r\n\r\n'
	return message.encode('utf8')

# Issue the HTTP GET request repeatedly for a given referer and script,
# recording the amount of time it takes for each
def issue_requests(tls, host, message, ttl, filename):
	times = list()
	for i in range(REPEAT_COUNT):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if tls:
			s = CTX.wrap_socket(s, server_hostname=host)
			port = 443
		else:
			port = 80
		s.connect((host, port))
		s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
		s.send(message)
		full_response = b''
		time_before = time.time()
		while True:
			try:
				response = s.recv(args.bufsize)
				if response: full_response += response
				else: break
			except:
				break
		times.append(time.time() - time_before)
		if full_response:
			path = os.path.join(args.dir, host)
			if not os.path.isdir(path): os.makedirs(path)
			with open(os.path.join(path, str(i) + '_' + filename),
				  'wb') as f:
				f.write(full_response.split(b'\r\n')[-1])
	return times

parser = argparse.ArgumentParser(description='Test the time required to download each of several files.')
parser.add_argument('-n', '--numfiles', default=NUM_FILES, type=int, help='the number of files to download')
parser.add_argument('-r', '--repeat', default=REPEAT_COUNT, type=int, help='the number of times to download each file')
parser.add_argument('-f', '--filelist', default=FILE_LIST, type=str, help='the path to the file containing the list of candidate files to be downloaded')
parser.add_argument('-b', '--bufsize', default=BUFSIZE, type=int, help='the size in bytes of the buffer to receive HTTP responses')
parser.add_argument('-d', '--dir', default=STORAGE_DIR, type=str, help='the path at which to store the downloaded files')
args = parser.parse_args()

distance_table = dict() #number of hops to each host
with open('jsfiles.json') as infile: jsondata = json.load(infile)
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

download_times = dict()
flattened_times = list()
for f in download_files[0:1]:
	try:
		tls, host, request, filename = parseURI(f)
	except URIError as e:
		print('The URI ' + f + ' is malformed. ' + \
		      'There should be at least 4 slash-delimited ' + \
		      'segments, but there are only ' + str(e.numsegs))
		continue
	except ProtocolError as e:
		print('Protocol ' + e.prtcl + \
			' is not allowed. Skipping file: ' + f)
		continue
	message = gen_message(host, request, referer['referer'])
	print('Requesting ' + f + ' ' + str(args.repeat) \
	      + ' times, referred by ' + referer['referer'] + \
	      ', with TTL=' + str(TTL))
	download_times[f] = issue_requests(tls, host, message, TTL, filename)
	print(f, download_times[f])
	flattened_times += download_times[f]
print('Mean:', statistics.mean(flattened_times))
print('Median:', statistics.median(flattened_times))
try: print('Mode:', statistics.mode(flattened_times))
except statistics.StatisticsError as e: print('Mode: ', e)
print('Standard Deviation:', statistics.stdev(flattened_times))
print('Minimum:', min(flattened_times))
print('Maximum:', max(flattened_times))
with open(RESULTS_FILE, 'w') as outfile: json.dump(download_times, outfile)
