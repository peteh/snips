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
	std::string fullIntent = "hermes/intent/async:DeviceSwitch";
	subscribe((int*) mid, fullIntent.c_str(), 1);
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

	bool switchTo = !m_lastState;
	std::string device = "";
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
				switchTo = (value == "on");
			}

			if (name == "device")
			{
				device = toLower(trim(value));
			}

		}
	}

	std::string deviceCode = "00000";
	if(device == "light")
	{
		// 00100 big lights
		// 00010 small lights
		deviceCode = "00010";
	}
	else if (device == "fan")
	{
		deviceCode = "01000";
	}
	else if (device == "bedlight")
	{
		deviceCode = "10000";
	}
	else
	{
		// not for us
		std::cout << "I am " << m_device << ", ignoring " << device;
		return;
	}

	m_lastState = switchTo;
	std::cout << "Switching " << device << " to " << switchTo << std::endl;
	if (switchTo)
	{
		m_rcSwitch.switchOn(m_rfGroup.c_str(), deviceCode.c_str());
		m_rcSwitch.switchOn(m_rfGroup.c_str(), deviceCode.c_str());
	}
	else
	{
		m_rcSwitch.switchOff(m_rfGroup.c_str(), deviceCode.c_str());
		m_rcSwitch.switchOff(m_rfGroup.c_str(), deviceCode.c_str());
	}
	std::string switchToStr = (switchTo ? "on" : "off");
	endSession(sessionId,
			"I turned the " + device + " " + switchToStr);

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

