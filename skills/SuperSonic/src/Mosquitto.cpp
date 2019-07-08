/*
 * Mosquitto.cpp
 *
 *  Created on: 25 Mar 2018
 *      Author: pi
 */

#include "Mosquitto.h"

Mosquitto::Mosquitto(RCSwitch &rcSwitch, std::string device,
		std::string rfGroup, std::string rfDevice) :
		m_rcSwitch(rcSwitch), m_lastState(false), m_device(device), m_rfGroup(
				rfGroup), m_rfDevice(rfDevice)
{
	mosqpp::lib_init();
	int mid = connect_async("localhost");
	loop_start();
	std::string fullIntentDeviceSwitch = "hermes/intent/async:DeviceSwitch";
	std::string goCrazyIntent = "hermes/intent/async:GoCrazy";
	subscribe((int*) mid, fullIntentDeviceSwitch.c_str(), 1);
	subscribe((int*) mid, goCrazyIntent.c_str(), 1);
}

void Mosquitto::addDevice(Device* device)
{
	m_devices.push_back(device);
}

std::string Mosquitto::toLower(std::string str)
{
	std::string temp = str;
	std::transform(temp.begin(), temp.end(), temp.begin(), ::tolower);
	return temp;
}

std::string trim(const std::string& str)
{
	size_t first = str.find_first_not_of(' ');
	if (std::string::npos == first)
	{
		return str;
	}
	size_t last = str.find_last_not_of(' ');
	return str.substr(first, (last - first + 1));
}

void Mosquitto::on_message(const struct mosquitto_message *message)
{
	std::cout << "Received message" << std::endl;
	std::cout << message->topic << std::endl;

	if (strcmp(message->topic, "hermes/intent/async:GoCrazy") == 0)
	{
		on_messageCrazy(message);
	}
	else
	{
		on_messageDeviceSwitch(message);
	}
}

void Mosquitto::on_messageCrazy(const struct mosquitto_message *message)
{
	std::cout << "Crazy";
	std::string messageStr = std::string((char*) message->payload);

	Json::StyledWriter styledWriter;
	Json::Value intentJson;
	Json::Reader reader;
	bool parsingSuccessful = reader.parse(messageStr, intentJson);
	if (parsingSuccessful)
	{
		std::cout << styledWriter.write(intentJson) << std::endl;
	}

	std::string intentName = intentJson["intent"]["intentName"].asString();
	std::cout << intentName << std::endl;

	std::string sessionId = intentJson["sessionId"].asString();

	std::string device = "";
	std::string siteId = "";

	if (intentJson.isMember("siteId"))
	{
		siteId = intentJson["siteId"].asString();
	}

	std::string room = siteId;

	std::vector<Device*> devices = findDevices(room, "all lights");
	//std::vector<Device*> devices = findDevices("everywhere", "all lights");
	std::cout << "Room: " << room << std::endl;

	std::string deviceStr = "";

	for (auto device : devices)
	{
		deviceStr += device->getDeviceName() + " ";
	}

	endSession(sessionId, "I am crazy");
	for (int i = 0; i < 5; i++)
	{
		for (auto device : devices)
		{
			device->switchOn();
			device->switchOff();
		}

	}

}

void Mosquitto::on_messageDeviceSwitch(const struct mosquitto_message *message)
{
	std::cout << "DEVICE SWITCHING";
	std::string messageStr = std::string((char*) message->payload);

	Json::StyledWriter styledWriter;
	Json::Value intentJson;
	Json::Reader reader;
	bool parsingSuccessful = reader.parse(messageStr, intentJson);
	if (parsingSuccessful)
	{
		std::cout << styledWriter.write(intentJson) << std::endl;
	}

	std::string intentName = intentJson["intent"]["intentName"].asString();
	std::cout << intentName << std::endl;

	std::string sessionId = intentJson["sessionId"].asString();

	std::string device = "";
	std::string siteId = "";
	std::string room = "";
	std::string onoff = "";

	if (intentJson.isMember("siteId"))
	{
		siteId = intentJson["siteId"].asString();
	}

	if (intentJson.isMember("slots"))
	{
		Json::Value slots = intentJson["slots"];

		for (unsigned int i = 0; i < slots.size(); i++)
		{
			Json::Value slot = slots[i];
			std::string name = slot["slotName"].asString();
			std::string value = slot["value"]["value"].asString();

			std::cout << name << ": " << value << std::endl;

			if (name == "onoff")
			{
				onoff = toLower(trim(value));
			}

			if (name == "device")
			{
				device = toLower(trim(value));
			}

			if (name == "room")
			{
				room = toLower(trim(value));
			}

		}
	}

	if (room.compare("") == 0)
	{
		std::cout << "Room not commanded, using siteId: " << siteId
				<< std::endl;
		room = siteId;
	}

	std::vector<Device*> devices = findDevices(room, device);
	std::cout << "Room: " << room << std::endl;

	std::string deviceStr = "";
	bool switchTo = (onoff != "") ? (onoff == "on") : true;

	for (auto device : devices)
	{
		deviceStr += device->getDeviceName() + " ";
	}

	std::string switchToStr = (switchTo ? "on" : "off");
	if (devices.size() == 0)
	{
		endSession(sessionId,
				"There is no " + device + " in the " + room + ", you moron! ");
		return;
	}

	endSession(sessionId, "I turned the " + deviceStr + " " + switchToStr);
	for (auto device : devices)
	{
		if (switchTo)
		{
			device->switchOn();
		}
		else
		{
			device->switchOff();
		}
	}

}

void Mosquitto::endSession(std::string sessionId, std::string saySomething)
{
	Json::Value jsonStuff = Json::Value();
	jsonStuff["sessionId"] = sessionId;
	jsonStuff["text"] = saySomething;
	Json::StyledWriter styledWriter;

	std::string messageJson = styledWriter.write(jsonStuff);

	this->publish((int*) 0, "hermes/dialogueManager/endSession",
			messageJson.size(), messageJson.c_str());
}

std::vector<Device*> Mosquitto::findDevices(std::string room,
		std::string deviceName)
{
	std::vector<Device*> devices;

	for (auto device : m_devices)
	{
		if ((room.compare(device->getRoom()) == 0
				|| room.compare("everywhere") == 0)
				&& (deviceName.compare(device->getDeviceName()) == 0
						|| device->isAlias(deviceName)))
		{
			std::cout << device->getRoom() << ":" << device->getDeviceName()
					<< " matches the search" << std::endl;
			devices.push_back(device);
		}
	}
	return devices;
}

void Mosquitto::on_connect(int rc)
{
	if (rc == 0)
	{
		std::cout << "Connected to mqtt broker" << std::endl;
	}
	else
	{
		// otherwise well.. maybe we could try to reconnect.
		std::cerr << "Connection problem" << std::endl;
	}
}

Mosquitto::~Mosquitto()
{
	loop_stop();
	mosqpp::lib_cleanup();
}

