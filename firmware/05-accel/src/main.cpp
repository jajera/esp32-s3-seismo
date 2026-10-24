#include <Arduino.h>
#include <Wire.h>
#include <math.h>

// Lab pin map — docs/index.md. Address from CS→3V3, SDO→GND.
static const int PIN_SDA = 8;
static const int PIN_SCL = 18;
static const uint8_t IMU_ADDR = 0x6A;

static const uint8_t REG_WHO_AM_I = 0x0F;
static const uint8_t REG_CTRL1_XL = 0x10;
static const uint8_t REG_CTRL3_C = 0x12;
static const uint8_t REG_OUTX_L_A = 0x28;
static const uint8_t WHO_AM_I_LSM6DSO = 0x6C;

// CTRL1_XL: ODR 104 Hz (0100), FS ±2 g (00) → 0x40
static const uint8_t CTRL1_XL_104HZ_2G = 0x40;
// ±2 g: 0.061 mg/LSB
static const float G_PER_LSB = 0.000061f;
static const float RAD2DEG = 57.2957795f;

static bool writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

static bool readRegs(uint8_t reg, uint8_t *buf, size_t n) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) {
    return false;
  }
  size_t got = Wire.requestFrom(IMU_ADDR, (uint8_t)n);
  if (got != n) {
    return false;
  }
  for (size_t i = 0; i < n; i++) {
    buf[i] = Wire.read();
  }
  return true;
}

static bool readAccelG(float *ax, float *ay, float *az) {
  uint8_t raw[6];
  if (!readRegs(REG_OUTX_L_A, raw, 6)) {
    return false;
  }
  int16_t x = (int16_t)((uint16_t)raw[1] << 8 | raw[0]);
  int16_t y = (int16_t)((uint16_t)raw[3] << 8 | raw[2]);
  int16_t z = (int16_t)((uint16_t)raw[5] << 8 | raw[4]);
  *ax = x * G_PER_LSB;
  *ay = y * G_PER_LSB;
  *az = z * G_PER_LSB;
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("seismo accel — phase 5");
  Serial.printf("SDA=GPIO%d SCL=GPIO%d addr=0x%02X\n", PIN_SDA, PIN_SCL, IMU_ADDR);

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);

  uint8_t who = 0;
  if (!readRegs(REG_WHO_AM_I, &who, 1)) {
    Serial.println("WHO_AM_I read failed");
    while (true) {
      delay(1000);
    }
  }
  Serial.printf("WHO_AM_I=0x%02X (expect 0x%02X)\n", who, WHO_AM_I_LSM6DSO);
  if (who != WHO_AM_I_LSM6DSO) {
    Serial.println("unexpected WHO_AM_I — halt");
    while (true) {
      delay(1000);
    }
  }

  writeReg(REG_CTRL3_C, 0x44);  // BDU + IF_INC
  if (!writeReg(REG_CTRL1_XL, CTRL1_XL_104HZ_2G)) {
    Serial.println("CTRL1_XL write failed");
    while (true) {
      delay(1000);
    }
  }
  delay(50);
  Serial.println("Watch pitch/roll (degrees) when you tilt — |a| stays ~1 on slow tilt");
}

void loop() {
  float ax, ay, az;
  if (!readAccelG(&ax, &ay, &az)) {
    Serial.println("accel read fail");
  } else {
    // Standard accel tilt (gravity vector). Slow tilt: |a|≈1, angles move a lot.
    float pitch = atan2f(-ax, sqrtf(ay * ay + az * az)) * RAD2DEG;
    float roll = atan2f(ay, az) * RAD2DEG;
    Serial.printf("ax=%+.2f ay=%+.2f az=%+.2f  pitch=%+.0f° roll=%+.0f°\n",
                  ax, ay, az, pitch, roll);
  }
  delay(200);
}
