#!/usr/bin/env python
import socket, subprocess, ssl, os, json, sys

BUFSIZE = 4096
CTX = ssl.create_default_context()
STORAGE_DIR = 'receivedfiles'
REPEAT_COUNT = 1000

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

# Perform a TCP traceroute to the host, and return the number of hops required.
def traceroute(host):
	traceroute_output = subprocess.check_output(['sudo', 'tcptraceroute',
						     host])
	return int(traceroute_output.split('\n')[-2].split()[0])

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
	return message

# Issue the HTTP GET request repeatedly for a given referer and script, saving
# the file if one is received (rare)
def issue_requests(tls, host, message, ttl, filename):
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
		full_response = ''
		while True:
			try:
				response = s.recv(BUFSIZE)
				if response: full_response += response
				else: break
			except:
				break
		if full_response:
			path = os.path.join(STORAGE_DIR, host)
			if not os.path.isdir(path): os.mkdirs(path)
			with open(os.path.join(path, str(i) + '_' + filename),
				  'w') as f:
				f.write(full_response.split('\r\n')[-1])

distance_table = dict() #number of hops to each host
with open('jsfiles.json') as f: jsondata = json.load(f)
for referer in jsondata:
	for script in referer['scripts']:
		try:
			tls, host, request, filename = parseURI(script)
		except URIError as e:
			print 'The URI ' + script + ' is malformed. ' + \
			      'There should be at least 4 slash-delimited ' + \
			      'segments, but there are only ' + str(e.numsegs)
			continue
		except ProtocolError as e:
			print 'Protocol ' + e.prtcl + \
				' is not allowed. Skipping file: ' + script
			continue
		if host not in distance_table:
			distance_table[host] = traceroute(host)
		ttl = distance_table[host] - 1
		message = gen_message(host, request, referer['referer'])
		print 'Requesting ' + script + ' ' + str(REPEAT_COUNT) \
		      + ' times, referred by ' + referer['referer'] + \
		      ', with TTL=' + str(ttl)
		sys.stdout.flush()
		issue_requests(tls, host, message, ttl, filename)
