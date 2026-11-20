/*
 * ESP32 Voltage Monitor
 * ---------------------
 * Measures the ESP32 supply voltage (3V3 rail, or battery / VIN through a
 * resistor divider) with the on-chip ADC and streams the result over Serial
 * as CSV:  time_ms,raw_adc,adc_mv,voltage_v
 *
 * Note: the classic ESP32 has no ADC channel wired internally to VDD
 * (unlike the ESP8266's ESP.getVcc()). The standard way to measure the
 * chip's own supply is to feed it into an ADC1 pin through a divider:
 *
 *      3V3 / VBAT ── R1 ──┬── R2 ── GND
 *                         │
 *                     GPIO34 (ADC1_CH6)
 *
 * With R1 = R2 = 100k the pin sees half the voltage, so DIVIDER_RATIO = 2.0.
 * If you connect a voltage below ~3.1 V directly (no divider), set it to 1.0.
 *
 * analogReadMilliVolts() uses the factory eFuse calibration, so it is far
 * more accurate than converting analogRead() by hand.
 *
 * Board: any ESP32 in Arduino IDE (esp32 core 2.x or 3.x).
 */

#include <Arduino.h>

// ---------------- Configuration ----------------
const int      ADC_PIN         = 34;     // ADC1 pin (ADC2 doesn't work with Wi-Fi on)
const float    DIVIDER_RATIO   = 2.0f;   // (R1 + R2) / R2
const float    CAL_FACTOR      = 1.000f; // fine-tune against a multimeter
const int      SAMPLES         = 64;     // readings averaged per output line
const uint32_t SAMPLE_PERIOD_MS = 500;   // time between output lines
const long     BAUD_RATE       = 115200;
// ------------------------------------------------

uint32_t lastSample = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  delay(500);

  analogReadResolution(12);                  // 0..4095
  analogSetPinAttenuation(ADC_PIN, ADC_11db); // full range ~0..3.1 V
  pinMode(ADC_PIN, INPUT);

  Serial.println("# ESP32 voltage monitor started");
  Serial.println("time_ms,raw_adc,adc_mv,voltage_v");
}

void loop() {
  uint32_t now = millis();
  if (now - lastSample < SAMPLE_PERIOD_MS) return;
  lastSample = now;

  uint32_t rawSum = 0;
  uint32_t mvSum  = 0;
  for (int i = 0; i < SAMPLES; i++) {
    rawSum += analogRead(ADC_PIN);
    mvSum  += analogReadMilliVolts(ADC_PIN);
    delayMicroseconds(100);
  }

  float rawAvg  = (float)rawSum / SAMPLES;
  float adcMv   = (float)mvSum / SAMPLES;
  float voltage = adcMv / 1000.0f * DIVIDER_RATIO * CAL_FACTOR;

  Serial.print(now);
  Serial.print(',');
  Serial.print(rawAvg, 1);
  Serial.print(',');
  Serial.print(adcMv, 1);
  Serial.print(',');
  Serial.println(voltage, 4);
}
