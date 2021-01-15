from socket import *
import sys
import select

udp = socket(AF_INET, SOCK_DGRAM)
host = sys.argv[1]
port = int(sys.argv[2])


while(True):
	Input = input('# ')
	if Input == 'exit':
		break
	elif Input == 'get-file-list':
		udp.sendto(str.encode(Input),(host, port))
		Response,addr = udp.recvfrom(8192)
		print(Response.decode('utf-8'))
	else:
		udp.sendto(str.encode(Input),(host, port))
		for i in range(len(Input.split())-1):
			Response,addr = udp.recvfrom(8192)
			print(Response.decode('utf-8'))
			print('---------------------------------------------------')	

udp.close()





