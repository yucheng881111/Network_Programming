from socket import *
import os
from _thread import *
from select import select
import random
from threading import Lock
import datetime
import sys

ServerSocket_tcp = socket(AF_INET, SOCK_STREAM)
host = '127.0.0.1'
port = int(sys.argv[1])
ThreadCount = 0

ServerSocket_tcp.bind((host, port))

print('Waiting for Connection...')
ServerSocket_tcp.listen(15)

account_info = []
board = []
post = []
sn = [1]

def threaded_client(connection_tcp, address, account_info, board, post, sn):
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
           
            for m in account_info:
                if usernum in m[3]:
                    reply = 'Bye, '+m[0]+'.'
                    break
            connection_tcp.send(str.encode(reply))
            
        elif data_li[0] == 'list-user':
            # print info in shared memory
            reply = 'Name     Email\n'
            for info in account_info:
                reply += (info[0]+'     '+info[1]+'\n')
            connection_tcp.send(str.encode(reply))
                    
        elif data_li[0] == 'exit':
            usernum = int(data_li[1])
            # find number in shared memory, then erase it
            for m in account_info:
                if usernum in m[3]:
                    break
            break   
        # hw2
        elif data_li[0] == 'create-board':
            board_name,usernum = data_li[1],int(data_li[2])
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
            
            reply = 'Index Name     Moderator\n'
            idx=1
            for b in board:
                reply += (str(idx)+'     '+b[0]+'  '+b[1]+'\n')
                idx+=1
            connection_tcp.send(str.encode(reply))
     
        elif data_li[0] == 'list-post':
            board_name = data_li[1]
           
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
            
            for i in account_info:
                if usernum in i[3]:
                    connection_tcp.send(str.encode(i[0]))
                    break

    connection_tcp.close()

while True:
    Client, address = ServerSocket_tcp.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address, account_info, board, post, sn ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))






















