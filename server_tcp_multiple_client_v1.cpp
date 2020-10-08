#include<stdio.h>
#include<stdlib.h>
#include<sys/socket.h>
#include<string.h>
#include<unistd.h>
#include<sys/types.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<bits/stdc++.h>
#include<sys/time.h>

using namespace std;

int main(int argc,char *argv[]){

	char inputBuffer[256] = {};
	char message[] = {"Hi,this is server.\n"};

	int sockfd=0,forClientSockfd=0;
	sockfd = socket(AF_INET,SOCK_STREAM,0);
	int new_socket,client_socket[20],max_client=20,activity,valread,sd;
	int max_sd;
	fd_set readfds;

	if(sockfd==-1){
		cout<<"Fail to make socket."<<endl;
	}
	
	for(int i=0;i<max_client;++i){
		client_socket[i]=0;
	}
		
	struct sockaddr_in serverInfo;
	int addrlen = sizeof(serverInfo);
	bzero(&serverInfo,sizeof(serverInfo));
	
	serverInfo.sin_family = PF_INET;
	serverInfo.sin_addr.s_addr = INADDR_ANY;
	serverInfo.sin_port = htons(8700);
	bind(sockfd,(struct sockaddr *)&serverInfo,sizeof(serverInfo));
	listen(sockfd,5);
	
	puts("Waiting for connections ...");

	while(1){
		FD_ZERO(&readfds);
		FD_SET(sockfd,&readfds);
		max_sd=sockfd;

		for(int i=0;i<max_client;++i){
			sd=client_socket[i];
			if(sd>0){
				FD_SET(sd,&readfds);
			}
			if(sd>max_sd){
				max_sd=sd;
			}
		}
		activity = select(max_sd+1,&readfds,NULL,NULL,NULL);
		if(activity<0){
			cout<<"select error!"<<endl;
		}

		if(FD_ISSET(sockfd,&readfds)){
			new_socket = accept(sockfd,(struct sockaddr*)&serverInfo,(socklen_t*)&addrlen);
			cout<<"New connection, socket fd is "<<new_socket<<", ip is: "<<inet_ntoa(serverInfo.sin_addr)<<", port: "<<ntohs(serverInfo.sin_port)<<endl;
			send(new_socket,message,strlen(message),0);
			puts("welcome message sent.");

			for(int i=0;i<max_client;++i){
				if(client_socket[i]==0){
					client_socket[i]=new_socket;
					cout<<"Adding to list of sockets as "<<i<<endl;
					break;
				}
			}		

		}
		for(int i=0;i<max_client;++i){
			sd = client_socket[i];
			if(FD_ISSET(sd,&readfds)){
				if((valread=read(sd,inputBuffer,256))==0){
					getpeername(sd,(struct sockaddr*)&serverInfo,(socklen_t*)&addrlen);
					cout<<"Host disconnected, ip "<<inet_ntoa(serverInfo.sin_addr)<<", port "<<ntohs(serverInfo.sin_port)<<endl;
					close(sd);
					client_socket[i]=0;
				}else{
					inputBuffer[valread]='\0';
					send(sd,inputBuffer,strlen(inputBuffer),0);
					cout<<"Get from client socket "<<sd<<". Message: "<<inputBuffer<<endl;

				}
			}	
		}
		
	}
	

return 0;

}



