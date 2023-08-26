

#include <Wire.h> 
#include <iarduino_I2C_connect.h>

#define ROUNDING_ENABLED true
#define PING_INTERVAL 33 // ms between measures
#define US_ROUNDTRIP_MM 5.7f
#include <NewPing.h>


const uint8_t device_address = 0x62;
uint8_t device_register[10];
bool device_register_mask[10] = {0, 0, 0, 0, 1, 1, 1, 1, 1, 1}; // master can write if values 1

/**
 * 0x0 - water level 1 - low byte
 * 0x1 - water level 1 - hight byte
 * 0x2 - water level 2 - low byte
 * 0x3 - water level 2 - hight byte
*/



#define water_level_measure_iterations 15

class WaterLevelSensor {

    public:
        NewPing* water_level_sensor;
        uint8_t water_level_trigger_pin;
        uint8_t water_level_echo_pin;
        unsigned int water_level_max_cm_distance = 15;

        unsigned int water_level_data[water_level_measure_iterations];
        unsigned int uS[water_level_measure_iterations];
        uint8_t water_level_iteration = 0;
        unsigned long water_level_ping_timer = 0;

        unsigned int water_level_current = 0; // water level stored here

        WaterLevelSensor(
          uint8_t water_level_trigger_pin,
          uint8_t water_level_echo_pin
        ) {
            this->water_level_ping_timer = millis();
            this->water_level_trigger_pin = water_level_trigger_pin;
            this->water_level_echo_pin = water_level_echo_pin;
            this->water_level_sensor = new NewPing(
                this->water_level_trigger_pin,
                this->water_level_echo_pin,
                this->water_level_max_cm_distance
                );
        }
        ~WaterLevelSensor() {

        }

        void setup() {
            pinMode(this->water_level_trigger_pin, OUTPUT); 
            pinMode(this->water_level_trigger_pin, INPUT); 
        }
        
        void run() {
            this->water_level_measure();
        }

        int water_level_measure() {
          if(millis() - this->water_level_ping_timer >= PING_INTERVAL) {
            this->water_level_ping_timer += PING_INTERVAL;
            if (this->water_level_iteration < water_level_measure_iterations) {
              unsigned int last = this->water_level_sensor->ping(this->water_level_max_cm_distance);
              if (last != NO_ECHO) {
                this->water_level_data[this->water_level_iteration] = NewPingConvert(last, US_ROUNDTRIP_MM);
                this->water_level_iteration++;
              }
            } else {
              this->water_level_median_cycle();
              this->water_level_iteration = 0;
            }
          }
        }
        void water_level_median_cycle() {
          uint8_t j, it = water_level_measure_iterations;
          uS[0] = NO_ECHO;
          for (uint8_t i = 0; i < it; i++) { // Loop through iteration results.
            if (this->water_level_data[i] != NO_ECHO) { // Ping in range, include as part of median.
              if (i > 0) {          // Don't start sort till second ping.
                for (j = i; j > 0 && uS[j - 1] < this->water_level_data[i]; j--) // Insertion sort loop.
                  uS[j] = uS[j - 1];                         // Shift ping array to correct position for sort insertion.
              } else j = 0;         // First ping is sort starting point.
              uS[j] = this->water_level_data[i];        // Add last ping to array in sorted position.
            } else it--;            // Ping out of range, skip and don't include as part of median.
          }
          this->water_level_current = uS[it >> 1];
        }
};



WaterLevelSensor** water_level_sensors;
uint8_t water_level_sensors_count = 2;

uint8_t log_times = 0;

iarduino_I2C_connect I2C_device;

void setup() {
  Serial.begin(115200);
  // инициируем подключение к шине I2C в качестве ведомого (slave) устройства, с указанием своего адреса на шине.
  Wire.begin(device_address); 
  I2C_device.begin(device_register);
  I2C_device.writeMask(device_register_mask);

  water_level_sensors = new WaterLevelSensor*[water_level_sensors_count];
  water_level_sensors[0] = new WaterLevelSensor(3, 2); // trigger, echo
  water_level_sensors[0]->setup();
  water_level_sensors[1] = new WaterLevelSensor(5, 4); // trigger, echo
  water_level_sensors[1]->setup();

}


void loop() {
    delay(1);                    
    for (int i = 0; i < water_level_sensors_count; i++) {
        water_level_sensors[i]->run();
        device_register[i * 2] = water_level_sensors[i]->water_level_current;
        device_register[i * 2 + 1] = (water_level_sensors[i]->water_level_current >> 8);
    }
    log_times += 1;
    if (log_times >= 100) {
        log_times = 0;
        Serial.print("Ping: ");
        Serial.print(water_level_sensors[0]->water_level_current);     
        Serial.print(" ");

        Serial.print(device_register[0], DEC);
        Serial.print(" ");
        Serial.print(device_register[1], DEC);
        Serial.print("mm ");

        Serial.print("Ping: ");
        Serial.print(water_level_sensors[1]->water_level_current);     
        Serial.print(" ");

        Serial.print(device_register[2], DEC);
        Serial.print(" ");
        Serial.print(device_register[3], DEC);
        Serial.println("mm");
    }
}