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

class USER{
public:
	string username="";
	string email="";
	string passwd="";
	vector<int> number;
	USER(string s1,string s2,string s3){
		username=s1;
		email=s2;
		passwd=s3;
	}
};

int main(int argc,char *argv[]){

	stringstream stream_port;
	int port_num;
	stream_port<<argv[1];
	stream_port>>port_num;
	

	char inputBuffer[1000] = {};
	
	vector<USER> vec;

	int tcp_sockfd=0,udp_sockfd=0,maxfdp,nready;
	int new_socket,client_socket[15],max_client=15,activity,valread,sd;
	
	fd_set readfds;
	
	if((tcp_sockfd = socket(AF_INET,SOCK_STREAM,0))<0){
		cout<<"tcp socket fail"<<endl;
	}

	for(int i=0;i<max_client;++i){
		client_socket[i]=0;
	}

	struct sockaddr_in serverInfo,clientInfo;
	int addrlen = sizeof(serverInfo);
	bzero(&serverInfo,sizeof(serverInfo));
	bzero(&clientInfo,sizeof(clientInfo));

	serverInfo.sin_family = PF_INET;
	serverInfo.sin_addr.s_addr = INADDR_ANY;
	serverInfo.sin_port = htons(port_num);

	bind(tcp_sockfd,(struct sockaddr *)&serverInfo,sizeof(serverInfo));
	listen(tcp_sockfd,15);
	
	if((udp_sockfd = socket(AF_INET,SOCK_DGRAM,0))<0){
		cout<<"udp socket fail"<<endl;
		return 0;
	}

	if(bind(udp_sockfd,(const struct sockaddr *)&serverInfo,sizeof(serverInfo))<0){
		cout<<"udp bind failed"<<endl;
		return 0;
	}
	
	puts("Waiting for connections ...");


	FD_ZERO(&readfds);
	maxfdp=max(tcp_sockfd,udp_sockfd);

	while(1){
		FD_SET(tcp_sockfd, &readfds); 
	        FD_SET(udp_sockfd, &readfds);
		
		for(int i=0;i<max_client;++i){
			sd=client_socket[i];
			if(sd>0){
				FD_SET(sd,&readfds);
			}
			if(sd>maxfdp){
				maxfdp=sd;
			}
		}


		nready = select(maxfdp+1, &readfds, NULL, NULL, NULL);
		
		if(nready<0){
			cout<<"select error!"<<endl;
		}

		//TCP
		if(FD_ISSET(tcp_sockfd,&readfds)){
			new_socket = accept(tcp_sockfd,(struct sockaddr*)&serverInfo,(socklen_t*)&addrlen);
			cout<<"New connection."<<endl;
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
				if((valread=read(sd,inputBuffer,sizeof(inputBuffer)))==0){
					getpeername(sd,(struct sockaddr*)&serverInfo,(socklen_t*)&addrlen);
					cout<<"Host disconnected, ip "<<inet_ntoa(serverInfo.sin_addr)<<", port "<<ntohs(serverInfo.sin_port)<<endl;
					client_socket[i]=0;
				}else{
					inputBuffer[valread]='\0';
					cout<<"Get from TCP socket "<<sd<<". Message: "<<inputBuffer<<endl;
					
					stringstream ss(inputBuffer);
					string temp;
					ss>>temp;
					if(temp=="exit"){
						int n;
						ss>>n;
						for(int i=0;i<vec.size();++i){
							vector<int>::iterator it=find(vec[i].number.begin(),vec[i].number.end(),n);
							if(it!=vec[i].number.end()){
								(*it)=0;
							}
						}
					}else if(temp=="logout"){
						int n;
						ss>>n;
						const char fail[]="Please login first.";
						if(n==0){
							send(sd,fail,sizeof(fail),0);
						}else{
							string s="Bye, ";
							for(int i=0;i<vec.size();++i){
								vector<int>::iterator it=find(vec[i].number.begin(),vec[i].number.end(),n);
								if(it!=vec[i].number.end()){
									s+=vec[i].username;
									(*it)=0;
									break;
								}
							
							}
							s+=".";
							send(sd,(const char *)s.c_str(),sizeof(inputBuffer),0);
						}
						
					}else if(temp=="list-user"){
						string s="Name   Email\n";
						for(int i=0;i<vec.size();++i){
							if(i==vec.size()-1){
								s+=(vec[i].username+"   "+vec[i].email);
							}else{
								s+=(vec[i].username+"   "+vec[i].email+"\n");
							}
						}
						send(sd,(const char *)s.c_str(),sizeof(inputBuffer),0);
					}else{ //login
						string temp1,temp2;
						ss>>temp1>>temp2;
						int status;
						ss>>status;
						bool ok=false;
						const char fail1[]="Please logout first.";
						const char fail2[]="Login failed.";
						if(status!=0){
							send(sd,fail1,sizeof(fail1),0);
						}else{
							for(int i=0;i<vec.size();++i){
								if(vec[i].username==temp1&&vec[i].passwd==temp2){
									srand((unsigned)time(NULL));
									int r=rand()+1;
									string s="Welcome, "+temp1+" "+to_string(r);
									send(sd,(const char *)s.c_str(),sizeof(inputBuffer),0);
									vec[i].number.push_back(r);
									ok=true;
									break;
								}
							}
							if(!ok){
								send(sd,fail2,sizeof(fail2),0);
							}
						}
						
					}

				}
			}	
		}


		//UDP
		
		if (FD_ISSET(udp_sockfd, &readfds)) { 
            		int len = sizeof(clientInfo); 
            		bzero(inputBuffer, sizeof(inputBuffer)); 
            		printf("Get from UDP: "); 
            		recvfrom(udp_sockfd,inputBuffer,sizeof(inputBuffer),0,(struct sockaddr*)&clientInfo,(socklen_t *)&len); 
            		puts(inputBuffer);
            		
            		stringstream ss(inputBuffer);
            		string temp;
            		ss>>temp; //register or whoami
            		
            		const char success[]="Register successfully.";
            		const char fail[]="Username is already used.";
            		
            		//register
            		if(inputBuffer[0]=='r'){
            			string temp1,temp2,temp3;
            			ss>>temp1>>temp2>>temp3;
            			bool rep=false;
            			for(int i=0;i<vec.size();++i){
            				if(vec[i].username==temp1){
            					rep=true;
            					break;
            				}
            			}
            			if(rep){
            				sendto(udp_sockfd,(const char*)fail,sizeof(fail),0,(struct sockaddr*)&clientInfo, sizeof(clientInfo));
            			}else{
            				USER U(temp1,temp2,temp3);
            				vec.push_back(U);
            				sendto(udp_sockfd,(const char*)success,sizeof(success),0,(struct sockaddr*)&clientInfo, sizeof(clientInfo));
            			}
            			
            		
            		}else{ //whoami
            			int num;
            			ss>>num;
            			const char fail[]="Please login first.";
            			if(num==0){
            				sendto(udp_sockfd,(const char*)fail,sizeof(fail),0,(struct sockaddr*)&clientInfo, sizeof(clientInfo));
            			}else{
		    			for(int i=0;i<vec.size();++i){
		    				if(find(vec[i].number.begin(),vec[i].number.end(),num)!=vec[i].number.end()){
		    					sendto(udp_sockfd,(const char*)(vec[i].username).c_str(),sizeof(inputBuffer),0,(struct sockaddr*)&clientInfo, sizeof(clientInfo));
		    					break;
		    				}
		    			}
            			}
            		}	
        	}
	}
	
return 0;
}




