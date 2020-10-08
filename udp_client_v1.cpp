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
	char message[]={"Hello from client\n"};
	struct sockaddr_in serverAddr;

	if((sockfd = socket(AF_INET,SOCK_DGRAM,0))<0){
		cout<<"socket creation failed"<<endl;
		return 0;
	}

	memset(&serverAddr,0,sizeof(serverAddr));

	serverAddr.sin_family = AF_INET;
	serverAddr.sin_addr.s_addr = INADDR_ANY;
	serverAddr.sin_port = htons(8888);

	sendto(sockfd,(const char *)message,strlen(message),MSG_CONFIRM,(const struct sockaddr *)&serverAddr,sizeof(serverAddr));
	cout<<"hello sent."<<endl;
	int len;
        int n = recvfrom(sockfd,(char *)buffer,1024,MSG_WAITALL,(struct sockaddr *)&serverAddr,(socklen_t *)&len);
        buffer[n] = '\0';
        cout<<"Server: "<<buffer<<endl;
	
	while(1){
		char sendbuffer[256];
		cout<<"% ";
		scanf("%s",sendbuffer);
		sendto(sockfd,(const char *)sendbuffer,strlen(sendbuffer),MSG_CONFIRM,(const struct sockaddr *)&serverAddr,sizeof(serverAddr));	
		int len;
		int n = recvfrom(sockfd,(char *)buffer,1024,MSG_WAITALL,(struct sockaddr *)&serverAddr,(socklen_t *)&len);
		buffer[n] = '\0';
		cout<<"Server: "<<buffer<<endl;
	}

return 0;

}

