#!/usr/bin/env python

import socket, subprocess, ssl

HOST = 'hm.baidu.com'
PORT = 80
MESSAGE = 'GET /h.js?4f1beaf39805550dd06b5cac412cd19b HTTP/1.1\r\n'
MESSAGE += 'Host: ' + HOST + '\r\n'
MESSAGE += 'Connection: keep-alive\r\n'
MESSAGE += 'Cache-Control: max-age=0\r\n'
MESSAGE += 'Accept */*\r\n'
MESSAGE += 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36\r\n'
MESSAGE += 'Referer: http://www.7k7k.com/\r\n'
MESSAGE += 'Accept-Encoding: gzip, deflate, sdch\r\n'
MESSAGE += 'Accept-Language: en-US,en;q=0.8\r\n\r\n'
BUFSIZE = 4096

traceroute = subprocess.check_output(['sudo', 'tcptraceroute', HOST])
numhops = int(traceroute.split('\n')[-2].split()[0])

ctx = ssl.create_default_context()
for i in range(1):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if tls:
		s = ctx.wrap_socket(s, server_hostname=HOST)
	elif ssl:
		s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_SSLv3)
	s.connect((IP, PORT))
	s.setsockopt(socket.SOL_IP, socket.IP_TTL, numhops-1)
	s.send(MESSAGE)
	s.recv(BUFSIZE)
