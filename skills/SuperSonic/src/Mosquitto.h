/*
 * Mosquitto.h
 *
 *  Created on: 25 Mar 2018
 *      Author: pi
 */

#ifndef MOSQUITTO_H_
#define MOSQUITTO_H_

#include <string>
#include <iostream>
#include <cstddef>
#include <mosquittopp.h>
#include <jsoncpp/json/json.h>
#include <algorithm>
#include "RCSwitch.h"
#include "device/Device.h"

class Mosquitto : public mosqpp::mosquittopp
{
public:
	Mosquitto(RCSwitch &rcSwitch, std::string intent, std::string rfGroup, std::string rfDevice) ;
	virtual ~Mosquitto();


    /*
     * This method is called when mosquittopp is connected (after a call to mosquittopp::connect). It then call on_connect.chai to handle the connection.
     *
     * @param rc : Return code of the connection. (see libmosquitto documentation).
     */
    void on_connect(int rc);

    /*
     * This method is called when mosquittopp receives a message from any of its topic subscriptions.
     *
     * @param message : Message from the broker, the message is converted from mosquitto_message to Message class before it is given to the on_message.chai script.
     *                  The message object is named 'message' in the script.
     *'
     */
    void on_message(const struct mosquitto_message *message);

    void endSession(std::string sessionId, std::string saySomething);

    void addDevice(Device* device);

private:
    std::string toLower(std::string str);
    std::vector<Device*> findDevices(std::string room, std::string deviceName);

    RCSwitch m_rcSwitch;
    bool m_lastState;
    std::string m_device;
	std::string m_rfGroup;
	std::string m_rfDevice;
	std::vector<Device*> m_devices;
};

#endif /* MOSQUITTO_H_ */
