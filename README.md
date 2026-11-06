# METER-AIR-TANAH

Memperkirakan **volume air tanah yang diambil**, **tren muka air sumur**, dan **kesehatan pompa** dari sinyal listrik pompa, tanpa memasang apa pun ke dalam sumur atau memotong pipa.

Proyek untuk UNS Innovation Hackathon 2026, Sub-tema C (manajemen energi dan lingkungan perkotaan).

> **Status: tahap konsep, TKT 3.** Yang ada saat ini adalah simulasi, kerangka firmware yang belum diuji di perangkat keras, dan dasbor yang membaca data simulasi. Belum ada hasil pengukuran. Jangan mengutip angka dari repositori ini sebagai kinerja alat.

## Cara kerja singkat

Daya listrik pompa bergantung pada debit dan tinggi angkat. Dengan mengukur tegangan dan arus pompa, lalu memakai kurva pompa dan kalibrasi per pompa, kita memperkirakan debit (lalu volume) dan tren muka air.

Batas penting: daya yang sama bisa muncul pada dua kedalaman berbeda (lihat `docs/simulasi_pompa.png`, panel c). Karena itu model memakai fitur tambahan (faktor daya, bentuk arus) dan kalibrasi terhadap flowmeter dan sensor tekanan. Volume air dan kWh per m³ lebih dapat diandalkan daripada angka kedalaman; kedalaman dipakai sebagai **tren**.

Alat ini bukan pengganti meter air resmi. Fungsinya menguji silang dan memantau pompa yang belum bermeter.

## Isi repositori

| Folder | Isi |
|---|---|
| `docs/` | proposal (Word dan PDF), diagram blok, grafik simulasi |
| `sim/` | simulasi pompa dan pembuat data contoh |
| `firmware/esp32_meter/` | kerangka firmware ESP32 (belum diuji) |
| `dashboard/` | dasbor Streamlit dan fungsi hitung |
| `data/` | skema data dan data contoh simulasi |

## Mulai cepat

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r dashboard/requirements.txt
python sim/simulasi_pompa.py         # membuat data contoh dan grafik
streamlit run dashboard/app.py       # membuka dasbor
```

## Yang harus dikerjakan berikutnya

- [ ] Rakit rig sumur mini (pompa, tandon, katup, flowmeter, sensor tekanan)
- [ ] Kalibrasi sensor arus dan tegangan terhadap alat ukur acuan
- [ ] Rekam data pada banyak kombinasi debit dan tinggi angkat
- [ ] Latih dan uji model; laporkan galat dalam persen pada data uji terpisah
- [ ] Uji di 1 sampai 3 sumur nyata (dengan izin tertulis pemilik)
- [ ] Hubungkan firmware ke basis data; ganti sumber data dasbor
- [ ] Mode demo (putar ulang data rekaman) untuk presentasi

## Keselamatan

Pekerjaan pada panel pompa melibatkan listrik 220 V. Matikan MCB sebelum memasang sensor, gunakan RCBO, dan lakukan uji pertama di laboratorium dengan pendampingan dosen.

## Catatan orisinalitas

Prinsip estimasi debit dan muka air dari sinyal listrik pompa sudah ada di literatur dan paten (misalnya US 12,066,313 B1). Pembeda proyek ini ada pada penerapan untuk pompa fasilitas kota, kalibrasi dengan galat terukur, dan keluaran gabungan energi per volume, tren muka air, serta kesehatan pompa. Lihat daftar pustaka di proposal.

## Lisensi

Belum ditentukan. Saat ini semua hak dipegang tim karena tidak ada lisensi. Lisensi akan ditentukan setelah masa seleksi dan penjurian selesai.
