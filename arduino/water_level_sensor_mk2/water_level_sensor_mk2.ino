

#include <Wire.h> 
#include <iarduino_I2C_connect.h>
#include <iarduino_HC_SR04_tmr.h>


const uint8_t device_address = 0x62;
uint8_t device_register[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
bool device_register_mask[10] = {0, 0, 0, 0, 1, 1, 1, 1, 1, 1}; // master can write if values 1

/**
 * 0x0 - water level 1 - low byte
 * 0x1 - water level 1 - hight byte
 * 0x2 - water level 2 - low byte
 * 0x3 - water level 2 - hight byte
*/


uint8_t pinTrig1 = 3;// зеленый
uint8_t pinEcho1 = 2;
uint8_t pinTrig2 = 5;
uint8_t pinEcho2 = 4;

uint8_t poll_time = 100;


uint8_t log_times = 0;

iarduino_I2C_connect I2C_device;
iarduino_HC_SR04_tmr water_level_sensor1(pinTrig1, pinEcho1);
iarduino_HC_SR04_tmr water_level_sensor2(pinTrig2, pinEcho2);

void setup() {
  // инициируем подключение к шине I2C в качестве ведомого (slave) устройства, с указанием своего адреса на шине.
  Wire.begin(device_address); 
  I2C_device.begin(device_register);
  I2C_device.writeMask(device_register_mask);
  water_level_sensor1.averaging = 3;
  water_level_sensor1.begin(poll_time);
  water_level_sensor2.begin(poll_time);
  // water_level_sensor1.work(true);
}


void loop() {
  bool i = millis() % 100 < 50; // каждые 50 мс меняет значение

  water_level_sensor1.work(i);
  water_level_sensor2.work(!i);
                   
  device_register[0] = water_level_sensor1.distance();
  device_register[1] = water_level_sensor2.distance();
  // long distance1 = water_level_sensor1.distance();
  // long distance2 = water_level_sensor2.distance();
  // device_register[0] = (uint8_t) distance1;
  // device_register[3] = distance2 & 0xFF;
  // device_register[2] = (distance2 >> 8) & 0xFF;


  // delay(1); 
}