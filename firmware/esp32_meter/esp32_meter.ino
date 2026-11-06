/*
 * METER-AIR-TANAH - kerangka firmware ESP32 (BELUM DIUJI di perangkat keras)
 *
 * Membaca arus (CT SCT-013 + resistor beban + bias 1,65 V) dan tegangan (ZMPT101B),
 * menghitung Vrms, Irms, daya aktif, faktor daya, lalu mengirim JSON ke basis data
 * lewat HTTPS setiap KIRIM_MS.
 *
 * SEBELUM DIPAKAI:
 *  1. Isi WIFI_SSID, WIFI_PASS, API_URL, API_KEY (jangan di-commit; lihat config.example.h).
 *  2. Kalibrasi KAL_V dan KAL_I terhadap multimeter / alat ukur acuan, bukan angka tebakan.
 *  3. Pasang sensor oleh orang yang paham listrik 220 V; MCB mati saat memasang; pakai RCBO.
 *  4. Lihat docs/ untuk skema wiring (isi sendiri setelah rig dirakit).
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <math.h>
#include "config.h"          // salin dari config.example.h dan isi (config.h ada di .gitignore)

const int PIN_I = 34;        // ADC1, sensor arus
const int PIN_V = 35;        // ADC1, sensor tegangan
const int N_SAMPEL = 2000;   // sampel per jendela (~ beberapa siklus 50 Hz)
const unsigned long KIRIM_MS = 10000;

// TODO kalibrasi: nilai di bawah hanya penanda tempat.
float KAL_V = 1.0f;          // volt per unit ADC (setelah dikurangi offset)
float KAL_I = 1.0f;          // ampere per unit ADC

unsigned long terakhirKirim = 0;

struct Ukur { float vrms, irms, p, pf; };

Ukur baca() {
  double sumV = 0, sumI = 0, sumV2 = 0, sumI2 = 0, sumP = 0;
  static float offV = 2048, offI = 2048;           // offset DC, diperbarui perlahan
  for (int k = 0; k < N_SAMPEL; k++) {
    int rv = analogRead(PIN_V), ri = analogRead(PIN_I);
    offV += (rv - offV) * 0.001f; offI += (ri - offI) * 0.001f;
    float v = (rv - offV) * KAL_V, i = (ri - offI) * KAL_I;
    sumV2 += v * v; sumI2 += i * i; sumP += v * i;
    delayMicroseconds(100);                        // ~ 10 kHz, sesuaikan dengan waktu analogRead
  }
  Ukur u;
  u.vrms = sqrt(sumV2 / N_SAMPEL);
  u.irms = sqrt(sumI2 / N_SAMPEL);
  u.p = sumP / N_SAMPEL;
  float s = u.vrms * u.irms;
  u.pf = s > 0.01f ? fabs(u.p) / s : 0;
  return u;
}

void kirim(const Ukur &u) {
  if (WiFi.status() != WL_CONNECTED) return;
  WiFiClientSecure client;
  client.setInsecure();    // TODO: ganti dengan sertifikat root server sebelum dipakai sungguhan
  HTTPClient http;
  http.begin(client, API_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("apikey", API_KEY);
  http.addHeader("Authorization", String("Bearer ") + API_KEY);
  char body[256];
  snprintf(body, sizeof(body),
           "{\"id_perangkat\":\"%s\",\"tegangan\":%.1f,\"arus\":%.3f,\"daya_aktif\":%.1f,\"faktor_daya\":%.3f}",
           ID_PERANGKAT, u.vrms, u.irms, u.p, u.pf);
  int kode = http.POST((uint8_t *)body, strlen(body));
  Serial.printf("POST %d  %s\n", kode, body);
  http.end();
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi tersambung");
}

void loop() {
  Ukur u = baca();
  if (millis() - terakhirKirim >= KIRIM_MS) {
    terakhirKirim = millis();
    kirim(u);
  }
}
