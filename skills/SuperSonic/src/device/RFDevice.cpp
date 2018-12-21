/*
 * RFDevice.cpp
 *
 *  Created on: 6 Jun 2018
 *      Author: pi
 */

#include "RFDevice.h"

RFDevice::RFDevice() :
		RFDevice("", "", nullptr, "00000", "00000")
{
}

RFDevice::RFDevice(std::string room, std::string deviceName, RCSwitch* rcSwitch,
		std::string groupCode, std::string deviceCode) :
		m_groupCode(groupCode), m_deviceCode(deviceCode), Device(room,
				deviceName),
				m_rcSwitch(rcSwitch),
				m_isOn(false)
{

}

void RFDevice::switchOn()
{
	m_rcSwitch->switchOn(getGroupCode().c_str(), getDeviceCode().c_str());
	m_isOn = true;
}

void RFDevice::switchOff()
{
	m_rcSwitch->switchOff(getGroupCode().c_str(), getDeviceCode().c_str());
	m_isOn = false;
}

RFDevice::~RFDevice()
{
	// TODO Auto-generated destructor stub
}

