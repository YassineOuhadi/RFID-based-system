#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>

#define RST_PIN         9
#define SS_PIN          10

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600);
  while (!Serial);
  SPI.begin();
  lcd.begin(16, 2);
  lcd.print("Hello World!");
  mfrc522.PCD_Init();
  delay(4);
  mfrc522.PCD_DumpVersionToSerial();
  Serial.println("Scan PICC to see UID, SAK, type, and data blocks...");
}

void loop() {
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Store RFID code in a string
  String rfid_code = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    rfid_code += String(mfrc522.uid.uidByte[i], HEX);
  }

  // Define the class name
  String class_name = "Amphi A1"; // Replace with the name of the class or amphi
  
  // Send RFID code and class name to PC via Serial
  Serial.print(rfid_code);
  Serial.print(",");
  Serial.println(class_name);

  // Halt PICC and wait for a new card
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  if (Serial.available() > 0) {
    String message = Serial.readString();
    lcd.clear();
    lcd.print(message);
  }
}
