//#include "ThreadHandler.h"

#include "drinker_controller.h"
#include "feeder_controller.h"
#include "ir_led_controller.h"


// led control
LedController* led_controller;

// feeder control
FeederController** feeder_controllers;

// drinker control
DrinkerController** drinker_controllers;


void setup() {
  /*

   * 11 - кран воды 2 input
   * 10 - кран воды 2 output
   * 9 - кран воды 1 output
   * 8 - кран воды 1 input
   * 7 - box 2
   * 6 - box 1
   * 5 - кормушка 1 сервопроивод подача корма
   * 4 - свет pwm (980Hz)
   * 3 - кормушка 2 сервопроивод подача корма
   * 2 - ir датчик (490Hz)
   * 
   * 44 - уровень воды 1 красный echo
   * 42 - уровень воды 1 черный trig
   * 
   * 45 - уровень воды 2 echo
   * 43 - уровень воды 2 trig
   */
   
    Serial.begin(115200);
    Serial.setTimeout(100);

    // led control
    led_controller = new LedController(2, 4); // ir_pin = 2 (490Hz), led_pin = 4 (980Hz)
    led_controller->setup();

    // feeder control
    feeder_controllers = new FeederController*[2]; 
    // box_pin = 6, gate_pin = 5
    feeder_controllers[0] = new FeederController(
      6, 5,
      10, 100, 
      150, 100); 
    feeder_controllers[0]->setup();
     // box_pin = 7, gate_pin = 3
    feeder_controllers[1] = new FeederController(
      7, 3, 
      10, 100, 
      150, 100);
    feeder_controllers[1]->setup();

    // drinker control
    drinker_controllers = new DrinkerController*[2];
    // args: 
    // input_pin = 8, output_pin = 9, 
    // water_level_trigger_pin = 42, water_level_echo_pin = 44, 
    // input_open = 60, input_close = 150, 
    // output_open = 60, output_close = 135
    drinker_controllers[0] = new DrinkerController(
        8, 9, 
        42, 44,
        60, 150, 
        60, 135); 
    drinker_controllers[0]->setup();
    
    // args: 
    // input_pin = 11, output_pin = 10, 
    // water_level_trigger_pin = 43, water_level_echo_pin = 45, 
    // input_open = 60, input_close = 150, 
    // output_open = 60, output_close = 135
    drinker_controllers[1] = new DrinkerController(
      11, 10, 
      43, 45,
      60, 150, 
      60, 135);
    drinker_controllers[1]->setup();
}


void loop() {
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
              Serial.println(argument);
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
                      Serial.print("_");
                      Serial.print(feeder_controllers[0]->feeder_gate_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
                  case 2: {
                      Serial.print("1_");
                      Serial.print(feeder_controllers[1]->feeder_box_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(feeder_controllers[1]->feeder_gate_controller->servo_angle);
                      Serial.print("\r\n");
                      break;
                  }
              }
              break;
          }
          case 21: {
              int argument1 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[0]->feeder_box_set_angle(argument2);
                      }
                      break;
                  }
                  case 2: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[1]->feeder_box_set_angle(argument2);
                      }
                      break;
                  }
              }
              break;
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
              break;
          }
          case 23: {
              int argument1 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[0]->feed(argument2);                      
                      }
                      break;
                  }
                  case 2: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[1]->feed(argument2);
                      }
                      break;
                  }
              }
              break;
          }
          case 24: {
              int argument1 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[0]->feeder_gate_set_angle(argument2);                      
                      }
                      break;
                  }
                  case 2: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          feeder_controllers[1]->feeder_gate_set_angle(argument2);
                      }
                      break;
                  }
              }
              break;
          }
          case 30: {
              int argument = Serial.parseInt();
              switch (argument) {
                  case 1: {
                      Serial.print("0_");
                      Serial.print(drinker_controllers[0]->input_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[0]->output_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[0]->water_level_current);
                      Serial.print("\r\n");
                      break;
                  }
                  case 2: {
                      Serial.print("0_");
                      Serial.print(drinker_controllers[1]->input_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[1]->output_controller->servo_angle);
                      Serial.print("_");
                      Serial.print(drinker_controllers[1]->water_level_current);
                      Serial.print("\r\n");
                      break;
                  }
              }
              break;
          }
          case 31: {
              int argument1 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          drinker_controllers[0]->input_set_angle(argument2);
                      }
                      break;
                  }
                  case 2: {
                      int argument2 = Serial.parseInt();
                      if (argument2 > 0) {
                          drinker_controllers[1]->input_set_angle(argument2);
                      }
                      break;
                  }
              }
              break;
          }
          case 32: {
              int argument1 = Serial.parseInt();
              int argument2 = Serial.parseInt();
              switch (argument1) {
                  case 1: {
                      if (argument2 > 0) {
                          drinker_controllers[0]->output_set_angle(argument2);
                      }
                      break;
                  }
                  case 2: {
                      if (argument2 > 0) {
                          drinker_controllers[1]->output_set_angle(argument2);
                      }
                      break;
                  }
              }
              break;
          }
          default: {
//            Serial.println("unsupported");
            break;
          }
      }
  }
  led_controller->ir_decode();
  drinker_controllers[0]->loop();
  drinker_controllers[1]->loop();
}
