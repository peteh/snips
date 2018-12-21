/*
 * Device.h
 *
 *  Created on: 27 May 2018
 *      Author: pi
 */

#ifndef DEVICE_DEVICE_H_
#define DEVICE_DEVICE_H_

#include <string>
#include <vector>

class Device
{
public:

	Device(std::string room, std::string deviceName);

	virtual ~Device();

	std::string getDeviceName()
	{
		return m_deviceName;
	}

	std::string getRoom()
	{
		return m_room;
	}

	virtual bool isOn() = 0;

	virtual void switchOn() = 0;
	virtual void switchOff() = 0;

	Device* addAliasDeviceName(std::string alias)
	{
		m_aliases.push_back(alias);
		return this;
	}

	bool isAlias(std::string search)
	{
		for(auto alias : m_aliases)
		{
			if(alias.compare(search) == 0)
			{
				return true;
			}
		}
		return false;
	}

private:
	std::string m_room;
	std::string m_deviceName;
	std::vector<std::string> m_aliases;

};

#endif /* DEVICE_DEVICE_H_ */
