#include<stdio.h>
#include<stdlib.h>
#include<sys/socket.h>
#include<string.h>
#include<unistd.h>
#include<sys/types.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<bits/stdc++.h>

using namespace std;

int main(int argc,char *argv[]){	
	
	int sockfd=0;
	sockfd = socket(AF_INET,SOCK_STREAM,0);
	if(sockfd==-1){
		cout<<"Fail to make socket."<<endl;
	}

	struct sockaddr_in Info;
	bzero(&Info,sizeof(Info));
	Info.sin_family = PF_INET;
	
	Info.sin_addr.s_addr = inet_addr("127.0.0.1");
	Info.sin_port = htons(8700);

	int err = connect(sockfd,(struct sockaddr *)&Info,sizeof(Info));
	if(err==-1){
		cout<<"Connection error"<<endl;
		return 0;
	}

	
	while(1){
		char receiveMessage[100]={};
		recv(sockfd,receiveMessage,sizeof(receiveMessage),0);
                cout<<receiveMessage<<endl;
		cout<<"% ";
		char message[100];
       		scanf("%s",message);
        	int check = send(sockfd,message,sizeof(message),0);
		if(check==-1){
			cout<<"Sending failed."<<endl;
			cout<<"close socket!!"<<endl;
       			close(sockfd);
			break;
		}
		//recv(sockfd,receiveMessage,sizeof(receiveMessage),0);
		//cout<<receiveMessage<<endl;
	}


return 0;

}



