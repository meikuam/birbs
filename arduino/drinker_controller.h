#pragma once
#include "servo_controller.h"
#define ROUNDING_ENABLED true
#define US_ROUNDTRIP_MM 5.7f
#include <NewPing.h>

// drinker control
class DrinkerController {
  
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
        int water_level_measure_iterations = 10;
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
          int output_close_angle=-1) {
            this->input_open_angle = input_open_angle;
            this->input_close_angle = input_close_angle;
            this->input_controller = new ServoController(
                input_pin, 
                this->input_close_angle, 
                MG995_MIN_PWM,
                MG995_MAX_PWM);

            this->output_open_angle = output_open_angle;
            this->output_close_angle = output_close_angle;
            this->output_controller = new ServoController(
                output_pin, 
                this->output_open_angle, 
                MG995_MIN_PWM, 
                MG995_MAX_PWM);
            
            this->water_level_trigger_pin = water_level_trigger_pin;
            this->water_level_echo_pin = water_level_echo_pin;
            this->water_level_sonar = new NewPing(
                this->water_level_trigger_pin,
                this->water_level_echo_pin,
                this->water_level_max_cm_distance
                );
        };

        void setup() {
            pinMode(this->water_level_trigger_pin, OUTPUT); 
            pinMode(this->water_level_trigger_pin, INPUT); 
        }
        void loop() {
            this->water_level_measure();
            if (empty_flag) {
              fill_flag = false;
              this->input_close();
              this->output_open();
              if (this->water_level_current >= this->water_level_min_level) {
                this->output_close();
                empty_flag = false;
              }
            }
            if (fill_flag) {
              empty_flag = false;
              this->output_close();
              this->input_open();
              
              if (this->water_level_current <= this->water_level_max_level) {
                this->input_close();
                fill_flag = false;
              }
            }
        }

        int water_level_measure() {
            this->water_level_current = NewPingConvert(
                this->water_level_sonar->ping_median(
                    this->water_level_measure_iterations,
                    this->water_level_max_cm_distance),
                US_ROUNDTRIP_MM);
//            this->water_level_current = this->water_level_sonar->convert_cm(
//                this->water_level_sonar->ping_median(
//                    this->water_level_measure_iterations,
//                    this->water_level_max_cm_distance));
            return this->water_level_current;
        }

        void input_set_angle(int angle) {
            this->input_controller->write(angle);
        }
        void output_set_angle(int angle) {
            this->output_controller->write(angle);
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
          empty_flag = false;
          fill_flag = true;
        }
        void empty_async() {
          empty_flag = true;
          fill_flag = false;
        }
        
};
