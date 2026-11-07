"""Fungsi hitung untuk dasbor (tanpa Streamlit, supaya mudah diuji)."""
import numpy as np
import pandas as pd

KOLOM_WAJIB = ("waktu", "daya_aktif", "debit_est")
CELAH_MENIT = 5  # celah antar baris lebih dari ini dianggap pompa mati (sesi baru)


def muat(path_atau_buffer):
    df = pd.read_csv(path_atau_buffer, parse_dates=["waktu"])
    return df.sort_values("waktu").reset_index(drop=True)


def kolom_hilang(df):
    return [k for k in KOLOM_WAJIB if k not in df.columns]


def _dt_menit(df):
    dt = df["waktu"].diff().dt.total_seconds().fillna(0).to_numpy() / 60.0
    # Celah antar sesi (>5 menit) dianggap pompa mati.
    return np.where(dt > CELAH_MENIT, 0, dt)


def volume_m3(df, kolom_debit="debit_est"):
    """Volume air (m3) dari debit L/menit, dijumlahkan terhadap waktu."""
    if len(df) < 2 or kolom_debit not in df.columns:
        return 0.0
    liter = (df[kolom_debit].to_numpy() * _dt_menit(df)).sum()
    return float(liter / 1000.0)


def energi_kwh(df):
    if len(df) < 2:
        return 0.0
    dt_jam = _dt_menit(df) / 60.0
    return float((df["daya_aktif"].to_numpy() * dt_jam).sum() / 1000.0)


def kwh_per_m3(df):
    v = volume_m3(df)
    return energi_kwh(df) / v if v > 0 else float("nan")


def jam_operasi(df):
    return float(_dt_menit(df).sum() / 60.0)


def galat_persen(df, est, ref):
    """Galat relatif rata-rata (%), hanya pada data uji bila ada kolom 'set'."""
    if est not in df.columns or ref not in df.columns:
        return float("nan")
    d = df[df["set"] == "uji"] if "set" in df.columns else df
    d = d[d[ref] != 0]
    if d.empty:
        return float("nan")
    return float(((d[est] - d[ref]).abs() / d[ref].abs() * 100).mean())


def tren_harian(df, kolom="kedalaman_est"):
    return df.set_index("waktu")[kolom].resample("1h").mean().dropna()


def nomor_sesi(df):
    """Nomor sesi pompa (1, 2, ...): sesi baru bila celah antar baris > CELAH_MENIT."""
    celah = df["waktu"].diff().dt.total_seconds().fillna(0) > CELAH_MENIT * 60
    return celah.cumsum().astype(int) + 1


def ringkasan_sesi(df):
    """Satu baris per sesi pompa: waktu, durasi, volume, energi, kWh/m3, faktor daya, kedalaman."""
    d = df.assign(sesi=nomor_sesi(df))
    baris = []
    for s, g in d.groupby("sesi"):
        v = volume_m3(g)
        e = energi_kwh(g)
        r = dict(sesi=s, mulai=g["waktu"].iloc[0], selesai=g["waktu"].iloc[-1],
                 durasi_menit=(g["waktu"].iloc[-1] - g["waktu"].iloc[0]).total_seconds() / 60,
                 volume_m3=v, energi_kwh=e, kwh_m3=e / v if v > 0 else np.nan,
                 daya_w=g["daya_aktif"].mean())
        if "debit_ref" in g.columns:
            r["volume_ref_m3"] = volume_m3(g, "debit_ref")
        for k in ("faktor_daya", "kedalaman_est", "kedalaman_ref"):
            if k in g.columns:
                r[k] = g[k].mean()
        if "set" in g.columns:
            r["set"] = g["set"].mode().iloc[0]
        baris.append(r)
    return pd.DataFrame(baris)


def kesehatan_pompa(sesi, batas_naik_persen=10.0):
    """Bandingkan kWh/m3 tiap sesi dengan rata-rata sesi pertama (acuan).
    Naik > batas -> 'Periksa'; > setengah batas -> 'Pantau'; selain itu 'Normal'."""
    if sesi.empty or sesi["kwh_m3"].isna().all():
        return sesi.assign(perubahan_persen=np.nan, status="–")
    acuan = sesi["kwh_m3"].iloc[0]
    ubah = (sesi["kwh_m3"] / acuan - 1) * 100
    status = np.where(ubah > batas_naik_persen, "Periksa",
                      np.where(ubah > batas_naik_persen / 2, "Pantau", "Normal"))
    return sesi.assign(perubahan_persen=ubah, status=status)
