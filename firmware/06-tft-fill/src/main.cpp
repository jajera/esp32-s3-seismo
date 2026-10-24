#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

// Lab pin map — docs/index.md
static const int PIN_SDA = 8;
static const int PIN_SCL_I2C = 18;
static const uint8_t IMU_ADDR = 0x6A;
static const uint8_t REG_WHO_AM_I = 0x0F;

static const int TFT_SCK = 12;
static const int TFT_MOSI = 11;
static const int TFT_CS = 10;
static const int TFT_DC = 9;
static const int TFT_RST = 7;
// BL already tied to 3V3 in Phase 2

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

static uint8_t readWhoAmI() {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(REG_WHO_AM_I);
  if (Wire.endTransmission(false) != 0) {
    return 0;
  }
  if (Wire.requestFrom(IMU_ADDR, (uint8_t)1) != 1) {
    return 0;
  }
  return Wire.read();
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("seismo tft-fill — phase 6");
  Serial.printf("SPI SCK=%d MOSI=%d CS=%d DC=%d RST=%d  BL=3V3(phase2)\n",
                TFT_SCK, TFT_MOSI, TFT_CS, TFT_DC, TFT_RST);

  // Prove I2C still lives with SPI pins driven
  Wire.begin(PIN_SDA, PIN_SCL_I2C);
  Wire.setClock(400000);
  uint8_t who = readWhoAmI();
  Serial.printf("IMU WHO_AM_I=0x%02X (expect 0x6C) — buses coexist\n", who);

  SPI.begin(TFT_SCK, -1, TFT_MOSI, TFT_CS);
  tft.init(240, 320);
  tft.setRotation(0);
  tft.fillScreen(ST77XX_BLACK);
  Serial.println("cycling red → green → blue every 1 s");
}

void loop() {
  tft.fillScreen(ST77XX_RED);
  Serial.println("fill RED");
  delay(1000);
  tft.fillScreen(ST77XX_GREEN);
  Serial.println("fill GREEN");
  delay(1000);
  tft.fillScreen(ST77XX_BLUE);
  Serial.println("fill BLUE");
  delay(1000);
}
