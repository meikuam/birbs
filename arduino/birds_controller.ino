#include "IRremote.h"
#include <Servo.h>
#include "ThreadHandler.h"

// leds control
#define DELAY_AFTER_SEND 20

class LedController {

    /*
   * incoming commands:
   * 10 - get state
   * 11 1 - set state to value (possible 1 - off, 2 - on)
   * 12 5 - set led_value to value (possible 1 - 255)
   * 
   * outcomming commands:
   * 0_0 - first number - led_state, second number - led_value
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
            IrReceiver.begin(this->ir_pin);
            
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
      /*
     * incoming commands:
     * 20 1 - get feeder box angle for first instance
     * 21 1 0 - set feeder box to angle for first instance
     * 22 1- enable feeder motor
     * 23 1 0 - enable feeder motor for number ms
     * 
     * outcomming commands:
     * 1_0 - feeder box angle for first instance
     */
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
        /*
     * incoming commands:
     * 30 1 - get drinker valves states for first instance
     * 31 1 0 - set drinker valve state (angle) for input of first instance
     * 32 1 0 - set drinker valve state (angle) for output of first instance
     * outcomming commands:
     * 1_0_0 - values for valves of first instance
     */
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

// led control
LedController* led_controller;

// feeder control
FeederController** feeder_controllers;

// drinker control
DrinkerController** drinker_controllers;


void setup() {
    Serial.begin(115200);

    // led control
    led_controller = new LedController(2, 3);

    // feeder control
    feeder_controllers = new FeederController*[2];
    feeder_controllers[0] = new FeederController(4, 5);
    feeder_controllers[1] = new FeederController(6, 7);

    // drinker control
    drinker_controllers = new DrinkerController*[2];
    drinker_controllers[0] = new DrinkerController(8, 9);
    drinker_controllers[1] = new DrinkerController(10, 11);
}


void loop() {
  // TODO: https://arduino.stackexchange.com/questions/439/why-does-starting-the-serial-monitor-restart-the-sketch
  if (Serial.available()) {
      int command_id = Serial.parseInt();
      switch (command_id) {
          case 10: {
              if (led_controller->led_state) {
                  Serial.print("1_");
              } else {
                  Serial.print("0_");
              }
              Serial.print(led_controller->led_value);
              Serial.print("\r\n");
              break;
          }
          case 11: {
              int argument = Serial.parseInt();
              if (argument == 1) {
                  led_controller->set_led_state(false);
              } else if (argument == 2){
                  led_controller->set_led_state(true);
              }
              break;
          }
          case 12: {
              int argument = Serial.parseInt();
              if (argument > 0) {
                  led_controller->set_led_value(argument);
              }
              break;
          }

          case 20: {
              int argument = Serial.parseInt();
              switch (argument) {
                  case 1: {
                      Serial.print("0_");
                      Serial.print(feeder_controllers[0]->feeder_box_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
                  case 2: {
                      Serial.print("1_");
                      Serial.print(feeder_controllers[1]->feeder_box_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
              }
          }
          case 21: {
              int argument1 = Serial.parseInt();
              int argument2 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      if (argument2 > 0) {
                          feeder_controllers[0]->feeder_box_controller->write(argument2);
                      }
                      break;
                  }
                  case 2: {
                      if (argument2 > 0) {
                          feeder_controllers[1]->feeder_box_controller->write(argument2);
                      }
                      break;
                  }
              }
          }
          case 22: {
              int argument = Serial.parseInt();
              switch (argument) {
                  case 1: {
                      feeder_controllers[0]->feed();
                      break;
                  }
                  case 2: {
                      feeder_controllers[1]->feed();
                      break;
                  }
              }
          }
          case 23: {
              int argument1 = Serial.parseInt();
              int argument2 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      if (argument2 > 0) {
                          feeder_controllers[0]->feed(argument2);                      
                      }
                      break;
                  }
                  case 2: {
                      if (argument2 > 0) {
                          feeder_controllers[1]->feed(argument2);
                      }
                      break;
                  }
              }
          }

          case 30: {
              int argument = Serial.parseInt();
              switch (argument) {
                  case 1: {
                      Serial.print("0_");
                      Serial.print(drinker_controllers[0]->input_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[0]->output_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
                  case 2: {
                      Serial.print("0_");
                      Serial.print(drinker_controllers[1]->input_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[1]->output_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
              }
          }
          case 31: {
              int argument1 = Serial.parseInt();
              int argument2 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      if (argument2 > 0) {
                          drinker_controllers[0]->input_controller->write(argument2);
                      }
                      break;
                  }
                  case 2: {
                      if (argument2 > 0) {
                          drinker_controllers[1]->input_controller->write(argument2);
                      }
                      break;
                  }
              }
          }
          case 32: {
              int argument1 = Serial.parseInt();
              int argument2 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      if (argument2 > 0) {
                          drinker_controllers[0]->output_controller->write(argument2);
                      }
                      break;
                  }
                  case 2: {
                      if (argument2 > 0) {
                          drinker_controllers[1]->output_controller->write(argument2);
                      }
                      break;
                  }
              }
          }
          default: {
            Serial.println("unsupported");
            break;
          }
      }
  }
  led_controller->ir_decode();
}
