# utils.py - various utilities useful for the TTL probe
import ssl, subprocess, socket, time, os

BUFSIZE = 4096
SSL_CONTEXT = ssl.create_default_context()

class TTLProbeError(Exception):
	"""Base class for TTL probe exceptions."""
	pass

class URIError(TTLProbeError):
	"""Exception raised for a malformed URI.

	Attributes:
		numsegs -- the number of slash-delimited segments in the
			   malformed URI
	"""
	def __init__(self, numsegs):
		self.numsegs = numsegs

class ProtocolError(TTLProbeError):
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
	port = None
	if ':' in host:
		split_host = host.split(':')
		if len(split_host) > 1: host, port = split_host[0], split_host[1]
	command = ['sudo', 'tcptraceroute', host]
	if port: command.append(port)
	try:
		traceroute_output = subprocess.check_output(command)
	except subprocess.CalledProcessError as e:
		print(e, '\nUnable to perform traceroute on', host)
		return None
	return int(traceroute_output.split(b'\n')[-2].split()[0])

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

def save_file(directory, host, filename, contents, counter=None):
	path = os.path.join(directory, host)
	if counter: filename = str(counter) + '_' + filename
	if not os.path.isdir(path): os.makedirs(path)
	with open(os.path.join(path, filename), 'wb') as f:
		f.write(contents)
