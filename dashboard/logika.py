"""Fungsi hitung untuk dasbor (tanpa Streamlit, supaya mudah diuji)."""
import numpy as np
import pandas as pd


def muat(path_atau_buffer):
    df = pd.read_csv(path_atau_buffer, parse_dates=["waktu"])
    return df.sort_values("waktu").reset_index(drop=True)


def volume_m3(df, kolom_debit="debit_est"):
    """Volume air (m3) dari debit L/menit dengan integrasi trapesium terhadap waktu."""
    if len(df) < 2:
        return 0.0
    dt_menit = df["waktu"].diff().dt.total_seconds().fillna(0).to_numpy() / 60.0
    # Celah antar sesi (>5 menit) dianggap pompa mati.
    dt_menit = np.where(dt_menit > 5, 0, dt_menit)
    liter = (df[kolom_debit].to_numpy() * dt_menit).sum()
    return float(liter / 1000.0)


def energi_kwh(df):
    if len(df) < 2:
        return 0.0
    dt_jam = df["waktu"].diff().dt.total_seconds().fillna(0).to_numpy() / 3600.0
    dt_jam = np.where(dt_jam > 5 / 60, 0, dt_jam)
    return float((df["daya_aktif"].to_numpy() * dt_jam).sum() / 1000.0)


def kwh_per_m3(df):
    v = volume_m3(df)
    return energi_kwh(df) / v if v > 0 else float("nan")


def galat_persen(df, est, ref):
    """Galat relatif rata-rata (%), hanya pada data uji bila ada kolom 'set'."""
    d = df[df["set"] == "uji"] if "set" in df.columns else df
    d = d[d[ref] != 0]
    if d.empty:
        return float("nan")
    return float(((d[est] - d[ref]).abs() / d[ref].abs() * 100).mean())


def tren_harian(df, kolom="kedalaman_est"):
    return df.set_index("waktu")[kolom].resample("1h").mean().dropna()
