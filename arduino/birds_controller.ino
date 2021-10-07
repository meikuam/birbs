#include "IRremote.h"
#include <Servo.h>

// leds control
#define DELAY_AFTER_SEND 20

class LedController {

    /*
   * incoming commands:
   * 10 - get state
   * 10_0 - set state to 0
   * 11 - get led_value
   * 11_0 - set led_value
   * 
   * outcomming commands:
   * 0_0 - state is 0
   * 1_0 - led_value is 0
   */
    private:
    public:
        const uint16_t IR_ADDRESS = 0x0080;
        const uint8_t IR_COMMANDS[6] =  {
            0x12, // on/off      // 0
            0x1E, // mode        // 1
            0x4,  // up bridges  // 2
            0x6,  // down bridges// 3
            0xA,  // slow        // 4
            0x1F  // rapide      // 5
        };
        const uint8_t IR_DELAY_AFTER_RECIEVE = 200;
        uint8_t ir_pin;
        uint8_t led_pin;
      
        bool led_state = false;
        uint8_t led_value = 5;
        uint8_t led_step = 5;
        LedController(
          uint8_t ir_pin, 
          uint8_t led_pin, 
          uint8_t led_step = 5) {
            this->ir_pin = ir_pin;
            this->led_pin = led_pin;
            this->led_step = led_step;
            
            pinMode(this->led_pin, OUTPUT);
            IrReceiver.begin(this->ir_pin, ENABLE_LED_FEEDBACK);
            
            this->set_led();
        };
    
        void set_led() {
            if (this->led_state) {
                analogWrite(this-led_pin, this->led_value);
            } else {
                analogWrite(this->led_pin, 0);
            }
        }
    
        void set_led_value(byte value) {
            this->led_value = value;
            this->set_led();
        }

        void set_led_state(bool state) {
            this->led_state = state;
            this->set_led();
        }

        void up_leds() {
            this->led_value = min(this->led_value + this->led_step, 255);
            this->set_led();
        }

        void down_leds() {
            this->led_value = max(this->led_value - this->led_step, this->led_step);
            this->set_led();
        }

        void led_switch() {
            this->led_state = !this->led_state;
            this->set_led();
        }

        void ir_decode() {
            if (IrReceiver.decode()) {
                if (IrReceiver.decodedIRData.address == this->IR_ADDRESS) {
                    for (int command_index = 0; command_index < 6; command_index++) {
                        if (IrReceiver.decodedIRData.command == this->IR_COMMANDS[command_index]) {
                            switch (command_index) {
                                case 0: {
                                  this->led_switch();
                                  break;
                                }
                                case 2: {
                                  this->up_leds();
                                  break;
                                }
                                case 3: {
                                  this->down_leds();
                                  break;
                                }
                            }
                            break; 
                        }
                    }
                }
            }
            delay(IR_DELAY_AFTER_RECIEVE);
            IrReceiver.resume();
        }
};

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

        void write(int angle) {
            this->servo_angle = angle;
            this->servo.write(this->servo_angle);
        }
};


class FeederController {
    private:
    public:
        ServoController* feeder_box_controller;
        int open_feeder_angle;
        int close_feeder_angle;

        uint8_t feeder_motor_pin;
        int feeder_motor_delay = 1000;

        FeederController(
          uint8_t feeder_box_pin, 
          uint8_t feeder_motor_pin, 
          int open_feeder_angle=10, 
          int close_feeder_angle=100) {
            this->open_feeder_angle = open_feeder_angle;
            this->close_feeder_angle = close_feeder_angle;
            this->feeder_box_controller = new ServoController(feeder_box_pin);
            this->feeder_motor_pin = feeder_motor_pin;
            pinMode(this->feeder_motor_pin, OUTPUT);
        };

        void feed(int motor_delay = -1) {
            digitalWrite(this->feeder_motor_pin, HIGH);
            if (motor_delay > 0){
                delay(motor_delay); 
            } else{
                delay(this->feeder_motor_delay);
            }
            digitalWrite(this->feeder_motor_pin, LOW);
        }

        void set_feeder_box_angle(int angle) {
            this->feeder_box_controller->write(angle);
        }
        void open() {
            this->set_feeder_box_angle(this->open_feeder_angle);
        }
        
        void close() {
            this->set_feeder_box_angle(this->open_feeder_angle);
        }
};
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

        DrinkerController(
          uint8_t input_pin, 
          uint8_t output_pin,
          int input_open_angle=120,
          int input_close_angle=0,
          int output_open_angle=120,
          int output_close_angle=0) {
            this->input_open_angle = input_open_angle;
            this->input_close_angle = input_close_angle;
            this->output_open_angle = output_open_angle;
            this->output_close_angle = output_close_angle;
            this->input_controller = new ServoController(input_pin);
            this->output_controller = new ServoController(output_pin);
        };

        void set_input_angle(int angle) {
            this->input_controller->write(angle);
        }
        void set_output_angle(int angle) {
            this->input_controller->write(angle);
        }
        void open_input() {
          this->set_input_angle(this->input_open_angle);
        }
        void close_input() {
          this->set_input_angle(this->input_close_angle);
        }
        void open_output() {
          this->set_output_angle(this->output_open_angle);
        }
        void close_output() {
          this->set_output_angle(this->output_close_angle);
        }
        
};



//const int pin_servo1 = 3;
//const int pin_servo2 = 5;
//const int feeder_motor3 = 2;
//const int feeder_motor4 = 4;
//
//
//int angle1 = 0;
//int angle2 = 0;
//int dir = 1;


void setup() {
    Serial.begin(115200);

    // led control
    LedController led_controller(2, 5);

    // feeder control
    FeederController feeder_controller1(3, 4);
    FeederController feeder_controller2(6, 7);

    // drinker control
    DrinkerController drinker_controller1(8, 9);
    DrinkerController drinker_controller2(10, 11);
//
//  
////  valve1.attach(pin_servo, 500, 2500); // mg995 600-2000 µs
//  
//  valve1.attach(pin_servo1, 400, 2500); // mg90s 400-2400 µs
//  valve2.attach(pin_servo2, 400, 2500); // mg90s 400-2400 µs
//  pinMode(feeder_motor3, OUTPUT);
//  pinMode(feeder_motor4, OUTPUT);
//  
//  delay(10);
////  angle = valve1.read();
}

void loop() {
  if (Serial.available()) {
//    int servo_id = Serial.parseInt();
//    if (servo_id == 1) {
//      angle1 = Serial.parseInt();
//      valve1.write(angle1);
//      delay(10);
//      Serial.println("servoid 1");
//    } else if (servo_id == 2) {
//      angle2 = Serial.parseInt();
//      valve2.write(angle2);
//      delay(10);
//      Serial.println("servoid 3");
//    } else if (servo_id == 3) {
//      Serial.println("motor 3");
//      digitalWrite(feeder_motor3, HIGH);
//      delay(5000);
//      digitalWrite(feeder_motor3, LOW);
////      int mode = Serial.parseInt();
////      if (mode == 0) {
////        digitalWrite(feeder_motor3, LOW);
////      } else {
////        digitalWrite(feeder_motor3, HIGH);
////      }
//    } else if (servo_id == 4) {
//      Serial.println("motor 4");
//      
//      digitalWrite(feeder_motor4, HIGH);
//      delay(5000);
//      digitalWrite(feeder_motor4, LOW);
////      int mode = Serial.parseInt();
////      if (mode == 0) {
////        digitalWrite(feeder_motor4, LOW);
////      } else {
////        digitalWrite(feeder_motor4, HIGH);
////      }
//    }
  }
  led_controller.ir_decode();
}
