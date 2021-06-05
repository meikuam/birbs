#include "IRremote.h"

const byte LED_PIN = 5;
const byte IR_RECEIVE_PIN = 2;
const byte ir_delay_after_recieve = 100;


uint16_t sAddress = 0x0080;
uint8_t sCommands[6] =  {
  0x12, // on/off      // 0
  0x1E, // mode        // 1
  0x4,  // up bridges  // 2
  0x6,  // down bridges// 3
  0xA,  // slow        // 4
  0x1F  // rapide      // 5
  };
uint8_t sRepeats = 0;

bool led_state = false;
byte led_value = 0;

/*
 * 
 * incoming commands:
// * 0 - on/off
// * 2 - up bridges
// * 3 - down bridges
 * 10 - get state
 * 10_0 - set state to 0
 * 11 - get led_value
 * 11_0 - set led_value
 * 
 * outcomming commands:
 * 0_0 - state is 0
 * 1_0 - led_value is 0
 */

void set_led(){
  if (led_state) {
    analogWrite(LED_PIN, led_value);
  } else {
    analogWrite(LED_PIN, 0);
  }
}

void setup() {
    Serial.begin(9600);
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
  if(Serial.available()) {
    String incoming_command = Serial.readString();
    
    int space_index = incoming_command.indexOf("_");
    
    if (space_index > 0) { // two words command
      int command = incoming_command.substring(0, space_index).toInt();
      int argument = incoming_command.substring(space_index + 1, incoming_command.length()).toInt();

      switch (command) {
//        case 0: {
//          led_state = !led_state;
//          set_led();
//          break;
//        }
//        case 2: {
//          led_value = min(led_value + 5, 255);
//          set_led();
//          break;
//        }
//        case 3: {
//          led_value = max(led_value - 5, 0);
//          set_led();
//          break;
//        }
        case 10: {
          led_state = argument;
          set_led();
          break;
        }
        case 11: {
          led_value = min(max(argument, 0), 255);
          set_led();
          break;
        }
      }
    } else {
      int command = incoming_command.toInt();
      switch (command) {
//        case 0: {
//          led_state = !led_state;
//          set_led();
//          break;
//        }
//        case 2: {
//          led_value = min(led_value + 5, 255);
//          set_led();
//          break;
//        }
//        case 3: {
//          led_value = max(led_value - 5, 0);
//          set_led();
//          break;
//        }
        case 10: {
          
          if (led_state)
              Serial.print("0_1\r\n");
          else
              Serial.print("0_0\r\n");
          break;
        }
        case 11: {
          Serial.print("1_");
          Serial.print(led_value);
          Serial.print("\r\n");
          break;
        }
      }
    }
  }
   if (IrReceiver.decode())
   {
      if (IrReceiver.decodedIRData.address == sAddress) {
        for (int command_index = 0; command_index < 6; command_index++) {
             if (IrReceiver.decodedIRData.command == sCommands[command_index]) {
                 switch (command_index) {
                    case 0: {
                      led_state = !led_state;
                      set_led();
//                      if (led_state)
//                          Serial.print("0_1\r\n");
//                      else
//                          Serial.print("0_0\r\n");
                      break;
                    }
                    case 2: {
                      led_value = min(led_value + 5, 255);
                      set_led();
//                      Serial.print("1_");
//                      Serial.print(led_value);
//                      Serial.print("\r\n");
                      break;
                    }
                    case 3: {
                      led_value = max(led_value - 5, 0);
                      set_led();
//                      Serial.print("1_");
//                      Serial.print(led_value);
//                      Serial.print("\r\n");
                      break;
                    }
                 }
                 break; 
             }
        }
      }
      delay(ir_delay_after_recieve);
      IrReceiver.resume();
   }
}
