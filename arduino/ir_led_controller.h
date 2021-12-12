#pragma once
 
#define DELAY_AFTER_SEND 20
#include "IRremote.h"

 // leds control
class LedController {
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
        const uint8_t IR_DELAY_AFTER_RECIEVE = 10;
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
        };

        void setup() {
            pinMode(this->led_pin, OUTPUT);
            IrReceiver.begin(this->ir_pin, ENABLE_LED_FEEDBACK);
            this->set_led();
        }
        void loop() {
            this->ir_decode();
        }
        void set_led() {
            if (this->led_state) {
                analogWrite(this->led_pin, this->led_value);
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
                delay(this->IR_DELAY_AFTER_RECIEVE);
                IrReceiver.resume();
            }
        }
};
