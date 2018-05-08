/*
 * UltraSonicSensorArray.cpp
 *
 *  Created on: 25 Nov 2017
 *      Author: pi
 */
#include <iterator>
#include <thread>
#include "UltraSonicSensorArray.h"
#include <unistd.h>
#include <sstream>

UltraSonicSensorArray::UltraSonicSensorArray() :
		m_sensors(), m_values() {
	m_valueMutex = new std::mutex();

}

//static void updateThread(UltraSonicSensorArray *sensorArray) {
//	while (true) {
//		//sensorArray->updateSensors();
//		std::cout << sensorArray->createMessage() << std::endl;
//		usleep(100000);
//	}
//}

std::string UltraSonicSensorArray::createMessage() {

	std::ostringstream s;
	s << "#";

		for (UltraSonicSensor *sensor : m_sensors) {
			s << sensor->getName() << ":" << (int) (sensor->getValue()) << ";";
		}
		s << "!";
	return s.str();
}

void UltraSonicSensorArray::addSensor(UltraSonicSensor &sensor) {
	m_sensors.push_back(&sensor);
}

void UltraSonicSensorArray::init() {
	for (UltraSonicSensor *sensor : m_sensors) {
		sensor->init();
	}
//	std::thread *thread = new std::thread(updateThread, this);
}

UltraSonicSensorArray::~UltraSonicSensorArray() {
	//delete m_valueMutex;
}

