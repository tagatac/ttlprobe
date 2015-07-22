#!/usr/bin/env python

import socket, time

IP = '123.125.65.120'
PORT = 80
BUFFER_SIZE = 1024
MESSAGE = 'GET /?falun HTTP/1.1\r\nHost: www.google.com\r\n\r\n'

for ttl in range(0, 25):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IP, PORT))
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	s.send(MESSAGE)
	time.sleep(1)
