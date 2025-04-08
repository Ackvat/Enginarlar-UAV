#include <Arduino.h>
#include <WiFi.h>

const char *Apssid = "enginarlariha_AP";
const char *Appassword = "enginar-1337";

const char *Wifi_ssid = "Broccoli_Modem_2.4Ghz";
const char *Wifi_password = "Tprk-s2000";

String getMACAddressString(uint8_t *mac, size_t size){
    String macString = "";
    for (size_t i = 0; i < size; i++) {
        if (mac[i] < 16) {
            macString += "0";
        }
        macString += String(mac[i], HEX);
        if (i < size - 1) {
            macString += ":";
        }
    }
    macString.toUpperCase();
    return macString;
}

void WiFiStationConnected(WiFiEvent_t event, WiFiEventInfo_t info){
  Serial.print("İstemci ile bağlantı kuruluyor: ");

  Serial.print(getMACAddressString(info.wifi_ap_staipassigned.mac, sizeof(info.wifi_ap_staipassigned.mac)));
  Serial.print(" -> ");
  Serial.print(IPAddress(info.wifi_ap_staipassigned.ip.addr));
  Serial.print(" (DHCP)");

  Serial.println();
}

void WiFiSetupAP(){
  Serial.println("AP hazırlanıyor...");

  WiFi.mode(WIFI_AP);

  WiFi.softAP(Apssid, Appassword);
  IPAddress myIP = WiFi.softAPIP();

  Serial.print("AP IP adresi: ");
  Serial.println(myIP);
  
  Serial.println();
}

void WiFiConnectToStation(){
  Serial.print("İstasyona bağlanıyor: ");
  Serial.print(Wifi_ssid);

  WiFi.begin(Wifi_ssid, Wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("İstasyona bağlantı kuruldu!");
  Serial.print("İstasyondan alınan DHCP IP adresi: ");
  Serial.print(WiFi.localIP());
  
  Serial.println();
}



void setup() {
  Serial.begin(115200);

  WiFiConnectToStation();
  WiFiSetupAP();

  WiFi.onEvent(WiFiStationConnected, WiFiEvent_t::ARDUINO_EVENT_WIFI_AP_STAIPASSIGNED);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n'); input.trim();
    
    int separatorIndex = input.indexOf(' ');
    String command = (separatorIndex == -1) ? input : input.substring(0, separatorIndex);
    String arguments = (separatorIndex == -1) ? "" : input.substring(separatorIndex + 1);
  }
}