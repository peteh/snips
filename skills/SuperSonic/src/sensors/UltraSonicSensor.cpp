/*
 * UltraSonicSensor.cpp
 *
 *  Created on: 24 Nov 2017
 *      Author: pi
 */

#include "UltraSonicSensor.h"
#include <thread>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

UltraSonicSensor::UltraSonicSensor(const std::string &name, int trigger,
		int echo) :
		m_name(name), m_trigger(trigger), m_echo(echo), m_value(0)
{

}

void UltraSonicSensor::init()
{
	pinMode(m_trigger, OUTPUT);
	pinMode(m_echo, INPUT);
	digitalWrite(m_trigger, LOW);
	delay(30);

	std::thread *thread = new std::thread(UltraSonicSensor::updateThread, this);
}

const std::string& UltraSonicSensor::getName()
{
	return m_name;
}

void UltraSonicSensor::updateThread(UltraSonicSensor *sensor)
{
	while (true)
	{
		double value;
		bool success = sensor->readValue(value);
		if (success)
		{
			sensor->setValue(value);
		}
		usleep(10000);
	}
}

double UltraSonicSensor::getValue()
{
	return m_value;
}

void UltraSonicSensor::setValue(double value)
{
	m_value = value;
}

bool UltraSonicSensor::readValue(double &result)
{
	//Send trig pulse
	digitalWrite(m_trigger, HIGH);
	delayMicroseconds(30);
	digitalWrite(m_trigger, LOW);
	unsigned int timeout = 2 * 1000000;

	long timeoutStart = micros();
	//Wait for echo start
	while (digitalRead(m_echo) == LOW && micros() - timeoutStart < timeout)
	{
		// we are just busy waiting
	}

	//Wait for echo end
	long startTime = micros();
	while (digitalRead(m_echo) == HIGH && micros() - timeoutStart < timeout)
	{
		// we are just busy waiting
	}

	// we reached the timeout
	if (micros() - timeoutStart >= timeout)
	{
		return false;
	}

	long travelTime = micros() - startTime;

	//Get distance in cm
	double distance = travelTime / 58.;
	result = distance;
	return true;
}

UltraSonicSensor::~UltraSonicSensor()
{
	// TODO Auto-generated destructor stub
}

