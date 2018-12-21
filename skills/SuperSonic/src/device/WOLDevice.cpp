/*
 * WOLDevice.cpp
 *
 *  Created on: 6 Jun 2018
 *      Author: pi
 */

#include "WOLDevice.h"
#include <stdlib.h>

WOLDevice::WOLDevice(std::string room, std::string deviceName,
		std::string macAddress) :
		Device(room, deviceName), m_macAddress(macAddress), m_isOn(false)
{
	// TODO Auto-generated constructor stub

}

void WOLDevice::switchOn()
{
	std::string command = "sudo etherwake " + m_macAddress;
	system(command.c_str());
	m_isOn = true;
}

void WOLDevice::switchOff()
{
	// nothing to do
	m_isOn = false;
}

WOLDevice::~WOLDevice()
{
	// TODO Auto-generated destructor stub
}

