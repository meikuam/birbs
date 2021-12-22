#pragma once
#include "ThreadHandler.h"
#include "servo_controller.h"
#define ROUNDING_ENABLED true
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
        int* water_level_data;
        uint8_t water_level_iteration = 0;
        unsigned long water_level_ping_timer = 0;
        
        int water_level_moving_average = 0;
        int water_level_measure_iterations = 3;
        int water_level_current = -1;
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
          int output_close_angle=-1) : Thread(3, 10000, 0) {
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
            
            this->water_level_data = new int[this->water_level_measure_iterations];
            this->water_level_ping_timer = millis();
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
            if(millis() - this->water_level_ping_timer >= PING_INTERVAL) {
              this->water_level_ping_timer += PING_INTERVAL;
              if (this->water_level_iteration < this->water_level_measure_iterations) {
                unsigned int last = this->water_level_sonar->ping(this->water_level_max_cm_distance);
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
          ThreadInterruptBlocker blocker;
          unsigned int uS[this->water_level_measure_iterations];
          uint8_t j, it = this->water_level_measure_iterations;
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
        void set_measure_iterations(uint8_t iterations = -1) {
          if (iterations != -1) {
            this->water_level_measure_iterations = iterations;
          }
          delete this->water_level_data;
          this->water_level_data = new int[this->water_level_measure_iterations];
          this->water_level_iteration = 0;
        }
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
