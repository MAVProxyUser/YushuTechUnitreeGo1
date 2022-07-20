#include <Wire.h>
#include "Adafruit_TCS34725.h"

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

int relay = 10;

void setup() {
  // Pin for relay module set as output
  pinMode(relay, OUTPUT);
  digitalWrite(relay, LOW);
  Serial.begin(9600);

  if (tcs.begin()) 
  {
    Serial.println("Found sensor");
    tcs.setInterrupt(true);  // turn off LED
  } 
  else 
  {
    Serial.println("No TCS34725 found ... check your connections");
    while (1); // halt!
  }
  
}

void loop() {
  digitalWrite(relay, LOW);
  float red, green, blue;
  delay(60);  // takes 50ms to read

  tcs.getRGB(&red, &green, &blue); 
  Serial.print("R:\t"); Serial.print(int(red)); 
  Serial.print("\tG:\t"); Serial.print(int(green)); 
  Serial.print("\tB:\t"); Serial.print(int(blue));
  Serial.print("\n");  

  if ( int(red) >= 210 )
  {
    // Fire the relay
    digitalWrite(relay, HIGH);
    Serial.println("ON");
    delay(50);
    digitalWrite(relay, LOW);
    Serial.println("OFF");
    delay(50);
  }  
}

