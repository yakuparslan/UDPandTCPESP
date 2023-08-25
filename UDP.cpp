#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <OSCData.h>
#include <time.h>
#include <NTPClient.h>
#include <Notes.h>
#include <Preferences.h>

char ssid1[] = "totoo";       
char pass1[] = "totoo119*";

char ssid2[] = "Yakopsen";       
char pass2[] = "1234567890";
//Output Pin
int outputPin = GPIO_NUM_13;
// delay of motor 
int delayMotor = 30;

Preferences preferences;
//192.168.64.140
const IPAddress remoteIP(192,168,64,140); 
const unsigned int remotePort = 1234;  


// Structure to hold MAC address and device name
struct DeviceInfo {
  uint8_t mac[6];
  const char *name;
  int deviceNum;
};

// Array of device information
DeviceInfo devices[] = {
  {{0xA8, 0x42, 0xE3, 0xCD, 0xEE, 0x78}, "HR01",1},
  {{0xC8, 0xC9, 0xA3, 0xC9, 0xA1, 0x7C}, "HR02",2},
  {{0xA8, 0x42, 0xE3, 0xCD, 0x06, 0xE4}, "HR03",3},
  {{0xA8, 0x42, 0xE3, 0xCD, 0xF0, 0x10}, "HR04",4},
  {{0xA8, 0x42, 0xE3, 0xCC, 0xF8, 0xA4}, "HR05",5},
  {{0xA8, 0x42, 0xE3, 0xCD, 0xF5, 0xD4}, "HR06",6},
  {{0xC8, 0xC9, 0xA3, 0xCA, 0x7F, 0x68}, "HR07",7},
  {{0xA8, 0x42, 0xE3, 0xCD, 0xEF, 0xE0}, "HR08",8},
  {{0xA8, 0x42, 0xE3, 0xCD, 0xE4, 0x3C}, "HR09",9},
  {{0xA8, 0x42, 0xE3, 0xCD, 0xE7, 0xD4}, "HR10",10},
  {{0xA8, 0x42, 0xE3, 0xCD, 0x3F, 0xBC}, "HR11",11},
  {{0x78, 0xE3, 0x6D, 0x09, 0x5A, 0x38}, "HR12",12},
  {{0xA8, 0x42, 0xE3, 0xCE, 0x36, 0xB8}, "HR13",13},
  {{0xA8, 0x42, 0xE3, 0xCE, 0x14, 0x2C}, "HR14",14},
  {{0xA8, 0x42, 0xE3, 0xCE, 0xCF, 0x8C}, "HR15",15},
  {{0xB0, 0xA7, 0x32, 0xF1, 0x5B, 0x6C}, "HR16",16},
  {{0xB0, 0xA7, 0x32, 0xF1, 0x4B, 0xE8}, "HR17",17},
  {{0xA8, 0x42, 0xE3, 0xCD, 0x25, 0xD4}, "HR18",18},
  {{0xA8, 0x42, 0xE3, 0xCD, 0x2F, 0x34}, "HR19",19},
  {{0xB0, 0xA7, 0x32, 0xF1, 0x83, 0x50}, "HR20",20},
  {{0xC8, 0xC9, 0xA3, 0xCA, 0x98, 0xE8}, "HR21",21},
  {{0x3C, 0x06, 0x30, 0x02, 0xD2, 0x29}, "HR22",22},
};

// NTP settings
const char* ntpServer = "pool.ntp.org";
struct tm timeinfo;
int year,month,day,hour,minute,second;
int desiredHour = 16;
int desiredMinute = 5;
int desiredSecond = 0; 
int desiredAchieve=0;
String datetimeStr;

char packetBuffer[255]; 

// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;
const unsigned int localPort = 1234;       
// Find corresponding device name
const char *espDeviceName = nullptr;
int espDeviceNum = 0;
//It will react as play/stop button 
int play  = 0;
int start = 0;

int counter = 0;
// Default MotorState
int motorState = LOW;  

// Default BPM
int bpm = 120; 

// BPM -> Beat Per Minute -> one beat in miliseconds
long interval = 60000/bpm; 
unsigned long currentMillis = millis();
unsigned long begin = 0;
unsigned long previousMillis = 0; 

void Debug(const char* message){
    // Send UDP packet
    Udp.beginPacket(remoteIP, remotePort);
    Udp.write((uint8_t*)message, strlen(message));
    Udp.endPacket();

}

void connectToWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid1, pass1);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    if (attempts >= 10) {
      Serial.println("Unable to connect to first Wi-Fi network. Trying the second one...");
      break;
    }
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to Wi-Fi!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    WiFi.begin(ssid2, pass2);
    attempts = 0;
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
      if (attempts >= 10) {
        Serial.println("Unable to connect to second Wi-Fi network.");
        break;
      }

      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("Connected to Wi-Fi!");
      Serial.print("IP address: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("Unable to connect to any Wi-Fi network.");
    }
  }
}


String formatDateTime(int year, int month, int day, int hour, int minute, int second) {
    char datetimeStr[20]; // Allocate a char array to hold the formatted string
    sprintf(datetimeStr, "%04d%02d%02d-%02d:%02d:%02d", year, month, day, hour, minute, second);
    return String(datetimeStr);
}


void printLocalTime(){
  
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500);
    Serial.print(".");delay(500); 
    
    return;
  }
  year = timeinfo.tm_year+1900;
  day = timeinfo.tm_mday;
  month = timeinfo.tm_mon + 1;
  hour = timeinfo.tm_hour;
  minute = timeinfo.tm_min;
  second = timeinfo.tm_sec;
  datetimeStr = formatDateTime(year, month, day, hour, minute, second);
  Serial.println(datetimeStr); 
}


void setDevice(){
   // Get ESP32 MAC address
  uint8_t espMac[6];
  WiFi.macAddress(espMac);
  for (size_t i = 0; i < sizeof(devices) / sizeof(devices[0]); i++) {
    if (memcmp(espMac, devices[i].mac, sizeof(espMac)) == 0) {
      espDeviceName = devices[i].name;
      espDeviceNum  = devices[i].deviceNum; 
      break;
    }
  }
  if(espDeviceNum>=15){
    outputPin = GPIO_NUM_15;
  }

}


void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());
  setDevice();
  WiFi.setHostname(espDeviceName); //define hostname
  WiFi.mode(WIFI_STA);
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  connectToWiFi();
  

  Udp.begin(localPort);
  Serial.print("UDP Started: ");
  Serial.println(localPort);
  Serial.println("Size of the Notes Array: "+String(array_length));
  pinMode(outputPin, OUTPUT);
  digitalWrite(outputPin, motorState);
  configTime(7200, 0, ntpServer);
  printLocalTime();
  String d_start = datetimeStr+"----"+espDeviceName+" started.";
  Debug(d_start.c_str());

  preferences.begin("delay", false); // "my-app" is the namespace for your preferences
  int storedValue = preferences.getInt("storedValue", 0);
  if(storedValue!=0){delayMotor=storedValue;}
  Serial.print("Stored value: ");
  Serial.println(storedValue);




}



void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    String receiver = String(packetBuffer);
    printLocalTime();
    String d_send = datetimeStr+"----"+receiver;
    Debug(d_send.c_str());
    Serial.println(receiver);
    
    if (receiver == "STOP") {
        play  = 0;
        start = 0; 
        counter = 0;
        digitalWrite(outputPin, LOW);      
    }
    else if (receiver == "PUSH") {
        currentMillis=millis();
        while(millis()-currentMillis<=delayMotor) {
            digitalWrite(outputPin, HIGH); 
        }
            digitalWrite(outputPin,LOW);
    }
    else if (receiver.substring(0,5) == "DELAY") {
        delayMotor = receiver.substring(6).toInt();
    }
    else if (receiver == "RESET") {
        ESP.restart(); 
    }
    else if (receiver.substring(0,3) == "BPM")  {
        int new_bpm = receiver.substring(4).toInt();     
        if (bpm !=new_bpm&& new_bpm >=1 && new_bpm<=1000) {
              bpm = new_bpm;  
        }
    }
    else if (receiver == "REC" ) {
        play =1;
    }
    else if (receiver == "START" ) {
        start =1;
    }
    else if (receiver == "SAVE" ) {
        preferences.putInt("storedValue", delayMotor);
        preferences.end();
        printLocalTime();
        String saved = datetimeStr+"----"+ delayMotor+" Delay is saved.";
        Debug(saved.c_str());
    }
    else if (packetBuffer[0] == 'T' ) {
        // Extract the desired time from the packet
        char timeStr[9];
        strncpy(timeStr, packetBuffer + 1, 8);
        timeStr[8] = '\0';

        // Parse the desired time
        desiredHour   = atoi(timeStr);
        desiredMinute = atoi(timeStr + 3);
        desiredSecond = atoi(timeStr + 6);
        desiredAchieve=0;
        Serial.println(String(desiredHour)+":"+String(desiredMinute)+":"+String(desiredSecond));
      
    }
        receiver = "";
}

  getLocalTime(&timeinfo);
  if(timeinfo.tm_hour==desiredHour&&timeinfo.tm_min==desiredMinute&&timeinfo.tm_sec>=desiredSecond&&desiredAchieve==0){
    start=1;
    desiredAchieve=1;
    
  }
  if(play==1){
  interval = 60000/bpm; 
  currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        digitalWrite(outputPin, HIGH);
        delay(delayMotor);
        digitalWrite(outputPin, LOW); 
    }      
  }

  if(start==1){
    if(counter==0){
      begin=millis();
    }
    interval = notes_on[counter]; 
    currentMillis = millis();
    
    if (currentMillis - begin >= interval) {
      Serial.println(counter);
      digitalWrite(outputPin, HIGH);
      delay(delayMotor);
      // delay(notes_off[counter]-notes_on[counter]);
      digitalWrite(outputPin, LOW); 
      counter++; 
    }
    if(counter==array_length){
      start=0;
      counter=0;
    }   
  } 
    

}

