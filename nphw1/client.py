from socket import *
import sys

ClientSocket_tcp = socket(AF_INET, SOCK_STREAM)
ClientSocket_udp = socket(AF_INET, SOCK_DGRAM)
#host = sys.argv[1]
#port = sys.argv[2]
host = '127.0.0.1'
port = 1233
number = 0

try:
    ClientSocket_tcp.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket_tcp.recv(1024)
print(Response.decode('utf-8'))

while True:
    Input = input('% ')
    li=Input.split()
    if li[0] == 'register' or li[0] == 'whoami': #udp
        if li[0] == 'register':
            if len(li) != 4:
                print('Usage: register <username> <email> <password>')
                continue
        if li[0] == 'whoami':
            if number == 0:
                print('Please login first.')
                continue
            ClientSocket_udp.sendto(str.encode(Input+' '+str(number)),(host, port))
        else:
            ClientSocket_udp.sendto(str.encode(Input),(host, port))
        Response,addr = ClientSocket_udp.recvfrom(1024)
        print(Response.decode('utf-8'))
    else:    #tcp
        if li[0] == 'login':
            if len(li) != 3:
                print('Usage: login <username> <password>')
                continue
            if number != 0:
                print('Please logout first.')
                continue
        if li[0] == 'logout' and number == 0:
            print('Please login first.')
            continue

        if li[0] == 'exit':
            ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
            break
        elif li[0] == 'logout':
            ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
            number=0
            Response = ClientSocket_tcp.recv(1024)
            print(Response.decode('utf-8'))
        elif li[0] == 'login':
            ClientSocket_tcp.send(str.encode(Input))
            Response = ClientSocket_tcp.recv(1024)
            Response = Response.decode('utf-8').split()
            number = int(Response[2])
            print(Response[0]+' '+Response[1])
        else: #list-user
            ClientSocket_tcp.send(str.encode(Input))
            Response = ClientSocket_tcp.recv(1024)
            print(Response.decode('utf-8'))

ClientSocket_tcp.close()
ClientSocket_udp.close()


