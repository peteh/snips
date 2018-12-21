/*
 * RFDevice.h
 *
 *  Created on: 6 Jun 2018
 *      Author: pi
 */

#ifndef DEVICE_RFDEVICE_H_
#define DEVICE_RFDEVICE_H_
#include "Device.h"
#include "../RCSwitch.h"

class RFDevice: public Device
{
public:
	RFDevice();
	RFDevice(std::string room, std::string deviceName, RCSwitch* rcSwitch,
			std::string groupCode, std::string deviceCode);

	std::string getGroupCode()
	{
		return m_groupCode;
	}

	std::string getDeviceCode()
	{
		return m_deviceCode;
	}

	void switchOn();
	void switchOff();
	bool isOn()
	{
		return m_isOn;
	}

	virtual ~RFDevice();

private:
	std::string m_groupCode;
	std::string m_deviceCode;
	RCSwitch* m_rcSwitch;
	bool m_isOn;
};

#endif /* DEVICE_RFDEVICE_H_ */
