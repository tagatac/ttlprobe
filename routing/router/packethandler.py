#!/usr/bin/env python
from netfilterqueue import NetfilterQueue
import binascii

def print_and_accept(pkt):
	with open('packet.pcap', 'w') as f: f.write(binascii.hexlify(pkt.get_payload()))
	print(pkt.get_payload())
	pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, print_and_accept)
try: nfqueue.run()
except KeyboardInterrupt: print()
