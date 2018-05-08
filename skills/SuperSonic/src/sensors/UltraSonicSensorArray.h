/*
 * UltraSonicSensorArray.h
 *
 *  Created on: 25 Nov 2017
 *      Author: pi
 */

#ifndef ULTRASONICSENSORARRAY_H_
#define ULTRASONICSENSORARRAY_H_
#include <vector>
#include "UltraSonicSensor.h"
#include <string>
#include <map>
#include <mutex>

class UltraSonicSensorArray {
public:
	UltraSonicSensorArray();
	void addSensor(UltraSonicSensor &sensor);

	void init();
	virtual ~UltraSonicSensorArray();
	void updateSensors();
	std::string createMessage();

private:

	std::vector<UltraSonicSensor*> m_sensors;
	std::map<std::string, double> m_values;
	std::mutex *m_valueMutex;
};

#endif /* ULTRASONICSENSORARRAY_H_ */
