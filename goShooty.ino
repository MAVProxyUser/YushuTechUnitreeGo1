#include <map>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
esp_spp_sec_t sec_mask=ESP_SPP_SEC_NONE;
esp_spp_role_t role=ESP_SPP_ROLE_SLAVE;
String readString;
int count = 0;

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(115200);
  if(! SerialBT.begin("Unitree pew pew switch", true) ) {
    Serial.println("========== serialBT failed!");
    abort();
  }

  uint8_t addr[6] = {0x98, 0xda, 0x10, 0x01, 0x18, 0x4e};
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
      if (content != "") {
        //Serial.println(content);
        byte a = content[16];
        //Serial.print(a, HEX);
        //Serial.println();
        if(a == 0x10)
        {
          count = count+1;
          Serial.println("pew pew pew!");
          if (count >= 5)
          { 
            count = 0;
            digitalWrite(13, HIGH);
            delay(2000);
            digitalWrite(13, LOW);
          }
          else
          {
            Serial.println(count);
          }
        }
        //else
        //{
        //  Serial.println("no pew pew"); 
        //}
      }
    }
  } 
}
