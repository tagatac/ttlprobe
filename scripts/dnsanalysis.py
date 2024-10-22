#!/usr/bin/env python3
import sys, json, subprocess

SCRAPYCOMMAND = "print(', '.join([response.xpath('//tr').re('<tr><th>City:</th><td>([\w ]*)</td></tr>')[0], response.xpath('//tr').re('<tr><th>Country:</th><td>([\w ]*) <img')[0]]))"

def get_location(address):
	response = subprocess.check_output(['scrapy', 'shell', '-c',
					    SCRAPYCOMMAND,
					    'http://whatismyipaddress.com/ip/'+address],
					   stderr=subprocess.DEVNULL)
	return response.decode('utf8').split('\n')[0]

def dig_baidu(dns):
	response = subprocess.check_output(['dig', '@'+dns, 'www.baidu.com',
					    '+noall', '+answer'])
	return response.decode('utf8').split()[-1]

if len(sys.argv) < 2:
	print('Usage: dnsanalysis <jsonfile>')
	sys.exit(1)
with open(sys.argv[1]) as f: jsondata = json.load(f)
for server in jsondata:
	print(server+'\n===============')
	try: location = get_location(server)
	except Exception as e: location = 'Rate limit exceeded :('
	print('Location:', location)
	baidu = dig_baidu(server)
	try: location = get_location(baidu)
	except Exception as e: location = 'Rate limit exceeded :('
	print('Baidu ('+baidu+') Location:', location)
	print()
