# Skema data

Satu tabel sudah cukup untuk lomba. Kolom yang sama dipakai CSV dan basis data (Supabase/PostgreSQL).

## `pengukuran`

| Kolom | Tipe | Keterangan |
|---|---|---|
| waktu | timestamp | waktu pengukuran |
| id_perangkat | teks | contoh `rig-01`, `sumur-masjid-01` |
| tegangan | angka | Vrms (V) |
| arus | angka | Irms (A) |
| daya_aktif | angka | W |
| faktor_daya | angka | 0 sampai 1 |
| debit_ref | angka | L/menit dari flowmeter pembanding (hanya saat kalibrasi/validasi) |
| kedalaman_ref | angka | m, dari sensor tekanan atau pengukuran manual (hanya saat kalibrasi/validasi) |

Kolom hasil model (`debit_est`, `kedalaman_est`, `set`) ditambahkan oleh skrip analisis.

## Aturan

- `data/sample/` berisi **data simulasi**. Beri nama file yang jelas (`..._sim.csv`).
- Data hasil rig atau lapangan disimpan di `data/raw/` (tidak ikut di-commit secara default; lihat `.gitignore`).
  Catat tiap sesi di logbook: tanggal, pompa, kondisi, siapa yang mengukur.
- Jangan menimpa data mentah. Hasil olahan disimpan di file terpisah.
