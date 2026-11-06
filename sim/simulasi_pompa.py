"""METER-AIR-TANAH: simulasi prinsip + pembuat data contoh.

Menjalankan:  python sim/simulasi_pompa.py
Keluaran   :  docs/simulasi_pompa.png  dan  data/sample/pengukuran_sim.csv

PENTING: semua angka di sini ILUSTRATIF (pompa rekaan), bukan hasil ukur.
Gunakan skrip ini untuk menguji alur data dan dasbor sebelum rig jadi.
Ganti parameter dengan data pompa sebenarnya (kurva H-Q dari datasheet).
"""
from pathlib import Path
import numpy as np
import pandas as pd

RHO, G = 1000.0, 9.81
H0, QMAX = 40.0, 45.0            # tinggi angkat shut-off [m], debit maks [L/menit]
K = H0 / QMAX**2                 # kurva pompa  H = H0 - K Q^2
C = 0.004                        # rugi gesek pipa [m/(L/menit)^2]
QBEP, ETA_P_MAX, ETA_M = 25.0, 0.45, 0.70
ROOT = Path(__file__).resolve().parents[1]


def eta_pompa(q):
    x = q / QBEP
    return np.clip(ETA_P_MAX * (2 * x - x**2), 0.05, None)


def titik_kerja(kedalaman):
    """Debit [L/menit], tinggi angkat [m], daya listrik [W] pada kedalaman muka air."""
    q = np.sqrt((H0 - kedalaman) / (K + C))
    h = H0 - K * q**2
    p_hid = RHO * G * (q / 60000.0) * h
    p_el = p_hid / (eta_pompa(q) * ETA_M)
    return q, h, p_el


def buat_data(hari=2, seed=7):
    """Data per 10 detik selama pompa menyala, 3 sesi per hari."""
    rng = np.random.default_rng(seed)
    baris = []
    t0 = pd.Timestamp("2026-11-01 06:00:00")
    for d in range(hari):
        for jam in (6, 12, 18):
            mulai = t0 + pd.Timedelta(days=d, hours=jam - 6)
            for k in range(180):                       # 30 menit per sesi
                t = mulai + pd.Timedelta(seconds=10 * k)
                frac = (d * 24 + jam + k / 360) / (hari * 24)
                kedalaman = 12 + 4 * frac + 0.4 * np.sin(2 * np.pi * (jam / 24)) + rng.normal(0, 0.1)
                q, _, p = titik_kerja(kedalaman)
                v = 220 + rng.normal(0, 2.5)
                pf = 0.80 + 0.12 * q / QMAX + rng.normal(0, 0.005)
                p_ukur = p * (1 + rng.normal(0, 0.01))
                baris.append(dict(
                    waktu=t, id_perangkat="rig-01", tegangan=round(v, 1),
                    arus=round(p_ukur / (v * pf), 3), daya_aktif=round(p_ukur, 1),
                    faktor_daya=round(pf, 3), debit_ref=round(q * (1 + rng.normal(0, 0.02)), 2),
                    kedalaman_ref=round(kedalaman, 2)))
    return pd.DataFrame(baris)


def fitur(df):
    p, pf = df["daya_aktif"].to_numpy(), df["faktor_daya"].to_numpy()
    return np.column_stack([np.ones_like(p), p, pf, p * pf, p**2, pf**2])


def kalibrasi_dan_estimasi(df):
    """Contoh alur kalibrasi: latih di separuh awal, uji di separuh akhir.
    Ini hanya MENUNJUKKAN ALUR; angka galat pada data simulasi bukan klaim kinerja."""
    n = len(df) // 2
    X = fitur(df)
    out = df.copy()
    for ref, est in (("debit_ref", "debit_est"), ("kedalaman_ref", "kedalaman_est")):
        w, *_ = np.linalg.lstsq(X[:n], df[ref].to_numpy()[:n], rcond=None)
        out[est] = np.round(X @ w, 2)
    out["set"] = np.where(np.arange(len(df)) < n, "kalibrasi", "uji")
    return out


def gambar(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = np.linspace(5, 34, 60)
    q, h, p = np.array([titik_kerja(x) for x in d]).T
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6), dpi=150)
    qq = np.linspace(0, QMAX, 100)
    ax[0].plot(qq, H0 - K * qq**2, "k", lw=2)
    for dd in (5, 15, 25, 34):
        ax[0].plot(qq, dd + C * qq**2, lw=1.5)
        qk, hk, _ = titik_kerja(dd)
        ax[0].plot(qk, hk, "o")
    ax[0].set(xlabel="Debit (L/menit)", ylabel="Tinggi angkat (m)", title="a. Titik kerja pompa")
    ax[1].plot(d, q); ax[1].set(xlabel="Kedalaman muka air (m)", ylabel="Debit (L/menit)", title="b. Debit")
    ax[2].plot(d, p); ax[2].set(xlabel="Kedalaman muka air (m)", ylabel="Daya listrik (W)", title="c. Daya (tidak searah)")
    for a in ax:
        a.grid(alpha=0.3)
    fig.suptitle("Simulasi ilustratif, bukan hasil pengukuran")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)


if __name__ == "__main__":
    df = kalibrasi_dan_estimasi(buat_data())
    out_csv = ROOT / "data" / "sample" / "pengukuran_sim.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    gambar(ROOT / "docs" / "simulasi_pompa.png")
    uji = df[df["set"] == "uji"]
    gal = (uji["debit_est"] - uji["debit_ref"]).abs() / uji["debit_ref"] * 100
    print(f"{len(df)} baris -> {out_csv}")
    print(f"Galat debit rata-rata pada data simulasi (set uji): {gal.mean():.1f}% (BUKAN klaim kinerja)")
