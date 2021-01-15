from socket import *
import os
import sys

udp = socket(AF_INET, SOCK_DGRAM)
host = '127.0.0.1'
port = int(sys.argv[1])
udp.bind((host, port))


while(True):
	data,addr = udp.recvfrom(8192)
	data_recv = data.decode('utf-8').split()
	if data_recv[0] == 'get-file':
		for File in data_recv[1:]:
			print('transferring '+File)
			with open(File,'r') as f:
				lines = f.readlines()
			s=''
			for l in lines:
				s+=l
			udp.sendto(str.encode(s),(addr[0], addr[1]))
	else:
		print('getting file list')
		ls = os.listdir('.')
		s=''
		for l in ls:
			s+=(l+' ')
		udp.sendto(str.encode(s),(addr[0], addr[1]))
	



















