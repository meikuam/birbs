#include "drinker_controller.h"
#include "feeder_controller.h"
#include "ir_led_controller.h"


// led control
LedController* led_controller;

// feeder control
FeederController** feeder_controllers;

// drinker control
DrinkerController** drinker_controllers;


#define SCK_PIN   52 
#define MISO_PIN  50 
#define MOSI_PIN  51
#define SS_PIN    53 


enum CommandStatus {
  COMMAND_STATUS_SELECT,
  COMMAND_STATUS_ARGUMENT,
  COMMAND_STATUS_PROCESSING,
  COMMAND_STATUS_RESPONSE
};

enum CommandResponseStatus {
  COMMAND_RESPONSE_SELECT_SUCCESS = 0x69,
  COMMAND_RESPONSE_SELECT_ERROR = 0x70,
  COMMAND_RESPONSE_ARGUMENT_SUCCESS = 0x40,
  COMMAND_RESPONSE_ARGUMENT_ERROR = 0x41,
  COMMAND_RESPONSE_PROCESSING_SUCCESS = 0xAA,
  COMMAND_RESPONSE_PROCESSING_ERROR = 0xAB,
  COMMAND_RESPONSE_RESPONSE_ERROR = 0x54,
  
};

class DataStorage {
  public:
    uint8_t* data;         // pointer to data stored
    uint8_t data_length;   // length of stored data
    uint8_t data_iterator; // iterator to current position in data

    DataStorage(int max_length = 128) {
      this->data = new uint8_t[max_length];
      this->reset();
    }
    void reset() {
      this->data_length = 0;
      this->data_iterator = 0;
    }
    void set(uint8_t* data, uint8_t len) {
       memcpy(this->data, data, sizeof(data) * len);
    }
    
    void add(uint8_t data) {
       this->data[this->data_length++] = data;
    }
    
};

class SPIProcessor {
  public:
    DataStorage* data_storage;

    uint8_t command_id;
  
    CommandStatus command_status;
    
    SPIProcessor() {
      this->command_status = COMMAND_STATUS_SELECT;
      this->command_id = 0x00;
      this->data_storage = new DataStorage(128);
    };
  
    uint8_t process_interrupt(uint8_t spdr) {
      uint8_t spdr_buffer = spdr;

      // here we chouse commands
      //-----------------------------------------------------------------------
      if (this->command_status == COMMAND_STATUS_SELECT){
        switch(spdr_buffer) {
          case 0x10: { // get leds status
            this->command_id = 0x10;
            this->command_status = COMMAND_STATUS_PROCESSING;
            break;
          }
          case 0x11: { // set leds on off
            this->command_id = 0x11;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x12: { // set leds value
            this->command_id = 0x12;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x20: {  // get servo angle
            this->command_id = 0x20;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x21: {  // get feeder_box open and close angles
            this->command_id = 0x21;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x22: {  // set feeder_box open and close angles
            this->command_id = 0x22;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 3;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x23: {  // get feeder_gate open and close angles
            this->command_id = 0x23;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x24: {  // set feeder_gate open and close angles
            this->command_id = 0x24;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 3;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x25: {  // feeder box open
            this->command_id = 0x25;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x26: {  // feeder box close
            this->command_id = 0x26;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x27: {  // feeder box set angle
            this->command_id = 0x27;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 2;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x28: {  // feeder gate feed for ms
            this->command_id = 0x28;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 3;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x29: {  // feeder gate set angle
            this->command_id = 0x29;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 2;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x2A: {  // feeder gate open
            this->command_id = 0x2A;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x2B: {  // feeder gate close
            this->command_id = 0x2B;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x30: {  // get drinker servo angle and water level current
            this->command_id = 0x30;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x31: {  // get drinker input open close angles
            this->command_id = 0x31;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x32: {  // set drinker input open close angles
            this->command_id = 0x32;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 3;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x33: {  // get drinker output open close angles
            this->command_id = 0x33;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x34: {  // set drinker output open close angles
            this->command_id = 0x34;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 3;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x35: {  // get drinker water level params
            this->command_id = 0x35;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x36: {  // set drinker water level params
            this->command_id = 0x36;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 5;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x37: {  // drinker input open
            this->command_id = 0x37;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x38: {  // drinker input close
            this->command_id = 0x38;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x39: {  // drinker input set angle
            this->command_id = 0x3A;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 2;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3A: {  // drinker output open
            this->command_id = 0x3A;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3B: {  // drinker output close
            this->command_id = 0x3B;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3C: {  // drinker output set angle
            this->command_id = 0x3C;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 2;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3D: {  // drinker full
            this->command_id = 0x3D;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3E: {  // drinker empty
            this->command_id = 0x3E;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          case 0x3F: {  // drinker get water_level
            this->command_id = 0x3F;
            this->command_status = COMMAND_STATUS_ARGUMENT;
            this->data_storage->reset();
            this->data_storage->data_length = 1;
            return COMMAND_RESPONSE_SELECT_SUCCESS;
          }
          default: {
            this->command_id = 0x00;
            break;
          }
        }
      }
      // here we accept args, if needed
      //-----------------------------------------------------------------------
      if (this->command_status == COMMAND_STATUS_ARGUMENT) {
          if (this->data_storage->data_iterator < this->data_storage->data_length - 1) {
            this->data_storage->data[this->data_storage->data_iterator++] = spdr_buffer;
            return COMMAND_RESPONSE_ARGUMENT_SUCCESS;
          } else if (this->data_storage->data_iterator < this->data_storage->data_length) {
            this->data_storage->data[this->data_storage->data_iterator++] = spdr_buffer;
            this->command_status = COMMAND_STATUS_PROCESSING;
          } else {
            this->command_status = COMMAND_STATUS_PROCESSING;
          }
      }
      // here we process commands
      //-----------------------------------------------------------------------
      if (this->command_status == COMMAND_STATUS_PROCESSING) {
        switch(this->command_id) {
          case 0x10: { // get leds status
            this->data_storage->reset();
            this->data_storage->add(led_controller->led_state? 0x2 : 0x1);
            this->data_storage->add(led_controller->led_value);
            this->command_status = COMMAND_STATUS_RESPONSE;
            break;
          }
          case 0x11: { // set leds on off
            switch (this->data_storage->data[0]) {
              case 0x1: {
                led_controller->set_led_state(false);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                led_controller->set_led_state(true);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x12: { // set leds value
            led_controller->set_led_value(this->data_storage->data[0]);
            this->command_status = COMMAND_STATUS_SELECT;
            return COMMAND_RESPONSE_PROCESSING_SUCCESS;
          }
          case 0x20: { // get feeder servo angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[0]->feeder_box_controller->servo_angle);
                this->data_storage->add(feeder_controllers[0]->feeder_gate_controller->servo_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[1]->feeder_box_controller->servo_angle);
                this->data_storage->add(feeder_controllers[1]->feeder_gate_controller->servo_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x21: { // get feeder_box open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[0]->feeder_box_open_angle);
                this->data_storage->add(feeder_controllers[0]->feeder_box_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[1]->feeder_box_open_angle);
                this->data_storage->add(feeder_controllers[1]->feeder_box_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x22: { // set feeder_box open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_box_open_angle = this->data_storage->data[1];
                feeder_controllers[0]->feeder_box_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_box_open_angle = this->data_storage->data[1];
                feeder_controllers[1]->feeder_box_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x23: {  // get feeder_gate open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[0]->feeder_gate_open_angle);
                this->data_storage->add(feeder_controllers[0]->feeder_gate_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(feeder_controllers[1]->feeder_gate_open_angle);
                this->data_storage->add(feeder_controllers[1]->feeder_gate_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x24: { // set feeder_gate open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_gate_open_angle = this->data_storage->data[1];
                feeder_controllers[0]->feeder_gate_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_gate_open_angle = this->data_storage->data[1];
                feeder_controllers[1]->feeder_gate_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x25: { // feeder box open
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_box_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_box_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x26: { // feeder box close
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_box_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_box_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x27: { // feeder box set angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_box_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_box_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x28: {// feeder gate feed for ms
            switch (this->data_storage->data[0]) {
              case 0x1: {
                int feed_delay = (int)this->data_storage->data[1]<<8 | (int)this->data_storage->data[2];
                feeder_controllers[0]->feed_async(feed_delay);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                int feed_delay = (int)this->data_storage->data[1]<<8 | (int)this->data_storage->data[2];
                feeder_controllers[1]->feed_async(feed_delay);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x29: { // feeder gate set angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_gate_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_gate_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x2A: { // feeder gate open
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_gate_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_gate_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x2B: { // feeder gate close
            switch (this->data_storage->data[0]) {
              case 0x1: {
                feeder_controllers[0]->feeder_gate_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                feeder_controllers[1]->feeder_gate_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x30: { // get drinker servo angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[0]->input_controller->servo_angle);
                this->data_storage->add(drinker_controllers[0]->output_controller->servo_angle);
                this->data_storage->add(drinker_controllers[0]->water_level_current);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[1]->input_controller->servo_angle);
                this->data_storage->add(drinker_controllers[1]->output_controller->servo_angle);
                this->data_storage->add(drinker_controllers[1]->water_level_current);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x31: { // get drinker input open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[0]->input_open_angle);
                this->data_storage->add(drinker_controllers[0]->input_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[1]->input_open_angle);
                this->data_storage->add(drinker_controllers[1]->input_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x32: { // set drinker input open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->input_open_angle = this->data_storage->data[1];
                drinker_controllers[0]->input_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->input_open_angle = this->data_storage->data[1];
                drinker_controllers[1]->input_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x33: { // get drinker output open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[0]->output_open_angle);
                this->data_storage->add(drinker_controllers[0]->output_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[1]->output_open_angle);
                this->data_storage->add(drinker_controllers[1]->output_close_angle);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x34: { // set drinker output open and close angles
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->output_open_angle = this->data_storage->data[1];
                drinker_controllers[0]->output_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->output_open_angle = this->data_storage->data[1];
                drinker_controllers[1]->output_close_angle = this->data_storage->data[2];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x35: { // get drinker water level params
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[0]->water_level_measure_iterations);
                this->data_storage->add(drinker_controllers[0]->water_level_max_cm_distance);
                this->data_storage->add(drinker_controllers[0]->water_level_max_level);
                this->data_storage->add(drinker_controllers[0]->water_level_min_level);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[1]->water_level_measure_iterations);
                this->data_storage->add(drinker_controllers[1]->water_level_max_cm_distance);
                this->data_storage->add(drinker_controllers[1]->water_level_max_level);
                this->data_storage->add(drinker_controllers[1]->water_level_min_level);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x36: { // set drinker water level params
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->water_level_measure_iterations = this->data_storage->data[1];
                drinker_controllers[0]->water_level_max_cm_distance = this->data_storage->data[2];
                drinker_controllers[0]->water_level_max_level = this->data_storage->data[3];
                drinker_controllers[0]->water_level_min_level = this->data_storage->data[4];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->water_level_measure_iterations = this->data_storage->data[1];
                drinker_controllers[1]->water_level_max_cm_distance = this->data_storage->data[2];
                drinker_controllers[1]->water_level_max_level = this->data_storage->data[3];
                drinker_controllers[1]->water_level_min_level = this->data_storage->data[4];
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x37: { // drinker input open
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->input_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->input_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x38: { // drinker input close
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->input_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->input_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x39: { //  drinker input set angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->input_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->input_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3A: { // drinker ouput open
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->output_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->output_open();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3B: { // drinker output close
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->output_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->output_close();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3C: { //  drinker output set angle
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->output_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->output_set_angle(this->data_storage->data[1]);
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3D: { // drinker fill
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->fill_async();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->fill_async();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3E: { // drinker empty
            switch (this->data_storage->data[0]) {
              case 0x1: {
                drinker_controllers[0]->empty_async();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                drinker_controllers[1]->empty_async();
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          case 0x3F: { // get drinker water level params
            switch (this->data_storage->data[0]) {
              case 0x1: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[0]->water_level_current);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              case 0x2: {
                this->data_storage->reset();
                this->data_storage->add(drinker_controllers[1]->water_level_current);
                this->command_status = COMMAND_STATUS_RESPONSE;
                return COMMAND_RESPONSE_PROCESSING_SUCCESS;
              }
              default: {
                this->command_status = COMMAND_STATUS_SELECT;
                return COMMAND_RESPONSE_PROCESSING_ERROR;
              }
            }
            break;
          }
          default: {
            break;
          }
        }
      }
      // here we responce to commands
      //-----------------------------------------------------------------------
      if (this->command_status == COMMAND_STATUS_RESPONSE) {
          if (this->data_storage->data_iterator < this->data_storage->data_length - 1) {
            return this->data_storage->data[this->data_storage->data_iterator++];
          } else if (this->data_storage->data_iterator < this->data_storage->data_length) {
            this->command_status = COMMAND_STATUS_SELECT;
            return this->data_storage->data[this->data_storage->data_iterator++];
          } else {
            this->command_status = COMMAND_STATUS_SELECT;
          }
      }
      return spdr_buffer;
    }
    
    void slave_init() {
          /*  
         * Setup SPI control register SPCR
         * SPCR
         * | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
         * | SPIE | SPE  | DORD | MSTR | CPOL | CPHA | SPR1 | SPR0 |
         * SPIE - Enables the SPI interrupt when 1 
         * SPE - Enables the SPI when 1
         * DORD - Sends data least Significant Bit First when 1, most Significant Bit first when 0
         * MSTR - Sets the Arduino in master mode when 1, slave mode when 0 
         * CPOL - Sets the data clock to be idle when high if set to 1, idle when low if set to 0
         * CPHA - Samples data on the trailing edge of the data clock when 1, leading edge when 0
         * SPR1 and SPR0 - Sets the SPI speed, 00 is fastest (4MHz) 11 is slowest (250KHz)   - in slave mode ignored
         */
  
         /*
          * SPI mode:
          * Mode       Clock Polarity (CPOL) Clock Phase (CPHA)  Output Edge   Data Capture
          * SPI_MODE0  0                     0                   Falling       Rising
          * SPI_MODE1  0                     1                   Rising        Falling
          * SPI_MODE2  1                     0                   Rising        Falling
          * SPI_MODE3  1                     1                   Falling       Rising
          * 
          * SPSR - (Status Register)
          * SPIF  WCOL  - - - - - -
          * SPIF - SPI Interrupt Flag set to 1 if SPIE set to 1 generates interrrupt 
          * WCOL - Write Collision flag set to 1 if while transfer data SPDR register was writed
          * 
          * 
          * SPDR - (SPI Data Register)
          */
          
      pinMode(SCK_PIN, INPUT);
      pinMode(MOSI_PIN, INPUT);
      pinMode(MISO_PIN, OUTPUT);
      pinMode(SS_PIN, INPUT_PULLUP);
    
  
      bitSet(SPCR, SPIE);
      bitSet(SPCR, SPE);
      bitClear(SPCR, DORD);
      bitClear(SPCR, MSTR);
      
      // use SPI_MODE0
      bitClear(SPCR, CPOL);
      bitClear(SPCR, CPHA);
      
      bitSet(SPCR, SPR0);
      bitClear(SPCR, SPR1);
  }
};


volatile SPIProcessor* spi_processor;

ISR (SPI_STC_vect)   //Inerrrput routine function
{
  SPDR = spi_processor->process_interrupt(SPDR);
}

void setup()
{
  
  Serial.begin(115200);
  Serial.setTimeout(100);
  Serial.println("Start birds controller");
  
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
    
  // spi init
  spi_processor = new SPIProcessor();
  spi_processor->slave_init();
}

void loop(void)
{
//  noInterrupts();
//  interrupts();

  led_controller->loop();

  drinker_controllers[0]->loop();
  drinker_controllers[1]->loop();

  feeder_controllers[0]->loop();
  feeder_controllers[1]->loop();
  
}
