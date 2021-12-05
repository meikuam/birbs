#pragma once
#include "servo_controller.h"



class FeederController {
      /*
     * incoming commands:
     * 20 1 - get feeder box angle for first instance
     * 21 1 0 - set feeder box to angle for first instance
     * 22 1- enable feeder gate
     * 23 1 0 - enable feeder gate for number ms
     * 
     * outcomming commands:
     * 1_0 - feeder box angle for first instance
     */
    private:
    public:
        ServoController* feeder_box_controller;
        int feeder_box_open_angle;
        int feeder_box_close_angle;

        ServoController* feeder_gate_controller;
        int feeder_gate_open_angle;
        int feeder_gate_close_angle;
        int feeder_gate_delay=100;

        FeederController(
          uint8_t feeder_box_pin, 
          uint8_t feeder_gate_pin,
          int feeder_box_open_angle=10, 
          int feeder_box_close_angle=100,
          int feeder_gate_open_angle=150, 
          int feeder_gate_close_angle=100,
          int feeder_gate_delay=100) {
            
            this->feeder_box_open_angle = feeder_box_open_angle;
            this->feeder_box_close_angle = feeder_box_close_angle;
            this->feeder_box_controller = new ServoController(
                feeder_box_pin,
                this->feeder_box_close_angle,
                MG90S_MIN_PWM,
                MG90S_MIN_PWM);
            this->feeder_gate_open_angle = feeder_gate_open_angle;
            this->feeder_gate_close_angle = feeder_gate_close_angle;
            this->feeder_gate_delay = feeder_gate_delay;
            this->feeder_gate_controller = new ServoController(
                feeder_gate_pin,
                this->feeder_gate_close_angle,
                MG90S_MIN_PWM,
                MG90S_MIN_PWM);
        };
        
        void setup() {
            
        }
        
        void feed(int gate_delay = -1) {
            feeder_gate_open();
            delay(gate_delay > 0 ? gate_delay : this->feeder_gate_delay);
            feeder_gate_close();
        }

        void feeder_gate_set_angle(int angle) {
            this->feeder_gate_controller->write(angle);
        }

        void feeder_gate_open() {
            this->feeder_gate_set_angle(this->feeder_gate_open_angle);
        }
        
        void feeder_gate_close() {
            this->feeder_gate_set_angle(this->feeder_gate_close_angle);
        }

        void feeder_box_set_angle(int angle) {
            this->feeder_box_controller->write(angle);
        }
        
        void feeder_box_open() {
            this->feeder_box_set_angle(this->feeder_box_open_angle);
        }
        
        void feeder_box_close() {
            this->feeder_box_set_angle(this->feeder_box_close_angle);
        }
};
