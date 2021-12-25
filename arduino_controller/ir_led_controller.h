#pragma once

 // leds control
class LedController {
    private:
    public:
        uint8_t led_pin;
      
        bool led_state = false;
        uint8_t led_value = 5;
        uint8_t led_step = 5;
        LedController(
          uint8_t led_pin, 
          uint8_t led_step = 5) {
            this->led_pin = led_pin;
            this->led_step = led_step;
        }
        virtual ~LedController() {
          
        }

        void setup() {
            pinMode(this->led_pin, OUTPUT);
            this->set_led();
        }
        virtual void run() {
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
};
