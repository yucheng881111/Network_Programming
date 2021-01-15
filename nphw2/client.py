from socket import *
import sys

ClientSocket_tcp = socket(AF_INET, SOCK_STREAM)
host = sys.argv[1]
port = int(sys.argv[2])
number = 0

ClientSocket_tcp.connect((host, port))

Response = ClientSocket_tcp.recv(2048)
print(Response.decode('utf-8'))
print('********************************\n** Welcome to the BBS server. **\n********************************')

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
    else:
        print('Command not found.')

ClientSocket_tcp.close()






