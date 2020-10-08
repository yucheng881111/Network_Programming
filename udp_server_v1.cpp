#include<bits/stdc++.h>
#include<stdlib.h>
#include<stdio.h>
#include<unistd.h>
#include<string.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<netinet/in.h>

using namespace std;

int main(int argc,char *argv[]){
	int sockfd;
	char buffer[1024];
	char message[]={"Hello from server\n"};
	struct sockaddr_in serverAddr,clientAddr;

	if((sockfd = socket(AF_INET,SOCK_DGRAM,0))<0){
		cout<<"socket creation failed"<<endl;
		return 0;
	}

	memset(&serverAddr,0,sizeof(serverAddr));
	memset(&clientAddr,0,sizeof(clientAddr));

	serverAddr.sin_family = AF_INET;
	serverAddr.sin_addr.s_addr = INADDR_ANY;
	serverAddr.sin_port = htons(8888);

	if(bind(sockfd,(const struct sockaddr *)&serverAddr,sizeof(serverAddr))<0){
		cout<<"bind failed"<<endl;
		return 0;
	}
	
	puts("Waiting for connection ...");
	
	int len = sizeof(clientAddr);
	int n = recvfrom(sockfd,(char *)buffer,1024,MSG_WAITALL,(struct sockaddr *)&clientAddr,(socklen_t *)&len);
        buffer[n] = '\0';
        cout<<"Client: "<<buffer<<endl;
	sendto(sockfd,(const char *)message,strlen(message),MSG_CONFIRM,(const struct sockaddr *)&clientAddr,len);
        cout<<"Hello message sent."<<endl;

	while(1){	
		n = recvfrom(sockfd,(char *)buffer,1024,MSG_WAITALL,(struct sockaddr *)&clientAddr,(socklen_t *)&len);
		buffer[n] = '\0';
		cout<<"Client: "<<buffer<<endl;
		sendto(sockfd,(const char *)buffer,strlen(buffer),MSG_CONFIRM,(const struct sockaddr *)&clientAddr,len);
		cout<<"Response message sent."<<endl;
	}


return 0;

}

