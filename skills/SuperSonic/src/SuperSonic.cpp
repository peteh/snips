#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <iostream>
#include <math.h>
#include "sensors/UltraSonicSensor.h"
#include "TcpServer.h"
#include "sensors/DHT11Sensor.h"

#define TRIGGER1 4
#define ECHO1 5

#define TRIGGER3 0
#define ECHO3 1

#define TRIGGER2 3
#define ECHO2 6

#define RCDATA 7

#define BUTTON_TIMEOUT_MS 1000

#include "RCSwitch.h"
#include "Mosquitto.h"
#include <mosquittopp.h>
#include "device/Device.h"
#include "device/RFDevice.h"
#include "device/WOLDevice.h"

void setup()
{
	wiringPiSetup();
}

void runBaseDriverServer()
{
	UltraSonicSensor sensor1("Ultra1", TRIGGER1, ECHO1);
	UltraSonicSensor sensor2("Ultra2", TRIGGER2, ECHO2);
	UltraSonicSensor sensor3("Ultra3", TRIGGER3, ECHO3);

	UltraSonicSensorArray sensorArray;
	sensorArray.addSensor(sensor1);
	sensorArray.addSensor(sensor2);
	sensorArray.addSensor(sensor3);
	sensorArray.init();

	TcpServer server(sensorArray);
	bool started = server.run();
}

bool trigger(double value)
{
	return value < 30.;
}

void distanceEnabler()
{
	UltraSonicSensor sensor1("Ultra1", TRIGGER1, ECHO1);
	sensor1.init();

	RCSwitch mySwitch = RCSwitch();
	mySwitch.enableTransmit(RCDATA);

	bool enabled = false;

	unsigned int lastSwitch = micros();

	double lastValue = INFINITY;
	while (true)
	{
		double value;
		if (!sensor1.readValue(value))
		{
			continue;
		}

		if (!trigger(lastValue) && trigger(value)
				&& micros() - lastSwitch > BUTTON_TIMEOUT_MS * 1000)
		{
			std::cout << "current: " << value << std::endl;
			std::cout << "last: " << lastValue << std::endl;

			if (enabled)
			{ // TODO Auto-generated constructor stub

				mySwitch.switchOff("11111", "10000");
			}
			else
			{
				mySwitch.switchOn("11111", "10000");
			}
			enabled = !enabled;

			lastSwitch = micros();
		}

		lastValue = value;
	}
}

void mosq()
{
	RCSwitch mySwitch = RCSwitch();
	mySwitch.enableTransmit(RCDATA);

	Mosquitto m = Mosquitto(mySwitch, "Bedlight", "10000", "10000");
	std::string LIGHT = "light";
	std::string FAN = "fan";
	std::string ALL_LIGHTS = "all lights";
	std::string EVERYTHING = "everything";

	// bedroom 10000
	// 00100 big lights bedroom
	// 00010 small lights bedroom
	// 01000 fan
	// 10000 bed light

	Device* bedlightBedroom = new RFDevice("bedroom", "bedlight", &mySwitch,
			"10000", "10000");
	bedlightBedroom->addAliasDeviceName(ALL_LIGHTS);
	bedlightBedroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(bedlightBedroom);

	Device* smallLightBedroom = new RFDevice("bedroom", "small light",
			&mySwitch, "10000", "00010");
	smallLightBedroom->addAliasDeviceName(LIGHT);
	smallLightBedroom->addAliasDeviceName(ALL_LIGHTS);
	smallLightBedroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(smallLightBedroom);

	Device* bigLightBedroom = new RFDevice("bedroom", "big light", &mySwitch,
			"10000", "00100");
	bigLightBedroom->addAliasDeviceName(LIGHT);
	bigLightBedroom->addAliasDeviceName(ALL_LIGHTS);
	bigLightBedroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(bigLightBedroom);

	Device* fanBedroom = new RFDevice("bedroom", FAN, &mySwitch, "10000",
			"01000");
	fanBedroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(fanBedroom);

	// kitchen 01000
	// 01000 fan
	Device* fanKitchen = new RFDevice("kitchen", FAN, &mySwitch, "01000",
			"01000");
	fanKitchen->addAliasDeviceName(EVERYTHING);
	m.addDevice(fanKitchen);

	// livingroom 00100
	Device* lightLivingroom = new RFDevice("livingroom", LIGHT, &mySwitch,
			"00100", "00010");
	lightLivingroom->addAliasDeviceName(ALL_LIGHTS);
	lightLivingroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(lightLivingroom);

	Device* fanLivingroom = new RFDevice("livingroom", FAN, &mySwitch, "00100", "01000");
	fanLivingroom->addAliasDeviceName(EVERYTHING);
	m.addDevice(fanLivingroom);

	m.addDevice(new WOLDevice("livingroom", "computer", "00:24:1D:C0:BE:F8"));
	sleep(30);
}

int main(void)
{
	setup();
	mosq();
	//runBaseDriverServer();
	//runVoiceRecognition();
	//distanceEnabler();
	return 0;
}
