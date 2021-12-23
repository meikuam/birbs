#include "ThreadHandler.h"
#include "spi_processor.h"
#include "drinker_controller.h"
#include "feeder_controller.h"
#include "ir_led_controller.h"

//TODO: add EEPROM saving of params

//Configures the interrupt timer ticks in us (1000 gives 1ms).
SET_THREAD_HANDLER_TICK(0);
//This macro configures which timer should be used for generating
//the interrupts driving the ThreadHandler.
THREAD_HANDLER(InterruptTimer::getInstance());

// led control
LedController* led_controller;

// feeder control
FeederController** feeder_controllers;

// drinker control
DrinkerController** drinker_controllers;

volatile SPIProcessor* spi_processor;

ISR (SPI_STC_vect)   //Inerrrput routine function
{
  SPDR = spi_processor->process_interrupt(SPDR);
}

void setup()
{
  
  Serial.begin(115200);
  Serial.setTimeout(100);
//  Serial.println("Start birds controller");
  
  // led control
  led_controller = new LedController(2, 4); // ir_pin = 2 (490Hz), led_pin = 4 (980Hz)
  led_controller->setup();

  // feeder control
  feeder_controllers = new FeederController*[2]; 
  // box_pin = 6, gate_pin = 5
  feeder_controllers[0] = new FeederController(
    6, 5,
    10, 105, 
    170, 105); 
  feeder_controllers[0]->setup();
   // box_pin = 7, gate_pin = 3
  feeder_controllers[1] = new FeederController(
    7, 3, 
    10, 95, 
    170, 105);
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
      65, 150, 
      65, 130); 
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
  spi_processor = new SPIProcessor(led_controller, feeder_controllers, 2, drinker_controllers, 2);
  spi_processor->slave_init();
  
  //start executing threads
  ThreadHandler::getInstance()->enableThreadExecution();
}

void loop(void)
{
  
//  noInterrupts();
//  interrupts();

//  led_controller->loop();
//
//  drinker_controllers[0]->run();
//  drinker_controllers[1]->run();
//
//  feeder_controllers[0]->loop();
//  feeder_controllers[1]->loop();
  
}
