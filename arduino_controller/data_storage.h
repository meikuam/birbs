#pragma once

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
