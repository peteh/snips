/*
 * UltraSonicSensor.h
 *
 *  Created on: 24 Nov 2017
 *      Author: pi
 */

#ifndef ULTRASONICSENSOR_H_
#define ULTRASONICSENSOR_H_
#include <iostream>
#include <mutex>
#include <wiringPi.h>

/**
 * Sensor abstraction for HC-SR04 Sensors.
 *
 * These sensors require 5V and the Echo has to be divided because the IO Pins of
 * the Rpi are designed to handle 3.3V. That's why we can use resistors to divide
 * the voltage.
 *
 *  (+5V) --- Sensor5VPin
 *
 *  RPITriggerPin --- SensorTriggerPin
 *
 *  (-) --- 1kOhm --- RPIEchoPin --- 0.3kOhm --- 0.3kOhm --- SensorEchoPin
 *
 *  (-) --- SensorGnd
 */
class UltraSonicSensor {
public:
	UltraSonicSensor(const std::string &name, int trigger, int echo);

	bool readValue(double &result);
	void init();
	const std::string& getName();
	double getValue();
	void setValue(double value);

	static void updateThread(UltraSonicSensor *sensor);
	virtual ~UltraSonicSensor();

private:
	int m_trigger;
	int m_echo;
	double m_value;
	const std::string m_name;
};

#endif /* ULTRASONICSENSOR_H_ */
