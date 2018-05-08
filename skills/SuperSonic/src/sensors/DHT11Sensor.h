/*
 * DHT11Sensor.h
 *
 *  Created on: 29 Nov 2017
 *      Author: pi
 */

#ifndef DHT11SENSOR_H_
#define DHT11SENSOR_H_

class DHT11Sensor
{
public:
	DHT11Sensor();
	void readValue();
	virtual ~DHT11Sensor();
};

#endif /* DHT11SENSOR_H_ */
