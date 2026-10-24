/*
 * Phase 7 — seismo intensity demo
 *
 * Detection: HP → energy → STA/LTA (EVENT). Intensity: Wald et al. 1999 PGA→MMI.
 * CUSTOMIZE knobs below. Docs: docs/phases/07-intensity-ui.md
 */
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <math.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

// =============================================================================
// CUSTOMIZE
// =============================================================================

static const int PIN_SDA = 8;
static const int PIN_SCL_I2C = 18;
static const int TFT_SCK = 12;
static const int TFT_MOSI = 11;
static const int TFT_CS = 10;
static const int TFT_DC = 9;
static const int TFT_RST = 7;
static const uint8_t IMU_ADDR = 0x6A;

// Sample rate the LSM6DSO is configured for (ODR). STA/LTA windows use this.
static const float SAMPLE_HZ = 104.0f;

// High-pass corner ~0.2 Hz: alpha ≈ 2π·fc / fs  (removes gravity / slow tilt)
static const float HP_ALPHA = 0.012f;

// STA ~0.5 s, LTA ~10 s (desk-friendly; field stations often use ~30 s LTA)
static const int N_STA = 52;     // 0.5 * 104
static const int N_LTA = 1040;   // 10 * 104 — raise toward 3120 for a quieter baseline
static const float LTA_MIN = 1e-10f;

// STA/LTA ratio: fire event / re-arm (hysteresis)
static const float RATIO_TRIGGER = 6.0f;
static const float RATIO_DETRIGGER = 2.0f;

// Peak |h| (g) over this window → MMI via Wald et al. 1999 (raw instrumental)
static const uint32_t PGA_WIN_MS = 400;
// Desk idle ~0.002–0.005 g — below quiet → MMI 0
static const float PGA_QUIET_G = 0.015f;
static const float CM_S2_PER_G = 980.665f;
// Imm = 3.66*log10(PGA_cm/s²) − 1.66; XII needs ~5.5 g → use ±8 g FS
static const float MMI_A = 3.66f;
static const float MMI_B = 1.66f;
static const float MMI_MAX = 12.0f;
static const float PGA_AT_MMI12_G = 5.48f;  // 10^((12+1.66)/3.66) / g₀

// Banner afterglow once the detector drops; max time locked in "triggered"
static const uint32_t EVENT_HOLD_MS = 500;
static const uint32_t TRIGGER_MAX_MS = 1200;

static const int WAVE_N = 200;
static const float WAVE_FULL_SCALE_G = 0.40f;
static const uint32_t UI_PERIOD_MS = 50;
static const uint32_t SERIAL_PERIOD_MS = 200;

// =============================================================================
static const uint8_t REG_WHO_AM_I = 0x0F;
static const uint8_t REG_CTRL1_XL = 0x10;
static const uint8_t REG_CTRL3_C = 0x12;
static const uint8_t REG_STATUS = 0x1E;
static const uint8_t REG_OUTX_L_A = 0x28;
static const uint8_t WHO_AM_I_LSM6DSO = 0x6C;
static const uint8_t STATUS_XLDA = 0x01;
// ±8 g @ 104 Hz — Wald XII needs ~5.5 g; ±2 g clips around MMI X
static const uint8_t CTRL1_XL_104HZ_8G = 0x4C;
static const float G_PER_LSB = 0.000244f;  // ±8 g datasheet

static const int TFT_W = 240;
static const int TFT_H = 320;
static const int WAVE_Y0 = 200;
static const int WAVE_H = 110;
static const int MMI_LEGEND_MAX = 12;  // MMI I … XII

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// --- STA/LTA detector state ---
static float dc_x = 0, dc_y = 0, dc_z = 1.0f;
static float sta = 0;
static float lta = LTA_MIN;
static bool armed = true;
static bool triggered = false;
static uint32_t sample_n = 0;
static bool warmup_done = false;

static float wave[WAVE_N];
static int wave_i = 0;
static float live_pga = 0;   // |h| this sample (g)
static float ratio = 0;
static float pga_g = 0;      // peak |h| in window
static float mmi = 0;
static bool event_on = false;
static uint32_t event_until = 0;
static uint32_t trigger_since = 0;
static uint32_t last_ui = 0;
static uint32_t last_serial = 0;
static float drawn_m = -999;
static bool drawn_event = false;
static bool drawn_warm = true;
static float drawn_pga = -1;
static float drawn_ratio = -1;

struct PeakSample {
  float mag;
  uint32_t t;
};
static PeakSample peaks[128];
static int peak_n = 0;
static int peak_i = 0;

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
  if (Wire.requestFrom(IMU_ADDR, (uint8_t)n) != n) {
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

static void pushPeak(float mag, uint32_t t) {
  peaks[peak_i] = {mag, t};
  peak_i = (peak_i + 1) % 128;
  if (peak_n < 128) {
    peak_n++;
  }
}

static float windowPga(uint32_t now) {
  float m = 0;
  for (int i = 0; i < peak_n; i++) {
    if (now - peaks[i].t <= PGA_WIN_MS && peaks[i].mag > m) {
      m = peaks[i].mag;
    }
  }
  return m;
}

// Wald et al. 1999: Imm = 3.66 log10(PGA_cm/s²) − 1.66. No desk fudge factor.
// Fit published ~V–VIII; we evaluate the same formula and clamp to I–XII.
static float pgaToMmi(float pga_g) {
  if (pga_g < PGA_QUIET_G) {
    return 0.0f;
  }
  if (pga_g >= PGA_AT_MMI12_G) {
    return MMI_MAX;
  }
  float pga_cm = pga_g * CM_S2_PER_G;
  if (pga_cm < 1.0f) {
    pga_cm = 1.0f;
  }
  float imm = MMI_A * log10f(pga_cm) - MMI_B;
  if (imm < 1.0f) {
    return 1.0f;
  }
  if (imm > MMI_MAX) {
    return MMI_MAX;
  }
  return imm;
}

// One sample through HP + STA/LTA. Returns true on rising-edge EVENT.
static bool processSample(float ax, float ay, float az, float *hz_out) {
  if (sample_n == 0) {
    dc_x = ax;
    dc_y = ay;
    dc_z = az;
  } else {
    dc_x += HP_ALPHA * (ax - dc_x);
    dc_y += HP_ALPHA * (ay - dc_y);
    dc_z += HP_ALPHA * (az - dc_z);
  }

  float hx = ax - dc_x;
  float hy = ay - dc_y;
  float hz = az - dc_z;
  *hz_out = hz;

  // Characteristic function = instantaneous energy of high-passed accel
  float cf = hx * hx + hy * hy + hz * hz;
  live_pga = sqrtf(cf);

  sta += (cf - sta) / (float)N_STA;
  // Soft-freeze LTA while triggered (1/10 rate) so a long desk shake can't lock forever
  float lta_step = triggered ? ((float)N_LTA * 10.0f) : (float)N_LTA;
  lta += (cf - lta) / lta_step;
  if (lta < LTA_MIN) {
    lta = LTA_MIN;
  }

  ratio = sta / lta;
  sample_n++;
  warmup_done = (sample_n >= (uint32_t)N_LTA);

  bool fired = false;
  if (warmup_done && armed && ratio >= RATIO_TRIGGER) {
    fired = true;
    triggered = true;
    armed = false;
  }
  if (triggered && ratio <= RATIO_DETRIGGER) {
    triggered = false;
    armed = true;
  }
  return fired;
}

// End a stuck trigger: catch LTA up to STA so ratio collapses and we can re-arm
static void forceEndTrigger() {
  if (!triggered) {
    return;
  }
  triggered = false;
  armed = true;
  if (sta > lta) {
    lta = sta;
  }
  ratio = (lta > LTA_MIN) ? (sta / lta) : 0.0f;
}

static uint16_t colorForMmi(float imm) {
  int band = (int)floorf(imm);
  if (band <= 0) {
    return 0x2104;
  }
  if (band <= 3) {
    return ST77XX_GREEN;   // I–III
  }
  if (band <= 5) {
    return ST77XX_YELLOW;  // IV–V
  }
  if (band <= 7) {
    return ST77XX_ORANGE;  // VI–VII
  }
  return ST77XX_RED;       // VIII–XII
}

static void drawStaticChrome() {
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);
  tft.setCursor(12, 8);
  tft.print("SEISMO");
  tft.setTextSize(1);
  tft.setCursor(110, 14);
  tft.print("STA/LTA + MMI");

  const int bar_y = 36;
  const int cell_w = TFT_W / MMI_LEGEND_MAX;
  for (int i = 1; i <= MMI_LEGEND_MAX; i++) {
    tft.fillRect((i - 1) * cell_w + 1, bar_y, cell_w - 2, 8, colorForMmi((float)i));
  }
  tft.drawFastHLine(0, WAVE_Y0 - 2, TFT_W, 0x8410);
  tft.setTextColor(0x8410);
  tft.setCursor(4, WAVE_Y0 - 12);
  tft.print("seismogram  Z (HP)");
}

static void drawLevelCells(float imm) {
  const int bar_y = 48;
  const int cell_w = TFT_W / MMI_LEGEND_MAX;
  int lit = (int)floorf(imm + 0.001f);  // 8.0 → 8 cells, matches red band
  if (lit < 0) {
    lit = 0;
  }
  if (lit > MMI_LEGEND_MAX) {
    lit = MMI_LEGEND_MAX;
  }
  // Lit cells use *current* severity color (same as the big number), not each
  // cell's legend hue — otherwise VIII+ looked "stuck" at orange mid-bar.
  uint16_t lit_c = colorForMmi(imm);
  tft.fillRect(0, bar_y, TFT_W, 10, ST77XX_BLACK);
  for (int i = 1; i <= MMI_LEGEND_MAX; i++) {
    uint16_t c = (i <= lit) ? lit_c : 0x2104;
    tft.fillRect((i - 1) * cell_w + 1, bar_y, cell_w - 2, 8, c);
  }
}

static void drawMagnitudePanel(float m_show, float pga, float rat, bool ev, bool warm) {
  bool changed = (warm != drawn_warm) || (fabsf(m_show - drawn_m) > 0.05f) ||
                 (ev != drawn_event) || (fabsf(pga - drawn_pga) > 0.008f) ||
                 (fabsf(rat - drawn_ratio) > 0.15f);
  if (!changed) {
    return;
  }
  drawn_m = m_show;
  drawn_event = ev;
  drawn_warm = warm;
  drawn_pga = pga;
  drawn_ratio = rat;

  tft.fillRect(0, 60, TFT_W, WAVE_Y0 - 62, ST77XX_BLACK);

  if (!warm) {
    tft.setTextColor(ST77XX_YELLOW);
    tft.setTextSize(2);
    tft.setCursor(20, 90);
    tft.print("WARMUP");
    tft.setTextSize(1);
    tft.setCursor(20, 120);
    uint32_t left = (N_LTA > sample_n) ? (N_LTA - sample_n) : 0;
    tft.printf("filling LTA ~%lu s", (unsigned long)(left / (uint32_t)SAMPLE_HZ));
    return;
  }

  if (ev) {
    tft.fillRect(0, 60, TFT_W, 26, ST77XX_RED);
    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(2);
    tft.setCursor(50, 64);
    tft.print("EVENT");
  }

  drawLevelCells(m_show);

  tft.setTextColor(colorForMmi(m_show));
  tft.setTextSize(6);
  char buf[8];
  snprintf(buf, sizeof(buf), "%.1f", m_show);
  int16_t x1, y1;
  uint16_t bw, bh;
  tft.getTextBounds(buf, 0, 0, &x1, &y1, &bw, &bh);
  tft.setCursor((TFT_W - (int)bw) / 2, ev ? 100 : 88);
  tft.print(buf);

  tft.setTextColor(ST77XX_CYAN);
  tft.setTextSize(1);
  tft.setCursor(12, 160);
  tft.print("MMI (Wald 1999)");
  tft.setCursor(12, 172);
  tft.printf("PGA %.3fg  STA/LTA %.1f", pga, rat);
}

static int sampleToY(float v) {
  int mid = WAVE_Y0 + WAVE_H / 2;
  float scale = (WAVE_H / 2 - 2) / WAVE_FULL_SCALE_G;
  int y = mid - (int)(v * scale);
  if (y < WAVE_Y0) {
    y = WAVE_Y0;
  }
  if (y > WAVE_Y0 + WAVE_H - 1) {
    y = WAVE_Y0 + WAVE_H - 1;
  }
  return y;
}

static void drawWave(bool ev) {
  tft.fillRect(0, WAVE_Y0, TFT_W, WAVE_H, ST77XX_BLACK);
  int mid = WAVE_Y0 + WAVE_H / 2;
  tft.drawFastHLine(0, mid, TFT_W, 0x4208);

  int plot_w = WAVE_N < TFT_W ? WAVE_N : TFT_W;
  for (int x = 1; x < plot_w; x++) {
    int i0 = (wave_i + WAVE_N - plot_w + x - 1) % WAVE_N;
    int i1 = (wave_i + WAVE_N - plot_w + x) % WAVE_N;
    uint16_t c = ev ? ST77XX_RED : ST77XX_GREEN;
    tft.drawLine(x - 1, sampleToY(wave[i0]), x, sampleToY(wave[i1]), c);
  }
}

void setup() {
  Serial.begin(115200);
  delay(400);
  Serial.println();
  Serial.println("seismo — STA/LTA + MMI (Wald 1999)");
  Serial.printf("HP_ALPHA=%.3f  STA=%d  LTA=%d  trig=%.1f/det=%.1f\n",
                HP_ALPHA, N_STA, N_LTA, RATIO_TRIGGER, RATIO_DETRIGGER);
  Serial.printf("MMI = %.2f*log10(PGA_cm/s2)-%.2f  XII@>=%.2fg  FS=±8g  quiet<%.3fg\n",
                MMI_A, MMI_B, PGA_AT_MMI12_G, PGA_QUIET_G);

  Wire.begin(PIN_SDA, PIN_SCL_I2C);
  Wire.setClock(400000);
  uint8_t who = 0;
  if (!readRegs(REG_WHO_AM_I, &who, 1) || who != WHO_AM_I_LSM6DSO) {
    Serial.printf("IMU WHO_AM_I=0x%02X — halt\n", who);
    while (true) {
      delay(1000);
    }
  }
  writeReg(REG_CTRL3_C, 0x44);
  writeReg(REG_CTRL1_XL, CTRL1_XL_104HZ_8G);
  delay(40);

  float ax, ay, az;
  for (int i = 0; i < 20; i++) {
    if (readAccelG(&ax, &ay, &az)) {
      dc_x = ax;
      dc_y = ay;
      dc_z = az;
    }
    delay(5);
  }

  SPI.begin(TFT_SCK, -1, TFT_MOSI, TFT_CS);
  tft.init(TFT_W, TFT_H);
  tft.setRotation(0);
  for (int i = 0; i < WAVE_N; i++) {
    wave[i] = 0;
  }
  drawStaticChrome();
  drawMagnitudePanel(0, 0, 0, false, false);
  drawWave(false);
  Serial.printf("warmup ~%.0f s (LTA fill) — keep still, then thump\n",
                (float)N_LTA / SAMPLE_HZ);
}

void loop() {
  float ax, ay, az;
  uint32_t now = millis();

  // Only advance STA/LTA on a fresh ODR sample (~104 Hz), not every loop spin
  uint8_t status = 0;
  if (!readRegs(REG_STATUS, &status, 1) || !(status & STATUS_XLDA)) {
    // still refresh UI/serial on the same cadence
  } else if (readAccelG(&ax, &ay, &az)) {
    float hz = 0;
    bool fired = processSample(ax, ay, az, &hz);

    wave[wave_i] = hz;
    wave_i = (wave_i + 1) % WAVE_N;

    pushPeak(live_pga, now);
    pga_g = windowPga(now);
    mmi = pgaToMmi(pga_g);

    if (fired) {
      trigger_since = now;
      event_until = now + EVENT_HOLD_MS;
      Serial.printf("*** EVENT ***  ratio=%.1f  PGA=%.3fg  MMI=%.1f\n",
                    ratio, pga_g, mmi);
    }

    // Keep banner alive while shaking; force re-arm if locked too long
    if (triggered) {
      event_until = now + EVENT_HOLD_MS;
      if (trigger_since == 0) {
        trigger_since = now;
      }
      if (now - trigger_since >= TRIGGER_MAX_MS) {
        forceEndTrigger();
        Serial.println("re-arm (trigger max)");
      }
    } else {
      trigger_since = 0;
    }
  }

  // Hold check every loop so UI clears even between ODR samples
  event_on = (now < event_until);
  float m_show = mmi;

  if (now - last_ui >= UI_PERIOD_MS) {
    last_ui = now;
    drawMagnitudePanel(m_show, pga_g, ratio, event_on, warmup_done);
    drawWave(event_on);
  }

  if (now - last_serial >= SERIAL_PERIOD_MS) {
    last_serial = now;
    if (!warmup_done) {
      Serial.printf("[warmup] %lu/%d  ratio=%.2f  noise=%.5f\n",
                    (unsigned long)sample_n, N_LTA, ratio, sqrtf(lta));
    } else {
      Serial.printf("%s MMI=%.1f pga=%.3f ratio=%.1f%s\n",
                    armed ? "[armed]" : "[trig]",
                    m_show, pga_g, ratio, event_on ? " EVENT" : "");
    }
  }
}
