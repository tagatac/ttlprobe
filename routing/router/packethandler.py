#!/usr/bin/env python
from netfilterqueue import NetfilterQueue
import time, sys, scapy.all as scapy

def drop_and_reply(pkt):
	print('hit!')
	pkt.drop()
	request = scapy.IP(pkt.get_payload())
	request_tcp = request.payload
	with open('adpubs.load', 'rb') as f:
		response_load = f.read()
	response_load = response_load.replace(b'TIMESTRING',
		time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime()))
	response_tcp = scapy.TCP()/response_load
	response_tcp.sport = 'http'
	response_tcp.dport = request_tcp.sport
	response = scapy.IP()/response_tcp
	response.src = '117.79.133.119'
	response.dst = '192.168.29.49'
	scapy.send(response, iface='eth0')

nfqueue = NetfilterQueue()
nfqueue.bind(1, drop_and_reply)
try: nfqueue.run()
except KeyboardInterrupt: print()
