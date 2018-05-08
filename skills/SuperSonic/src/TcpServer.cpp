/*
 * TcpServer.cpp
 *
 *  Created on: 24 Nov 2017
 *      Author: pi
 */
#include <cstring>
#include <netinet/tcp.h>
#include "TcpServer.h"

struct KeepConfig {
	/** The time (in seconds) the connection needs to remain
	 * idle before TCP starts sending keepalive probes (TCP_KEEPIDLE socket option)
	 */
	int keepidle;
	/** The maximum number of keepalive probes TCP should
	 * send before dropping the connection. (TCP_KEEPCNT socket option)
	 */
	int keepcnt;

	/** The time (in seconds) between individual keepalive probes.
	 *  (TCP_KEEPINTVL socket option)
	 */
	int keepintvl;
};

/**
 * enable TCP keepalive on the socket
 * @param fd file descriptor
 * @return 0 on success -1 on failure
 */
int set_tcp_keepalive(int sockfd) {
	int optval = 1;

	return setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval));
}

/** Set the keepalive options on the socket
 * This also enables TCP keepalive on the socket
 *
 * @param fd file descriptor
 * @param fd file descriptor
 * @return 0 on success -1 on failure
 */
int set_tcp_keepalive_cfg(int sockfd, const struct KeepConfig *cfg) {
	int rc;

	//first turn on keepalive
	rc = set_tcp_keepalive(sockfd);
	if (rc != 0) {
		return rc;
	}

	//set the keepalive options
	rc = setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &cfg->keepcnt,
			sizeof cfg->keepcnt);
	if (rc != 0) {
		return rc;
	}

	rc = setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &cfg->keepidle,
			sizeof cfg->keepidle);
	if (rc != 0) {
		return rc;
	}

	rc = setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &cfg->keepintvl,
			sizeof cfg->keepintvl);
	if (rc != 0) {
		return rc;
	}

	return 0;
}

TcpServer::TcpServer(UltraSonicSensorArray &sensorArray) :
		m_sensorArray(sensorArray) {

}

TcpServer::~TcpServer() {

}

void TcpServer::clientThread(int connFd, UltraSonicSensorArray *sensorArray) {

	while (true) {

		int ret1, ret2;
		char buffer[64];

		ret1 = recv(connFd, buffer, sizeof(buffer), MSG_PEEK | MSG_DONTWAIT);
		/* Error handling -- and EAGAIN handling -- would go here.  Bail if
		 necessary.  Otherwise, keep going.  */

		if(ret1 == 0)
		{
			//std::cerr << "Remote shutdown" << std::endl;
			return;
		}

		if(ret1 < 0)
		{
			//std::cerr << "Error handling errno: " << errno << std::endl;
		}

		if(ret1 > 0)
		{
			ret1 = recv(connFd, buffer, sizeof(buffer), 0);
		}

		std::string msg = sensorArray->createMessage();
		int data = write(connFd, msg.c_str(), msg.size());

		//std::cerr << data << std::endl;
		usleep(50000);
	}
}

bool TcpServer::run() {
	int pId, listenFd;
	socklen_t len; //store size of the address
	bool loop = false;
	struct sockaddr_in svrAdd, clntAdd;

	int portNo = 2999;

	//create socket
	listenFd = socket(AF_INET, SOCK_STREAM, 0);

	if (listenFd < 0) {
		std::cerr << "Cannot open socket" << std::endl;
		return false;
	}

	// we need to clear it with zero
	std::memset(&svrAdd, 0, sizeof(svrAdd));
	svrAdd.sin_family = AF_INET;
	svrAdd.sin_addr.s_addr = INADDR_ANY;
	svrAdd.sin_port = htons(portNo);

	struct KeepConfig cfg = { 10, 5, 5 };
	set_tcp_keepalive_cfg(listenFd, &cfg);
	//bind socket
	if (bind(listenFd, (struct sockaddr *) &svrAdd, sizeof(svrAdd)) < 0) {
		std::cerr << "Cannot bind" << std::endl;
		return false;
	}

	listen(listenFd, 5);

	len = sizeof(clntAdd);

	int noThread = 0;

	while (true) {
		std::cout << "Listening" << std::endl;

		//this is where client connects. svr will hang in this mode until client conn
		int connFd = accept(listenFd, (struct sockaddr *) &clntAdd, &len);
		//set output buffer size so that send blocks

		struct KeepConfig cfg = { 10, 5, 5 };
		set_tcp_keepalive_cfg(connFd, &cfg);

		if (connFd < 0) {
			std::cerr << "Cannot accept connection" << std::endl;
			return 0;
		} else {
			std::cout << "Connection successful" << std::endl;
		}

		// TODO: we never clean this up
		std::thread *newThread = new std::thread(TcpServer::clientThread,
				connFd, &m_sensorArray);

		noThread++;
	}
}
