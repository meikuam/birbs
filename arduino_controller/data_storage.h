#pragma once
#define DATA_STORAGE_MAX_LENGTH 64

class DataStorage {
  public:
    uint8_t data[DATA_STORAGE_MAX_LENGTH];         // pointer to data stored
    uint8_t data_length;   // length of stored data
    uint8_t data_iterator; // iterator to current position in data

    DataStorage() {
      this->reset();
    }
    void reset() {
      this->data_length = 0;
      this->data_iterator = 0;
    }
    void set(uint8_t* data, uint8_t len) {
      for(int i = 0; i < len; i++) {
        this->data[i] = data[i];
      }
//       memcpy(this->data, data, sizeof(data) * len);
    }
    
    void add(uint8_t data) {
       this->data[this->data_length++] = data;
    }
    
};
