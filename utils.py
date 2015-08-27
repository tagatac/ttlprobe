# utils.py - various utilities useful for the TTL probe
import ssl, subprocess, socket, time, os, dns.resolver, scapy.all as scapy

DNS_SERVERS = ['114.112.79.22', '118.194.196.109']
TRACEROUTE_MAX = 35
TRACEROUTE_COUNT = 2
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
	def __init__(self, URI='', numsegs='fewer'):
		self.URI = URI
		self.numsegs = numsegs
	def __str__(self):
		err_msg = 'The URI ' + self.URI + ' is malformed. There should '
		err_msg += 'be at least 4 slash-delimited segments, but there '
		err_msg += 'are ' + str(self.numsegs) + '.'
		return err_msg

class ProtocolError(TTLProbeError):
	"""Exception raised when an unsupported protocol is used.

	Attributes:
		prtcl -- the unsupported protocol
	"""
	def __init__(self, URI='', prtcl=''):
		self.URI = URI
		self.prtcl = prtcl
	def __str__(self):
		err_msg = 'Protocol ' + self.prtcl + ' is not allowed. ('
		err_msg += self.URI + ')'
		return err_msg

# Parse a JS file URI, and return whether TLS is used, the host, and the path to
# the JS file.
def parseURI(URI):
	splitURI = URI.split('/')
	if len(splitURI) < 4: raise URIError(URI, len(splitURI))
	if splitURI[0] == 'https:':
		tls = True
		port = 443
	elif splitURI[0] == 'http:':
		tls = False
		port = 80
	else: raise ProtocolError(URI, splitURI[0])
	authority = splitURI[2]
	host = authority
	if ':' in authority:
		split_authority = authority.split(':')
		if len(split_authority) > 1:
			host, port = split_authority[0], split_authority[1]
		elif split_authority:
			host = split_authority[0]
	request = '/' + '/'.join(splitURI[3:])
	filename = splitURI[-1]
	return tls, host, port, request, filename

# Return the first 'A' record for the given name (using DNS_SERVERS as
# nameservers)
def name_to_address(name):
	resolver = dns.resolver.Resolver()
	resolver.nameservers = DNS_SERVERS
	try:
		answer = resolver.query(name, 'A')
	except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as e:
		print('Unable to resolve the name \'' + name + '\'')
		return None
	return str(answer[0])

# Perform a TCP traceroute to the host, and return the number of hops required.
def traceroute(host, port):
	ans, unans = scapy.traceroute(host, maxttl=TRACEROUTE_MAX, dport=port,
				      verbose=0)
	for snd,rcv in sorted(ans, key=lambda exchange: exchange[0].ttl):
		if isinstance(rcv.payload, scapy.TCP): return snd.ttl
	return None

# Run traceroute TRACEROUTE_COUNT times in case it fails the first
# (TRACEROUTE_COUNT - 1) times
def rerun_traceroute(host, port):
	results = list()
	for i in range(TRACEROUTE_COUNT):
		result = traceroute(host, port)
		if result and result < TRACEROUTE_MAX: results.append(result)
	if results: return min(results)

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

def save_file(directory, host, filename, contents, counter=None):
	path = os.path.join(directory, host)
	if counter: filename = str(counter) + '_' + filename
	if not os.path.isdir(path): os.makedirs(path)
	with open(os.path.join(path, filename), 'wb') as f:
		f.write(contents)
