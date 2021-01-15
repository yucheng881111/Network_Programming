from socket import *
import sys
import select

ClientSocket_tcp = socket(AF_INET, SOCK_STREAM)
ClientSocket_udp = socket(AF_INET, SOCK_DGRAM)
host = sys.argv[1]
port = int(sys.argv[2])
number = 0
join = 0

ClientSocket_tcp.connect((host, port))

Response = ClientSocket_tcp.recv(2048).decode('utf-8')
print(Response)
Response = Response.split()
chatroom_port = 0
print('********************************\n** Welcome to the BBS server. **\n********************************')

chatroom_owner = 0

def chatroom(c_port):
    global chatroom_owner
    global join
    Chatroom_Socket = socket(AF_INET, SOCK_STREAM)
    Chatroom_Socket.connect((host, c_port))
    leave = False
    Chatroom_Socket.send(str.encode('first-conn '+str(number)))
    while True:
        if leave:
            break
        socket_list = [sys.stdin, Chatroom_Socket]
        read_sockets, write_socket, error_socket = select.select(socket_list,[],[])  
        for socks in read_sockets:  
            if socks == Chatroom_Socket:  
                message = socks.recv(2048).decode('utf-8')
                print(message)
                if 'the chatroom is close.' in message:
                    leave=True
                    break  
            else:  
                Input = input()
                if Input == 'leave-chatroom':
                    if (chatroom_owner == 1 and join==0):
                        Chatroom_Socket.send(str.encode(Input+' '+str(number)+' leave'))
                        chatroom_owner = 0
                    else:
                        Chatroom_Socket.send(str.encode(Input+' '+str(number)))
                        join=0
                    leave=True
                elif Input == 'detach' and chatroom_owner == 1:
                    Chatroom_Socket.send(str.encode('detach 1'))
                    leave=True
                else:
                    Chatroom_Socket.send(str.encode(Input+' '+str(number)))
                    
                
                
while True:
    Input = input('% ')
    li=Input.split()
    if li[0] == 'register':
        if len(li) != 4:
            print('Usage: register <username> <email> <password>')
            continue
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'whoami':
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'login':
        if len(li) != 3:
            print('Usage: login <username> <password>')
            continue
        if number != 0:
            print('Please logout first.')
            continue
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        Response = Response.decode('utf-8').split()
        number = int(Response[2])
        print(Response[0]+' '+Response[1])
    elif li[0] == 'logout':
        if number == 0:
            print('Please login first.')
            continue
        
        if chatroom_owner == 1:
            print('Please do "attach" and "leave-chatroom" first.')
            continue
        
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        number=0
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'exit':
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        break     
    elif li[0] == 'list-user':
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'create-board':
        if len(li)!=2:
            print('create-board <name>')
            continue
        if number == 0:
            print('Please login first.')
            continue                   
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'create-post':
        if '--title' not in li or '--content' not in li:
            print('create-post <board-name> --title <title> --content <content>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'list-board':
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'list-post':
        if len(li)!=2:
            print('list-post <board-name>')
            continue
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'read':
        if len(li)!=2:
            print('read <post-S/N>')
            continue
        if not(li[1].isdigit()):
            print('read <post-S/N>')
            continue 
        ClientSocket_tcp.send(str.encode(Input))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'delete-post':
        if len(li)!=2:
            print('delete-post <post-S/N>')
            continue
        if not(li[1].isdigit()):
            print('delete-post <post-S/N>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'update-post':
        if len(li)<4:
            print('update-post <post-S/N> --title/content <new>')
            continue
        if not(li[1].isdigit()) or not(li[2]=='--title' or li[2]=='--content'):
            print('update-post <post-S/N> --title/content <new>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'comment':
        if len(li)<3:
            print('comment <post-S/N> <comment>')
            continue
        if not(li[1].isdigit()):
            print('comment <post-S/N> <comment>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        print(Response.decode('utf-8'))
    #hw3
    elif li[0] == 'list-chatroom':
        if number == 0:
            print('Please login first.')
            continue
        ClientSocket_udp.sendto(str.encode(Input),(host, port))
        Response,addr = ClientSocket_udp.recvfrom(2048)
        print(Response.decode('utf-8'))
    elif li[0] == 'create-chatroom':
        if len(li)==1:
            print('create-chatroom <port>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        chatroom_port = int(li[1])
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048)
        res = Response.decode('utf-8')
        print(res)
        if res != 'User has already created the chatroom.':
            chatroom_owner = 1
            print('*************************\n** Welcome to the chatroom **\n*************************')
            chatroom(chatroom_port) 
            print('Welcome back to BBS.')
         
    elif li[0] == 'join-chatroom':
        if len(li)==1:
            print('join-chatroom <chatroom_name>')
            continue
        if number == 0:
            print('Please login first.')
            continue
        join=1
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048).decode('utf-8')
        if Response == 'The chatroom does not exist or the chatroom is close.':
            print(Response)
            continue
        print('*************************\n** Welcome to the chatroom **\n*************************')
        chatroom(int(Response.split()[-1]))
        print('Welcome back to BBS.')
        
    elif li[0] == 'attach':
        if number == 0:
            print('Please login first.')
            continue
        if chatroom_owner == 0:
            print('Please create-chatroom first.')
            continue
        print('*************************\n** Welcome to the chatroom **\n*************************')
        chatroom(chatroom_port)
        print('Welcome back to BBS.')
        
    elif li[0] == 'restart-chatroom':
        if number == 0:
            print('Please login first.')
            continue
        if chatroom_owner == 1:
            print('Your chatroom is still running.')
            continue
        ClientSocket_tcp.send(str.encode(Input+' '+str(number)))
        Response = ClientSocket_tcp.recv(2048).decode('utf-8')
        if Response == ' ':
            chatroom_owner = 1
            print('start to create chatroom...')
            print('*************************\n** Welcome to the chatroom **\n*************************')
            chatroom(chatroom_port)
            print('Welcome back to BBS.')
        else:
            print(Response)
    
    else:
        print('Command not found.')

ClientSocket_tcp.close()






