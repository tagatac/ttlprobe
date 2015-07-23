#!/usr/bin/env python

import socket, time, ssl

IP = '220.181.112.244'
PORT = 443
BUFFER_SIZE = 1024
MESSAGE = 'GET /?falun HTTP/1.1\r\nHost: www.google.com\r\n\r\n'

ctx = ssl.create_default_context()
for ttl in range(25):
	#s = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname='www.baidu.com')
	s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ssl_version=ssl.PROTOCOL_SSLv3)
	s.connect((IP, PORT))
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	s.send(MESSAGE)
	time.sleep(1)
