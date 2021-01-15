from socket import *
import os
from _thread import *
from select import select
import random
from threading import Lock
import datetime
import sys
from datetime import datetime
import traceback

def get_time():
    now = datetime.now()
    time = now.strftime("%-H:%M")
    return time

ServerSocket_tcp = socket(AF_INET, SOCK_STREAM)
ServerSocket_udp = socket(AF_INET, SOCK_DGRAM)
host = '127.0.0.1'
port = int(sys.argv[1])
ThreadCount = 0

ServerSocket_tcp.bind((host, port))
ServerSocket_udp.bind((host, port))

print('Waiting for Connection...')
ServerSocket_tcp.listen(15)

account_info = []
board = []
post = []
sn = [1]
chatroom = []
data_lock = Lock()

def chatroom_clientthread(server, conn, addr, list_of_clients, account_info, chatroom, chatroom_port):  
    thread_close = False
    while True:
        if thread_close == True:
            break
        read_sockets, write_sockets, error_sockets = select(list_of_clients,[],[])
        for sock in read_sockets:
            if sock == server:
                chat_conn, chat_addr = server.accept()
                list_of_clients.append(chat_conn)
                print (str(chat_addr[1]) + " connected.")
            else:
                try:
                    message = sock.recv(2048).decode('utf-8').split()
                    if message[0] == 'first-conn':
                        usernum = int(message[-1])
                        user=''
                        for n in account_info:
                            if usernum in n[3]:
                                user=n[0]
                                break
                        tmp=0
                        for i in range(len(chatroom)):
                            if chatroom[i][1]==chatroom_port:
                                tmp=i
                                break  
                        c=chatroom[tmp]
                        if len(c[3])<3:
                            for m in c[3]:
                                sock.send(str.encode(m+'\n'))
                        else:
                            sock.send(str.encode(c[3][-3]+'\n'))
                            sock.send(str.encode(c[3][-2]+'\n'))
                            sock.send(str.encode(c[3][-1]+'\n'))
                        if user != c[0]:
                            for clients in list_of_clients:  
                                if clients != sock and clients != server: 
                                    clients.send(str.encode('sys['+get_time()+']: ' +user+' join us.'))
                        continue
                    if message[0] == 'detach' and message[1] == '1':
                        list_of_clients.remove(sock)
                        continue
                    if message[0] == 'leave-chatroom' and message[-1] == 'leave':
                        print(str(message))
                        for clients in list_of_clients:  
                            if clients != sock and clients != server:
                                reply = 'sys['+get_time()+']: the chatroom is close.'
                                clients.send(str.encode(reply))
                        list_of_clients.clear()
                        usernum = int(message[-2])
                        user=''
                        for n in account_info:
                            if usernum in n[3]:
                                user=n[0]
                                break
                        for c in chatroom:
                            if c[0]==user:
                                c[2]='close'
                                break
                        thread_close=True
                        break
                    usernum = int(message[-1])
                    user=''
                    for n in account_info:
                        if usernum in n[3]:
                            user=n[0]
                            break
                    print("<" + user + ">: " + str(message))
                    message_to_send=''
                    if message[0] == 'leave-chatroom':
                        list_of_clients.remove(sock)
                        message_to_send = 'sys['+get_time()+']: '+user+' leave us.'
                    else:    
                        temp=''
                        for s in message[0:-1]:
                            temp+=(s+' ')
                        message_to_send =  user + '['+get_time()+']: ' + temp
                        chatroom[tmp][3].append(message_to_send)
                    for clients in list_of_clients:  
                        if clients != sock and clients != server:  
                            try:  
                                clients.send(str.encode(message_to_send))
                            except:
                                traceback.print_exc()
                                clients.close() 
                                list_of_clients.remove(clients)
                except Exception as e: 
                    traceback.print_exc()
                        
            

def threaded_client(connection_tcp, address, account_info, board, post, sn, c_port, chatroom):
    connection_tcp.send(str.encode('Welcome to the Server. '+address[0]+' : '+str(address[1])))
    while True:
        data = connection_tcp.recv(2048)
        if not data:
            break
        data_recv = data.decode('utf-8')
        print("Receive: %s" % data_recv)
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
                        u[3].append(num)
                        success=True
                        break
                if not success:
                    reply = 'Login failed. 0'  
                connection_tcp.send(str.encode(reply))                         
                    
        elif data_li[0] == 'logout':
            usernum = int(data_li[1])
            # find number in shared memory, then erase it
            with data_lock:
                for m in account_info:
                    if usernum in m[3]:
                        reply = 'Bye, '+m[0]+'.'
                        break
                connection_tcp.send(str.encode(reply))
            
        elif data_li[0] == 'list-user':
            # print info in shared memory
            with data_lock:                 
                reply = 'Name     Email\n'
                for info in account_info:
                    reply += (info[0]+'     '+info[1]+'\n')
                connection_tcp.send(str.encode(reply))
                    
        elif data_li[0] == 'exit':
            usernum = int(data_li[1])
            # find number in shared memory, then erase it
            with data_lock:
                for m in account_info:
                    if usernum in m[3]:
                        break
            break   
        # hw2
        elif data_li[0] == 'create-board':
            board_name,usernum = data_li[1],int(data_li[2])
            with data_lock:
                user=''
                success=True
                for n in account_info:
                    if usernum in n[3]:
                        user=n[0]
                        break
                for b in board:
                    if board_name == b[0]:
                        success=False
                        break
                if not success:
                    reply = 'Board already exists.'
                else:
                    reply = 'Create board successfully.'
                    board.append([board_name,user,[]])
                connection_tcp.send(str.encode(reply))
                
        elif data_li[0] == 'create-post':
            board_name,usernum = data_li[1],int(data_li[-1])
            title = ''
            content = ''
            for i in range(1,len(data_li)-1):
                if data_li[i] == '--title':
                    title_pos=i
                if data_li[i] == '--content':
                    content_pos=i
            for i in range(title_pos+1,content_pos):
                title += (data_li[i]+' ')
            for i in range(content_pos+1,len(data_li)-1):
                content += (data_li[i]+' ')
            
            with data_lock:
                user=''
                for n in account_info:
                    if usernum in n[3]:
                        user=n[0]
                        break
                success=False
                for b in board:
                    if board_name == b[0]:
                        success=True
                        break
                if not success:
                    reply = 'Board does not exist.'
                else:
                    reply = 'Create post successfully.'
                    date_tmp=str(datetime.date.today()).split('-')
                    date = date_tmp[1]+'/'+date_tmp[2]
                    post.append([sn[0],title,user,date,content,''])
                    for b in board:
                        if board_name == b[0]:
                            b[2].append(sn[0])
                            break
                    sn[0]+=1
                connection_tcp.send(str.encode(reply))
                
        elif data_li[0] == 'list-board':
            with data_lock:
                reply = 'Index Name     Moderator\n'
                idx=1
                for b in board:
                    reply += (str(idx)+'     '+b[0]+'  '+b[1]+'\n')
                    idx+=1
                connection_tcp.send(str.encode(reply))
     
        elif data_li[0] == 'list-post':
            board_name = data_li[1]
            with data_lock:
                success=False
                for b in board:
                    if board_name == b[0]:
                        post_li=b[2]
                        success=True
                        break
                if not success:
                    reply = 'Board does not exist.'
                else:
                    reply='S/N Title     Author     Date\n'
                    for p in post:
                        if p[0] in post_li:
                            reply += (str(p[0])+'   '+p[1]+'   '+p[2]+'   '+p[3]+'\n')
                connection_tcp.send(str.encode(reply))
        
        elif data_li[0] == 'read':
            post_sn = int(data_li[1])
            with data_lock:
                reply=''
                success=False
                for p in post:
                    if p[0] == post_sn:
                        reply += 'Author: '+p[2]+'\n'
                        reply += 'Title: '+p[1]+'\n'
                        reply += 'Date: '+p[3]+'\n'
                        reply += '--\n'
                        reply += p[4].replace('<br>','\n')
                        reply += '\n--\n'
                        reply += p[5]
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                connection_tcp.send(str.encode(reply))
        elif data_li[0] == 'delete-post':
            post_sn, usernum = int(data_li[1]), int(data_li[2])
            with data_lock:
                user=''
                for a in account_info:
                    if usernum in a[3]:
                        user=a[0]
                        break
                success=False
                for p in post:
                    if p[0] == post_sn:
                        if p[2] == user:
                            reply = 'Delete successfully.'
                            p[0]=0
                        else:
                            reply = 'Not the post owner.'
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                    
                connection_tcp.send(str.encode(reply))
         
        elif data_li[0] == 'update-post':
            post_sn, usernum = int(data_li[1]), int(data_li[-1])
            with data_lock:
                user=''
                for a in account_info:
                    if usernum in a[3]:
                        user=a[0]
                        break
                update=0
                if data_li[2] == '--content':
                    update=1
                
                update_info=''
                for i in range(3,len(data_li)-1):
                    update_info+=(data_li[i]+' ')
                success=False
                for p in post:
                    if p[0] == post_sn:
                        if p[2] == user:
                            reply = 'Update successfully.'
                            if update == 0: # title
                                p[1] = update_info
                            else: # content
                                p[4] = update_info
                        else:
                            reply = 'Not the post owner.'
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                    
                connection_tcp.send(str.encode(reply))
        
        elif data_li[0] == 'comment':
            post_sn, usernum = int(data_li[1]), int(data_li[-1])
            with data_lock:
                user=''
                for a in account_info:
                    if usernum in a[3]:
                        user=a[0]
                        break
                comment=''
                for i in range(2,len(data_li)-1):
                    comment+=(data_li[i]+' ')
                success=False
                for p in post:
                    if p[0] == post_sn:
                        reply = 'Comment successfully.'
                        p[5]+=(user+': '+comment+'\n') 
                        success=True
                        break
                if not success:
                    reply = 'Post does not exist.'
                connection_tcp.send(str.encode(reply))
        
        elif data_li[0] == 'register':
            username, email, password = data_li[1], data_li[2], data_li[3]
            # put them in shared memory
            with data_lock:
                success=True
                for n in account_info:
                    if n[0] == username:
                        reply = 'Username is already used.'
                        connection_tcp.send(str.encode(reply))
                        success=False
                        break
                if success:    
                    account_info.append([username,email,password,[]])
                    reply = 'Register successfully.'
                    connection_tcp.send(str.encode(reply))

        elif data_li[0] == 'whoami':
            usernum = int(data_li[1])
            # find number in shared memory
            with data_lock:
                for i in account_info:
                    if usernum in i[3]:
                        connection_tcp.send(str.encode(i[0]))
                        break
        #hw3
        elif data_li[0] == 'create-chatroom':
            with data_lock:    
                reply = 'start to create chatroom...'
                usernum, chatroom_port = int(data_li[2]), int(data_li[1])
                user=''
                for i in account_info:
                    if usernum in i[3]:
                        user=i[0]
                        break
                ok=True
                for c in chatroom:
                    if user == c[0]:
                        reply = 'User has already created the chatroom.'
                        ok=False
                        break
                connection_tcp.send(str.encode(reply))
                if ok:
                    chatroom.append([user,chatroom_port,'open',[]])
                    server = socket(AF_INET, SOCK_STREAM)
                    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                    server.bind((host, chatroom_port))
                    server.listen(10)
                    list_of_clients = []
                    list_of_clients.append(server)
                    conn, addr = server.accept()
                    list_of_clients.append(conn)
                    print (str(addr[1]) + " connected.")
                    start_new_thread(chatroom_clientthread, (server,conn,addr,list_of_clients,account_info,chatroom,chatroom_port))
                
        elif data_li[0] == 'join-chatroom':
            with data_lock:
                chatroom_name, usernum = data_li[1], int(data_li[2])
                reply = 'Action: connection to chatroom server.'
                p=''
                ok=False
                for c in chatroom:
                    if c[0] == chatroom_name and c[2] == 'open':
                        p=str(c[1])
                        ok=True
                        break
                if ok:
                    connection_tcp.send(str.encode(reply+' '+p))
                else:
                    reply = 'The chatroom does not exist or the chatroom is close.'
                    connection_tcp.send(str.encode(reply))
                
        elif data_li[0] == 'restart-chatroom':
            with data_lock:
                usernum = int(data_li[1])
                user=''
                for i in account_info:
                    if usernum in i[3]:
                        user=i[0]
                        break
                ok=False
                for c in chatroom:
                    if c[0] == user:
                        ok=True
                        c[2]='open'
                        chatroom_port=c[1]
                        break
                reply = ' '
                if not ok:
                    reply = 'Please create-chatroom first.'
                    connection_tcp.send(str.encode(reply))
                    continue
                
                server = socket(AF_INET, SOCK_STREAM)
                server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                server.bind((host, chatroom_port))
                server.listen(10)
                list_of_clients = []
                list_of_clients.append(server)
                connection_tcp.send(str.encode(reply))
                conn, addr = server.accept()
                list_of_clients.append(conn)
                print (str(addr[1]) + " connected.")
                start_new_thread(chatroom_clientthread, (server,conn,addr,list_of_clients,account_info,chatroom,chatroom_port))
    
    connection_tcp.close()

def threaded_client_udp(udp, chatroom): #list-chatroom    
    while True:
        data,addr = udp.recvfrom(2048)
        data_recv = data.decode('utf-8')
        print("Recv UDP: %s" % data_recv)
        reply=''
        with data_lock:
            for i in chatroom:
                reply+=(i[0]+'      ')
                reply+=i[2]
                reply+='\n'
            udp.sendto(str.encode("Chatroom_name    Status\n"+reply),(addr[0], addr[1]))

start_new_thread(threaded_client_udp, (ServerSocket_udp, chatroom))
while True:
    Client, address = ServerSocket_tcp.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address, account_info, board, post, sn, ThreadCount, chatroom))
    #start_new_thread(chatroom_server, (Client, address, ThreadCount, account_info, chatroom))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))









