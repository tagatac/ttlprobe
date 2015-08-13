#!/usr/bin/env python

import socket, time, argparse

parser = argparse.ArgumentParser(description='Probe the Great Firewall of China for keyword censorship.')
parser.add_argument('-t', '--tls', action='store_true', help='use the most modern encryption supported when conducting the probe')
parser.add_argument('-s', '--ssl', action='store_true', help='use SSLv3 when conducting the probe')
args = parser.parse_args()
encrypt = args.tls or args.ssl

if encrypt: import ssl
IP = '220.181.112.244'
PORT = 443 if encrypt else 80
MESSAGE = 'GET /?falun HTTP/1.1\r\nHost: www.google.com\r\n\r\n'

if args.tls: ctx = ssl.create_default_context()
for ttl in range(25):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if args.tls:
		s = ctx.wrap_socket(s, server_hostname='www.baidu.com')
	elif args.ssl:
		s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_SSLv3)
	s.connect((IP, PORT))
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	s.send(MESSAGE)
	time.sleep(1)
