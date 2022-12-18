#include <SimpleBLE.h>

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

void setup() {
  pinMode(13, OUTPUT); // Right relay
  Serial.begin(115200);
  Serial.println("========== serialBT failed!");

  Serial.println("connecting to 98da1001184e");
}

void loop() {
 
}
