/*
 * WOLDevice.h
 *
 *  Created on: 6 Jun 2018
 *      Author: pi
 */

#ifndef DEVICE_WOLDEVICE_H_
#define DEVICE_WOLDEVICE_H_
#include <string>
#include "Device.h"

class WOLDevice : public Device
{
public:
	WOLDevice(std::string room, std::string deviceName, std::string macAddress);
	void switchOn();
	void switchOff();
	bool isOn()
	{
		return m_isOn;
	}

	virtual ~WOLDevice();

private:
	std::string m_macAddress;
	bool m_isOn;
};

#endif /* DEVICE_WOLDEVICE_H_ */
