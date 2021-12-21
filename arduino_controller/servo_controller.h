#pragma once
#include "ThreadHandler.h"
#include <Servo.h>

const int MG995_MIN_PWM = 400;
const int MG995_MAX_PWM = 2400;
const int MG995_ROTATION_SPEED = 200; //60° for 200ms

const int MG90S_MIN_PWM = 400;
const int MG90S_MAX_PWM = 2400; 
const int MG90S_ROTATION_SPEED = 100; //60° for 100ms

const int MG90S_METALL_MIN_PWM = 400;
const int MG90S_METALL_MAX_PWM = 2400; 
const int MG90S_METALL_ROTATION_SPEED = 100; //60° for 100ms


// feeder controler
class ServoController: public Thread {
  /*
   * mg995 600-2000 µs
   * mg90s 400-2400 µs
   */
    private:
    public:
        uint8_t servo_pin;
        int min_pwm;
        int max_pwm;
        int rotation_speed;
        Servo servo;
        int servo_angle = -1;
        bool servo_enabled = false;
        bool servo_going_detach = false;
        unsigned long rotation_time_ms = 0;
        unsigned long rotation_start_time_ms = 0;
        
        ServoController(
          uint8_t servo_pin, 
          int default_angle=-1, 
          int min_pwm=400, 
          int max_pwm=2400,
          int rotation_speed=100) : Thread(2, 1000, 0){
            this->servo_pin = servo_pin;
            this->min_pwm = min_pwm;
            this->max_pwm = max_pwm;
            this->rotation_speed = rotation_speed;
            this->attach();
            if (default_angle > 0) {
                this->write(default_angle);
            }
        };
        ~ServoController() {
          
        }
        virtual void run() {
          if (this->servo_going_detach) {
            ThreadInterruptBlocker blocker;
            if (abs(millis() - this->rotation_start_time_ms) >= this->rotation_time_ms) {
                this->detach();
                this->servo_going_detach = false;
            }
          }
        }

        void attach() {
            this->servo.attach(this->servo_pin, this->min_pwm, this->max_pwm);
            this->servo_enabled = true;
        }
        void detach() {
            this->servo_enabled = false;
            this->servo.detach();
        }

        void write(int angle, bool going_detach = false) {
            ThreadInterruptBlocker blocker;
            if (going_detach) {
              // measure rotation angle, if previous value is unknown or it has been disabled, suppose that it should make full rotation
              int rotation_angle = !this->servo_enabled || this->servo_angle == -1 ? 90 : abs(this->servo_angle - angle);
              // calculate rotation_time in ms for rotation_speed at 60° angle
              this->rotation_time_ms = (rotation_angle * this->rotation_speed) / 60.0;
              if (!this->servo_enabled) {
                  this->attach();
              }
              this->servo_angle = angle;
              this->servo.write(this->servo_angle);
              this->rotation_start_time_ms = millis();
              this->servo_going_detach = true;
            } else {
              this->servo_going_detach = false;
              if (!this->servo_enabled) {
                  this->attach();
              }
              this->servo_angle = angle;
              this->servo.write(this->servo_angle);
            }
        }
};
