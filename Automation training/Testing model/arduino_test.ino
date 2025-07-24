#define LED_PIN 13
String firmwareVersion = "v1.0.0";

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(57600);
  
  // Print firmware version on boot
  Serial.println("Firmware Version: " + firmwareVersion);
}

void loop() {
  // Turn ON LED
  digitalWrite(LED_PIN, HIGH);
  Serial.println("LED ON");
  delay(5000);
  
  // Turn OFF LED
  digitalWrite(LED_PIN, LOW);
  Serial.println("LED OFF");
  delay(5000); // Optional: pause before next cycle
}



