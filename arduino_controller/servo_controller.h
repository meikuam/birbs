#pragma once

#include <Servo.h>
const int MG995_MIN_PWM = 400;
const int MG995_MAX_PWM = 2400;
const int MG90S_MIN_PWM = 400;
const int MG90S_MAX_PWM = 2400; 
const int MG90S_METALL_MIN_PWM = 400;
const int MG90S_METALL_MAX_PWM = 2400; 


// feeder controler
class ServoController {
  /*
   * mg995 600-2000 µs
   * mg90s 400-2400 µs
   */
    private:
    public:
        uint8_t servo_pin;
        int min_pwm;
        int max_pwm;
        Servo servo;
        int servo_angle = -1;
        ServoController(
          uint8_t servo_pin, 
          int default_angle=-1, 
          int min_pwm=400, 
          int max_pwm=2400) {
            this->servo_pin = servo_pin;
            this->min_pwm = min_pwm;
            this->max_pwm = max_pwm;
            this->servo.attach(this->servo_pin, this->min_pwm, this->max_pwm);
            if (default_angle > 0) {
                this->write(default_angle);
            }
        };

        void write(int angle, bool smart = true) {
            if (smart) {
              // TODO: make smart positioning of servo (to avoid jitter, shaking...)
                if (angle)
                this->servo_angle = angle;
                this->servo.write(this->servo_angle);
            } else {
                this->servo_angle = angle;
                this->servo.write(this->servo_angle);
            }
        }
};
