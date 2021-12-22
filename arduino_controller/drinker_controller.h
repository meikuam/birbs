#pragma once
#include "ThreadHandler.h"
#include "servo_controller.h"
#define ROUNDING_ENABLED true
#define PING_DELAY 10  // ms delay between measures
#define PING_INTERVAL 33 // ms between measures
#define US_ROUNDTRIP_MM 5.7f
#include <NewPing.h>

// drinker control
class DrinkerController: public Thread {
  
    private:
    public:
        ServoController* input_controller;
        ServoController* output_controller;
        int input_open_angle;
        int input_close_angle;
        int output_open_angle;
        int output_close_angle;

        NewPing* water_level_sonar;
        uint8_t water_level_trigger_pin;
        uint8_t water_level_echo_pin;
        int water_level_current = -1;
        int water_level_moving_average = 0;
        int water_level_measure_iterations = 3;
        int water_level_max_cm_distance = 10;
        int water_level_max_level = -1;
        int water_level_min_level = -1;
        bool empty_flag = false;
        bool fill_flag = false;

        DrinkerController(
          uint8_t input_pin, 
          uint8_t output_pin,
          uint8_t water_level_trigger_pin,
          uint8_t water_level_echo_pin,
          int input_open_angle=-1,
          int input_close_angle=-1,
          int output_open_angle=-1,
          int output_close_angle=-1) : Thread(3, 20000, 0) {
            this->input_open_angle = input_open_angle;
            this->input_close_angle = input_close_angle;
            this->input_controller = new ServoController(
                input_pin, 
                this->input_close_angle, 
                MG995_MIN_PWM,
                MG995_MAX_PWM,
                MG995_ROTATION_SPEED);
            this->input_close();

            this->output_open_angle = output_open_angle;
            this->output_close_angle = output_close_angle;
            this->output_controller = new ServoController(
                output_pin, 
                this->output_close_angle, 
                MG995_MIN_PWM, 
                MG995_MAX_PWM,
                MG995_ROTATION_SPEED);
            this->output_close();
            
            this->water_level_trigger_pin = water_level_trigger_pin;
            this->water_level_echo_pin = water_level_echo_pin;
            this->water_level_sonar = new NewPing(
                this->water_level_trigger_pin,
                this->water_level_echo_pin,
                this->water_level_max_cm_distance
                );
        };
        virtual ~DrinkerController() {
          delete this->input_controller;
          delete this->output_controller;
          delete this->water_level_sonar;
        }

        void setup() {
            pinMode(this->water_level_trigger_pin, OUTPUT); 
            pinMode(this->water_level_trigger_pin, INPUT); 
        }

        void reset() {
            this->fill_flag = false;
            this->empty_flag = false;
            this->input_close();
            this->output_open();
        }
        
        virtual void run() {
            this->water_level_measure();
            if (this->empty_flag) {
              ThreadInterruptBlocker blocker;
              this->fill_flag = false;
              this->input_close();
              this->output_open();
              if (this->water_level_current >= this->water_level_min_level) {
                this->output_close();
                this->empty_flag = false;
              }
            }
            if (this->fill_flag) {
              ThreadInterruptBlocker blocker;
              this->empty_flag = false;
              this->output_close();
              this->input_open();
              
              if (this->water_level_current <= this->water_level_max_level) {
                this->input_close();
                this->fill_flag = false;
              }
            }
        }

        int water_level_measure() {
            ThreadInterruptBlocker blocker;
//            unsigned int last_measure = NO_ECHO;
//            
//            uint8_t tries = 10;
//            for (int i = 0; i < this->water_level_measure_iterations; i++) {
//              last_measure = NO_ECHO;
//              tries = 10;
//              while(last_measure == NO_ECHO && tries > 0) {
//                last_measure = this->water_level_sonar->ping(this->water_level_max_cm_distance);
//                tries--;
//              }
//              if (last_measure != NO_ECHO) {
//                this->water_level_current = NewPingConvert(
//                  last_measure,
//                  US_ROUNDTRIP_MM
//                  );
//                this->water_level_moving_average = 0.9 * this->water_level_moving_average + 0.1 * this->water_level_current;
////                delay(PING_DELAY);
//              }
//            }

//            ///////////////////////////////
//            unsigned int measure_time = millis();
            this->water_level_current = NewPingConvert(
                this->water_level_sonar->ping_median(
                    this->water_level_measure_iterations,
                    this->water_level_max_cm_distance),
                US_ROUNDTRIP_MM);
            this->water_level_moving_average = 0.8 * this->water_level_moving_average + 0.2 * this->water_level_current;
//            measure_time = millis() - measure_time;
//            Serial.print("mm: "); Serial.print(this->water_level_current); Serial.print(" time:"); Serial.println(measure_time);
//            
//            ///////////////////////////////
//          if(millis() > ) {
//            
//          }
        }
//        void echo_check() { // If ping received, set the sensor distance to array.
//          if (sonar.check_timer())
//            cm[currentIteration] = sonar.ping_result / US_ROUNDTRIP_CM;
//        }
//        void one_sensor_cycle() { // All iterations complete, calculate the median.
//          unsigned int uS[this->water_level_measure_iterations];
//          uint8_t j, it = this->water_level_measure_iterations;
//          uS[0] = NO_ECHO;
//          for (uint8_t i = 0; i < it; i++) { // Loop through iteration results.
//            if (cm[i] != NO_ECHO) { // Ping in range, include as part of median.
//              if (i > 0) {          // Don't start sort till second ping.
//                for (j = i; j > 0 && uS[j - 1] < cm[i]; j--) // Insertion sort loop.
//                  uS[j] = uS[j - 1];                         // Shift ping array to correct position for sort insertion.
//              } else j = 0;         // First ping is sort starting point.
//              uS[j] = cm[i];        // Add last ping to array in sorted position.
//            } else it--;            // Ping out of range, skip and don't include as part of median.
//          }
//          this->water_level_current = uS[it >> 1];
//        }

        void input_set_angle(int angle) {
            this->input_controller->write(angle, true);
        }
        void output_set_angle(int angle) {
            this->output_controller->write(angle, true);
        }
        void input_open() {
          this->input_set_angle(this->input_open_angle);
        }
        void input_close() {
          this->input_set_angle(this->input_close_angle);
        }
        void output_open() {
          this->output_set_angle(this->output_open_angle);
        }
        void output_close() {
          this->output_set_angle(this->output_close_angle);
        }
        void fill_async() {
          ThreadInterruptBlocker blocker;
          if (this->water_level_max_level != -1 && this->water_level_min_level != -1) {
            this->empty_flag = false;
            this->fill_flag = true;
          }
        }
        void empty_async() {
          ThreadInterruptBlocker blocker;
          if (this->water_level_max_level != -1 && this->water_level_min_level != -1) {
            this->fill_flag = false;
            this->empty_flag = true;
          }
        }
        
};
