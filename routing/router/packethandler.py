#!/usr/bin/env python
from netfilterqueue import NetfilterQueue
import binascii

def modify_and_accept(pkt):
	print('hit!')
	print(pkt.get_payload())
	print(binascii.hexlify(pkt.get_payload()))
	with open('adpub.pcap', 'rb') as f: pkt.set_payload(f.read())
	pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, modify_and_accept)
try: nfqueue.run()
except KeyboardInterrupt: print()
