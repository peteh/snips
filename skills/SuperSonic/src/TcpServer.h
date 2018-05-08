/*
 * TcpServer.h
 *
 *  Created on: 24 Nov 2017
 *      Author: pi
 */

#ifndef TCPSERVER_H_
#define TCPSERVER_H_

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string>
#include <thread>
#include <ostream>
#include <iostream>
#include "sensors/UltraSonicSensorArray.h"
class TcpServer {
public:
	TcpServer(UltraSonicSensorArray &sensorArray);
	bool run();
	virtual ~TcpServer();
private:
	static void clientThread(int connFd, UltraSonicSensorArray *sensorArray);
	UltraSonicSensorArray &m_sensorArray;
};

#endif /* TCPSERVER_H_ */
