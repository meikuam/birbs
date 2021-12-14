#pragma once
#include "ThreadHandler.h"
#include "servo_controller.h"



class FeederController: public Thread  {
    private:
    public:
        ServoController* feeder_box_controller;
        int feeder_box_open_angle;
        int feeder_box_close_angle;

        ServoController* feeder_gate_controller;
        int feeder_gate_open_angle;
        int feeder_gate_close_angle;
        int feeder_gate_delay = 100;
        int feeder_gate_delay_cache = 100;
        bool feed_flag = false;
        unsigned long time_val = 0;


        FeederController(
          uint8_t feeder_box_pin, 
          uint8_t feeder_gate_pin,
          int feeder_box_open_angle=10, 
          int feeder_box_close_angle=100,
          int feeder_gate_open_angle=150, 
          int feeder_gate_close_angle=100,
          int feeder_gate_delay=100) : Thread(3, 500, 0){
            
            this->feeder_box_open_angle = feeder_box_open_angle;
            this->feeder_box_close_angle = feeder_box_close_angle;
            this->feeder_box_controller = new ServoController(
                feeder_box_pin,
                this->feeder_box_close_angle,
                MG90S_MIN_PWM,
                MG90S_MAX_PWM);
            this->feeder_gate_open_angle = feeder_gate_open_angle;
            this->feeder_gate_close_angle = feeder_gate_close_angle;
            this->feeder_gate_delay = feeder_gate_delay;
            this->feeder_gate_controller = new ServoController(
                feeder_gate_pin,
                this->feeder_gate_close_angle,
                MG90S_METALL_MIN_PWM,
                MG90S_METALL_MAX_PWM);
        };
        virtual ~FeederController() {
           delete this->feeder_box_controller;
           delete this->feeder_gate_controller;
        }
        
        void setup() {
            
        }
        
        virtual void run() {
          if (feed_flag) {
            if (abs(millis() - time_val) >= feeder_gate_delay_cache) {
                feeder_gate_close();
                feed_flag = false;
            }
          }
        }
        void feed_async(int gate_delay = -1) {
          feeder_gate_delay_cache = gate_delay > 0 ? gate_delay : this->feeder_gate_delay;
          time_val = millis();
          feeder_gate_open();
          feed_flag = true;
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
