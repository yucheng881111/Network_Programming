from socket import *
import os
from _thread import *
from select import select
import random
from threading import Lock

ServerSocket_tcp = socket(AF_INET, SOCK_STREAM)
ServerSocket_udp = socket(AF_INET, SOCK_DGRAM)
host = '127.0.0.1'
port = 1233
ThreadCount = 0

ServerSocket_tcp.bind((host, port))
ServerSocket_udp.bind((host, port))

print('Waiting for a Connection..')
ServerSocket_tcp.listen(15)

account_info = []
data_lock = Lock()

def threaded_client(connection_tcp, address, account_info):
    connection_tcp.send(str.encode('Welcome to the Server. '+address[0]+' : '+str(address[1])))
    s=[connection_tcp,ServerSocket_udp]
    while True:
        s_read, s_out, s_exc = select(s,[],[])
        for ss in s_read:
            if ss == connection_tcp:
                data = connection_tcp.recv(2048)
                if not data:
                    break
                data_recv = data.decode('utf-8')
                print("Recv TCP: %s" % data_recv)
                data_li = data_recv.split()
                reply = ''
                if data_li[0] == 'login':
                    user_login, passwd_login = data_li[1], data_li[2]
                    num = random.randint(1,2147483647)
                    # find user_login in shared memory
                    with data_lock:
                        success=False
                        for u in account_info:
                            if u[0] == user_login and u[2] == passwd_login:
                                reply = 'Welcome, '+u[0]+'. '+str(num)
                                u[3]+=(str(num)+' ')
                                success=True
                                break
                        if not success:
                            reply = 'Login failed. 0'                           
                            
                elif data_li[0] == 'logout':
                    usernum = data_li[1]
                    # find number in shared memory, then erase it
                    with data_lock:
                        for m in account_info:
                            if usernum in m[3].split():
                                reply = 'Bye, '+m[0]+'.'
                                break
                    
                elif data_li[0] == 'list-user':
                    # print info in shared memory
                    with data_lock:                 
                        reply = 'Name     Email\n'
                        for info in account_info:
                            reply += (info[0]+'     '+info[1]+'\n')
                            
                elif data_li[0] == 'exit':
                    usernum = data_li[1]
                    # find number in shared memory, then erase it
                    with data_lock:
                        for m in account_info:
                            if usernum in m[3].split():
                                break
                    break    
                
                connection_tcp.sendall(str.encode(reply))
            else:
                data,addr = ServerSocket_udp.recvfrom(2048)
                data_recv = data.decode('utf-8')
                print("Recv UDP: %s" % data_recv)
                data_li = data_recv.split()
                if data_li[0] == 'register':
                    username, email, password = data_li[1], data_li[2], data_li[3]
                    # put them in shared memory
                    with data_lock:
                        success=True
                        for n in account_info:
                            if n[0] == username:
                                ServerSocket_udp.sendto(str.encode("Username is already used."),(addr[0], addr[1]))
                                success=False
                                break
                        if success:    
                            account_info.append([username,email,password,''])
                            ServerSocket_udp.sendto(str.encode("Register successfully."),(addr[0], addr[1]))

                else: #whoami
                    usernum = data_li[1]
                    # find number in shared memory
                    with data_lock:
                        for i in account_info:
                            if usernum in i[3].split():
                                ServerSocket_udp.sendto(str.encode(i[0]),(addr[0], addr[1]))
                                break
    
    connection_tcp.close()

while True:
    Client, address = ServerSocket_tcp.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address, account_info ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()











