#include <map>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
esp_spp_sec_t sec_mask=ESP_SPP_SEC_NONE;
esp_spp_role_t role=ESP_SPP_ROLE_SLAVE;
String readString;
int leftcount = 0;
int rightcount = 0;
int bothcount = 0;

void setup() {
  pinMode(13, OUTPUT); // Right relay
  pinMode(12, OUTPUT); // Left relay
  Serial.begin(115200);
  if(! SerialBT.begin("Unitree pew pew switch", true) ) {
    Serial.println("========== serialBT failed!");
    abort();
  }

  //uint8_t addr[6] = {0x98, 0xda, 0x10, 0x01, 0x19, 0xd1}; //Cherbini
  uint8_t addr[6] = {0x98, 0xda, 0x10, 0x01, 0x18, 0x4e}; // Tina
  Serial.println("connecting to 98da1001184e");
  SerialBT.connect(addr, 1, sec_mask, role);
}

void loop() {
  if(! SerialBT.isClosed() && SerialBT.connected()) 
  {
    if(SerialBT.available()) 
    {
      String content = "";
      char character;

      while(SerialBT.available()) 
      {
        character = SerialBT.read(); 
        content.concat(character);
      }
      if (content != "") 
      {
        //Serial.println(content);
        byte a = content[16];
        // Leave this here, without it we frequently get 
        // ASSERT_WARN(1 8), in lc_task.c at line 1409
        Serial.print(a, HEX);
        Serial.println();
        if(a == 0x30)
        {
          bothcount = bothcount+1;
          if (bothcount >= 5)
          { 
            Serial.println("Both: pew pew pew!");
            // reset counters! 
            bothcount = 0;
            rightcount = 0;
            leftcount = 0;
            // fire both relays off
            digitalWrite(13, HIGH);
            digitalWrite(12, HIGH);
            delay(2000);
            digitalWrite(13, LOW);
            digitalWrite(12, LOW);
          }
          else
          {
            Serial.print("Bothcount: ");
            Serial.println(bothcount);
          }
        }  
        else if (a == 0x20)
        {
          rightcount = rightcount+1;
          if (rightcount >= 5)
          {
            Serial.println("Right: pew pew pew");
            rightcount = 0;
            digitalWrite(13, HIGH);
            delay(2000);
            digitalWrite(13, LOW);
          }
          else
          {
            Serial.print("Rightcount: ");
            Serial.println(rightcount);
          }
        }
        else if (a == 0x10)
        {
          leftcount = leftcount+1;
          if (leftcount >= 5)
          {
            Serial.println("Left: pew pew pew");
            leftcount = 0;
            digitalWrite(12, HIGH);
            delay(2000);
            digitalWrite(12, LOW);
          }
          else
          {
            Serial.print("Leftcount: ");
            Serial.println(leftcount);
          }
        }
      }
    }
  } 
}


