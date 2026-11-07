"""Dasbor METER-AIR-TANAH (Streamlit).

Jalankan:  streamlit run dashboard/app.py
Sumber data: CSV (contoh simulasi di data/sample, atau unggah CSV hasil rig).
Nanti diganti membaca dari basis data (Supabase) tanpa mengubah fungsi hitung.
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from logika import (
    KOLOM_WAJIB, energi_kwh, galat_persen, jam_operasi, kesehatan_pompa, kolom_hilang, kwh_per_m3, muat,
    nomor_sesi, ringkasan_sesi, volume_m3,
)
from simulator import Pompa, kedalaman_kembar, kurva, kurva_hq, kwh_per_m3_sesaat
from tampilan import (
    AIR, BIRU, CSS, HIJAU, KUNING, MERAH, NAVY, TOSKA, banner, brand_sidebar, footer, ikon, kartu, svg_gauge,
    svg_sumur,
)

ROOT = Path(__file__).resolve().parents[1]
CONTOH = ROOT / "data" / "sample" / "pengukuran_sim.csv"
TARIF_BAWAAN = 1444.70  # Rp/kWh, contoh tarif rumah tangga; ubah di panel kiri
HARI = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

LABEL_EST = "Perkiraan (dari listrik)"
LABEL_REF = "Acuan (alat ukur)"
WARNA_EST, WARNA_REF = BIRU, KUNING

alt.data_transformers.disable_max_rows()

st.set_page_config(page_title="Dasbor METER-AIR-TANAH", page_icon="💧", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Format angka (gaya Indonesia: titik ribuan, koma desimal)
# ---------------------------------------------------------------------------
def fmt(x, des=1):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    s = f"{x:,.{des}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def tanda(x, des=2):
    return ("+" if x > 0 else "") + fmt(x, des)


def waktu_label(t):
    t = pd.Timestamp(t)
    return f"{HARI[t.weekday()]}, {t:%d-%m %H:%M:%S}"


@st.cache_data(show_spinner=False)
def muat_cache(sumber):
    return muat(sumber)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(brand_sidebar(), unsafe_allow_html=True)
    st.markdown("### Sumber data")
    unggah = st.file_uploader("Unggah CSV pengukuran", type="csv",
                              help="Kosongkan untuk memakai data contoh simulasi.")
    with st.expander("Format CSV yang diterima"):
        st.markdown(
            "Kolom wajib: " + ", ".join(f"`{k}`" for k in KOLOM_WAJIB) + ".\n\n"
            "Kolom opsional: `tegangan`, `arus`, `faktor_daya`, `debit_ref`, `kedalaman_ref`, "
            "`kedalaman_est`, `set` (`kalibrasi`/`uji`), `id_perangkat`.\n\n"
            "Celah lebih dari 5 menit antar baris dianggap pompa mati (sesi baru). Rincian: `data/README.md`.")

try:
    df = muat_cache(unggah if unggah is not None else CONTOH)
except Exception as e:  # noqa: BLE001 - tampilkan galat apa pun ke pengguna
    st.error(f"Berkas tidak dapat dibaca sebagai CSV pengukuran: {e}")
    st.stop()
hilang = kolom_hilang(df)
if hilang:
    st.error("Kolom wajib tidak ditemukan: " + ", ".join(f"`{k}`" for k in hilang)
             + ". Lihat panduan format di panel kiri.")
    st.stop()
if len(df) < 2:
    st.error("Berkas berisi kurang dari 2 baris data.")
    st.stop()

df["sesi"] = nomor_sesi(df)
simulasi = unggah is None
ada_ref_q = "debit_ref" in df.columns
ada_kd = "kedalaman_est" in df.columns
ada_ref_kd = "kedalaman_ref" in df.columns
perangkat = ", ".join(map(str, df["id_perangkat"].unique())) if "id_perangkat" in df.columns else "–"
t0, t1 = df["waktu"].iloc[0], df["waktu"].iloc[-1]

with st.sidebar:
    st.markdown("### Biaya & tandon")
    tarif = st.number_input("Tarif listrik (Rp/kWh)", value=TARIF_BAWAAN, min_value=0.0, step=50.0,
                            help="Dipakai untuk menghitung biaya listrik per m³ air.")
    kapasitas_l = st.number_input("Kapasitas tandon (L)", value=1100, min_value=100, step=100,
                                  help="Hanya untuk animasi tandon pada putar ulang.")
    st.markdown("### Kesehatan pompa")
    batas_sehat = st.slider("Batas kenaikan kWh/m³ (%)", 2, 30, 10,
                            help="Bila energi per m³ naik melebihi batas ini dibanding sesi pertama, "
                                 "pompa ditandai perlu diperiksa.")
    st.markdown("### Informasi data")
    jarak = df["waktu"].diff().median()
    st.markdown(
        f"""
| | |
|---|---|
| Perangkat | {perangkat} |
| Rentang | {t0:%d-%m} – {t1:%d-%m-%Y} |
| Sesi pompa | {df['sesi'].max()} |
| Jumlah baris | {fmt(len(df), 0)} |
| Interval | {fmt(jarak.total_seconds(), 0)} detik |
""")

# ---------------------------------------------------------------------------
# Hitungan utama
# ---------------------------------------------------------------------------
vol = volume_m3(df)
vol_ref = volume_m3(df, "debit_ref") if ada_ref_q else None
energi = energi_kwh(df)
spesifik = kwh_per_m3(df)
jam = jam_operasi(df)
gal_q = galat_persen(df, "debit_est", "debit_ref")
gal_kd = galat_persen(df, "kedalaman_est", "kedalaman_ref")
sesi = kesehatan_pompa(ringkasan_sesi(df), batas_sehat)
n_sesi = len(sesi)

# ---------------------------------------------------------------------------
# Kepala halaman dan indikator utama
# ---------------------------------------------------------------------------
st.markdown(banner(simulasi, CONTOH.name if simulasi else unggah.name, perangkat,
                   f"{t0:%d-%m-%Y %H:%M} – {t1:%d-%m-%Y %H:%M}"), unsafe_allow_html=True)
if simulasi:
    st.warning("**Data simulasi.** Angka di halaman ini berasal dari pompa rekaan untuk menguji dasbor, bukan "
               "hasil pengukuran. Unggah CSV dari rig atau sumur nyata melalui panel kiri.", icon="⚠️")

kartu_list = []
if vol_ref:
    selisih = (vol / vol_ref - 1) * 100
    kartu_list.append(kartu("Volume air (perkiraan)", fmt(vol, 2), "m³",
                            f"acuan flowmeter {fmt(vol_ref, 2)} m³ ({tanda(selisih, 1)}%)",
                            "ok" if abs(selisih) < 5 else "warn", "drop"))
else:
    kartu_list.append(kartu("Volume air (perkiraan)", fmt(vol, 2), "m³", f"{n_sesi} sesi pompa", "", "drop"))
kartu_list.append(kartu("Energi pompa", fmt(energi, 2), "kWh",
                        f"{n_sesi} sesi · {fmt(jam, 1)} jam operasi", "", "bolt"))
kartu_list.append(kartu("Energi per volume", fmt(spesifik, 3), "kWh/m³",
                        f"≈ Rp {fmt(spesifik * tarif, 0)} per m³ air", "", "coins"))
if ada_kd and n_sesi >= 2:
    d_est = sesi["kedalaman_est"].iloc[-1] - sesi["kedalaman_est"].iloc[0]
    arah = "muka air turun" if d_est > 0.05 else ("muka air naik" if d_est < -0.05 else "relatif tetap")
    sub, kelas = arah, ""
    if ada_ref_kd:
        d_ref = sesi["kedalaman_ref"].iloc[-1] - sesi["kedalaman_ref"].iloc[0]
        sub = f"{arah} · acuan {tanda(d_ref)} m"
        kelas = "warn" if abs(d_est - d_ref) > 0.5 else "ok"
    kartu_list.append(kartu("Perubahan kedalaman", tanda(d_est), "m", sub, kelas, "ruler"))
if not np.isnan(gal_q):
    kartu_list.append(kartu("Galat debit (set uji)", fmt(gal_q, 1), "%",
                            f"galat kedalaman {fmt(gal_kd, 1)}%" if not np.isnan(gal_kd) else "terhadap flowmeter",
                            "ok" if gal_q < 5 else "warn", "target"))
akhir = sesi.iloc[-1]
kartu_list.append(kartu("Kesehatan pompa", akhir["status"], "",
                        f"kWh/m³ {tanda(akhir['perubahan_persen'], 1)}% dari sesi 1",
                        {"Normal": "ok", "Pantau": "warn", "Periksa": "bad"}.get(akhir["status"], ""), "heart"))
st.markdown(f'<div class="mat-kpis">{"".join(kartu_list)}</div>', unsafe_allow_html=True)

st.success(f"**Pompa menyala {n_sesi} sesi ({fmt(jam, 1)} jam)** dan diperkirakan mengambil **{fmt(vol, 2)} m³** air "
           f"dengan energi {fmt(energi, 2)} kWh (≈ Rp {fmt(energi * tarif, 0)}).", icon="💧")
if not np.isnan(gal_kd) and gal_kd > 10:
    st.warning(f"**Perkiraan kedalaman belum andal** (galat {fmt(gal_kd, 1)}% pada set uji). Daya yang sama bisa "
               "muncul pada dua kedalaman berbeda, jadi angka kedalaman dipakai sebagai **tren** saja. "
               "Lihat tab *Simulator apa-jika*.", icon="⚠️")


# ---------------------------------------------------------------------------
# Komponen grafik
# ---------------------------------------------------------------------------
def gaya(chart, tinggi=300):
    if tinggi is not None:
        chart = chart.properties(height=tinggi)
    return (chart.configure_view(stroke=None)
            .configure_axis(gridColor="#EDF0F4", labelFontSize=11, titleFontSize=12, titleColor="#4A5563",
                            titleFontWeight="normal", labelColor="#4A5563", domainColor="#C9D1DB",
                            tickColor="#C9D1DB")
            .configure_legend(orient="top", title=None, labelFontSize=12, symbolStrokeWidth=3)
            .configure_text(font="sans-serif"))


def sumbu_waktu(format_="%H:%M"):
    return alt.X("waktu:T", title=None, axis=alt.Axis(format=format_))


def warna_seri(domain, rentang):
    return alt.Color("Seri:N", scale=alt.Scale(domain=domain, range=rentang))


def grafik_est_ref(d, est, ref, judul_y, satuan, format_x="%d-%m %H:%M"):
    """Garis perkiraan vs acuan; garis dipotong per sesi agar celah antar sesi tidak tersambung."""
    kolom = [k for k in (est, ref) if k in d.columns]
    nama = {est: LABEL_EST, ref: LABEL_REF}
    panjang = d[["waktu", "sesi", *kolom]].melt(["waktu", "sesi"], var_name="kode", value_name="nilai")
    panjang["Seri"] = panjang["kode"].map(nama)
    garis = alt.Chart(panjang).mark_line(strokeWidth=2).encode(
        x=sumbu_waktu(format_x), y=alt.Y("nilai:Q", title=judul_y, scale=alt.Scale(zero=False)),
        color=warna_seri([LABEL_EST, LABEL_REF], [WARNA_EST, WARNA_REF]), detail="sesi:N",
        tooltip=[alt.Tooltip("waktu:T", title="Waktu", format="%d-%m %H:%M:%S"), "Seri:N",
                 alt.Tooltip("nilai:Q", title=satuan, format=".2f")])
    return gaya(garis)


# ---------------------------------------------------------------------------
# Tab
# ---------------------------------------------------------------------------
(tab_putar, tab_grafik, tab_muka, tab_sesi, tab_sim, tab_validasi, tab_data, tab_tentang) = st.tabs([
    ":material/play_circle: Putar ulang sumur", ":material/show_chart: Grafik pompa",
    ":material/water_drop: Tren muka air", ":material/monitor_heart: Sesi & kesehatan pompa",
    ":material/tune: Simulator apa-jika", ":material/fact_check: Validasi", ":material/table_chart: Data",
    ":material/info: Tentang sistem"])

# ---------------------------------------------------------------------------
# Putar ulang sumur
# ---------------------------------------------------------------------------
KECEPATAN = {"Lambat": 3, "Normal": 12, "Cepat": 30}
waktu_py = [t.to_pydatetime() for t in df["waktu"]]
waktu_np = df["waktu"].to_numpy()
n_baris = len(df)
sesi_arr = df["sesi"].to_numpy()
akhir_sesi = df.groupby("sesi").tail(1).index.to_numpy()   # indeks baris terakhir tiap sesi
langkah_data = df["waktu"].diff().median()
_dt_menit = df["waktu"].diff().dt.total_seconds().fillna(0).to_numpy() / 60
_dt_menit[_dt_menit > 5] = 0                                       # celah antar sesi: pompa mati
vol_kumulatif = np.cumsum(df["debit_est"].to_numpy() * _dt_menit) / 1000          # m³
energi_kum = np.cumsum(df["daya_aktif"].to_numpy() * _dt_menit / 60) / 1000      # kWh
vol_awal_sesi = {s: vol_kumulatif[i] for i, s in enumerate(sesi_arr) if i == 0 or sesi_arr[i - 1] != s}

ss = st.session_state
ss.setdefault("main", False)
if "t_putar" not in ss or not (waktu_py[0] <= ss.t_putar <= waktu_py[-1]):
    ss.t_putar = waktu_py[0]


def posisi(t):
    """(indeks baris terakhir <= t, pompa menyala?)"""
    i = int(np.clip(np.searchsorted(waktu_np, np.datetime64(t), side="right") - 1, 0, n_baris - 1))
    menyala = abs((pd.Timestamp(t) - df["waktu"].iloc[i]).total_seconds()) <= max(30, langkah_data.total_seconds() * 3)
    return i, menyala


def peristiwa():
    ev = []
    for _, r in sesi.iterrows():
        label = f" · set {r['set']}" if "set" in r and isinstance(r.get("set"), str) else ""
        ev.append((r["mulai"], f"Pompa menyala (sesi {r['sesi']}{label})", "on"))
        ev.append((r["selesai"], f"Pompa mati · {fmt(r['volume_m3'], 2)} m³", "off"))
    return ev


EV = peristiwa()


@st.fragment(run_every=0.5 if ss.main else None)
def putar_ulang():
    i, menyala = posisi(ss.t_putar)
    if ss.main:
        langkah = KECEPATAN.get(ss.get("kecepatan_putar") or "Normal", 12)
        if not menyala:                                   # sedang di celah -> lompat ke awal sesi berikut
            if i + 1 < n_baris:
                ss.t_putar = waktu_py[i + 1]
        else:
            ujung = akhir_sesi[np.searchsorted(akhir_sesi, i)]
            if i >= ujung:                                # akhir sesi -> tampilkan pompa mati sebentar
                if ujung >= n_baris - 1:
                    ss.main = False
                    st.rerun()
                ss.t_putar = waktu_py[i] + pd.Timedelta(minutes=2).to_pytimedelta()
            else:
                ss.t_putar = waktu_py[min(i + langkah, ujung)]
        i, menyala = posisi(ss.t_putar)

    k_kec, _ = st.columns([1, 1])
    b1, b2, b3, _ = st.columns([1.2, 0.6, 2, 2.2], vertical_alignment="bottom")
    if b1.button(":material/pause: Jeda" if ss.main else ":material/play_arrow: Putar", type="primary",
                 use_container_width=True):
        if not ss.main and i >= n_baris - 1:
            ss.t_putar = waktu_py[0]
        ss.main = not ss.main
        st.rerun()
    if b2.button(":material/first_page:", help="Kembali ke awal", use_container_width=True):
        ss.t_putar, ss.main = waktu_py[0], False
        st.rerun()
    berikut = next((e for e in EV if e[0] > pd.Timestamp(ss.t_putar)), None)
    if b3.button(":material/skip_next: Peristiwa berikutnya", use_container_width=True,
                 disabled=berikut is None, help="Lompat ke saat pompa menyala atau mati berikutnya."):
        t = berikut[0] + (pd.Timedelta(minutes=2) if berikut[2] == "off" else pd.Timedelta(0))
        ss.t_putar = min(t, t1).to_pydatetime()
        st.rerun()
    k_kec.segmented_control("Kecepatan", list(KECEPATAN), default="Normal", key="kecepatan_putar")
    st.slider("Waktu", min_value=waktu_py[0], max_value=waktu_py[-1], key="t_putar",
              step=langkah_data.to_pytimedelta(), format="DD-MM HH:mm:ss", label_visibility="collapsed")
    i, menyala = posisi(ss.t_putar)
    r = df.iloc[i]
    s_no = int(r["sesi"])

    debit = float(r["debit_est"]) if menyala else 0.0
    daya = float(r["daya_aktif"]) if menyala else 0.0
    kd_est = float(r["kedalaman_est"]) if ada_kd else 0.0
    kd_ref = float(r["kedalaman_ref"]) if ada_ref_kd else None
    vol_sesi = vol_kumulatif[i] - vol_awal_sesi[s_no]
    isi = vol_sesi * 1000 / kapasitas_l

    chip = ('<span class="mat-chip on"><span class="mat-dot"></span>POMPA MENYALA</span>' if menyala
            else f'<span class="mat-chip off">{ikon("power", 14)} POMPA MATI</span>')
    set_label = f" · set {r['set']}" if "set" in df.columns else ""
    chip_sesi = f'<span class="mat-chip ok">Sesi {s_no} dari {n_sesi}{set_label}</span>'
    persen = (pd.Timestamp(ss.t_putar) - t0) / (t1 - t0) * 100
    st.markdown(
        f'<div class="mat-live"><div class="mat-jam">{pd.Timestamp(ss.t_putar):%H:%M:%S}'
        f'<small>{HARI[pd.Timestamp(ss.t_putar).weekday()]}, {pd.Timestamp(ss.t_putar):%d-%m-%Y}</small></div>'
        f'{chip}{chip_sesi}'
        f'<div class="mat-progress"><div style="width:{persen:.1f}%"></div></div></div>',
        unsafe_allow_html=True)

    kiri, kanan = st.columns([2.6, 1], gap="medium")
    with kiri:
        st.markdown(f'<div class="mat-card"><div class="mat-card-title">{ikon("drop", 14)} Penampang sumur saat ini'
                    '</div>' + svg_sumur(menyala, debit, daya, kd_est, kd_ref, isi, vol_sesi,
                                         kapasitas_l=int(kapasitas_l)) + "</div>", unsafe_allow_html=True)
    with kanan:
        st.markdown(f'<div class="mat-card"><div class="mat-card-title">{ikon("gauge", 14)} Debit perkiraan</div>'
                    + svg_gauge(debit, 45, "L/menit", "garis = acuan", AIR,
                                float(r["debit_ref"]) if ada_ref_q and menyala else None) + "</div>",
                    unsafe_allow_html=True)
        baris = []
        for label, kol, des, sat in (("Tegangan", "tegangan", 1, "V"), ("Arus", "arus", 2, "A"),
                                     ("Faktor daya", "faktor_daya", 3, "")):
            if kol in df.columns:
                baris.append((label, f"{fmt(float(r[kol]), des)} {sat}" if menyala else "–"))
        baris.append(("Daya", f"{fmt(daya, 0)} W"))
        baris.append(("Energi per m³", f"{fmt(kwh_per_m3_sesaat(daya, debit), 3)} kWh" if menyala else "–"))
        st.markdown(f'<div class="mat-card"><div class="mat-card-title">{ikon("bolt", 14)} Listrik pompa</div>'
                    + "".join(f'<div class="mat-row"><span>{a}</span><b>{b}</b></div>' for a, b in baris)
                    + "</div>", unsafe_allow_html=True)
        st.markdown(f'<div class="mat-card"><div class="mat-card-title">{ikon("tank", 14)} Akumulasi sejak awal</div>'
                    f'<div class="mat-row"><span>Volume air</span><b>{fmt(vol_kumulatif[i], 2)} m³</b></div>'
                    f'<div class="mat-row"><span>Energi</span><b>{fmt(energi_kum[i], 3)} kWh</b></div>'
                    f'<div class="mat-row"><span>Biaya listrik</span><b>Rp {fmt(energi_kum[i] * tarif, 0)}</b></div>'
                    "</div>", unsafe_allow_html=True)

    bawah_kiri, bawah_kanan = st.columns([1.7, 1], gap="medium")
    with bawah_kiri:
        g = df[df["sesi"] == s_no]
        kolom = ["debit_est"] + (["debit_ref"] if ada_ref_q else [])
        panjang = g[["waktu", *kolom]].melt("waktu", var_name="kode", value_name="debit")
        panjang["Seri"] = panjang["kode"].map({"debit_est": LABEL_EST, "debit_ref": LABEL_REF})
        lalu = panjang[panjang["waktu"] <= r["waktu"]]
        lapis = [
            alt.Chart(panjang).mark_line(strokeWidth=1.5, opacity=0.25).encode(
                x=sumbu_waktu(), y=alt.Y("debit:Q", title="Debit (L/menit)", scale=alt.Scale(zero=False)),
                color=warna_seri([LABEL_EST, LABEL_REF], [WARNA_EST, WARNA_REF])),
            alt.Chart(lalu).mark_line(strokeWidth=2.2).encode(
                x="waktu:T", y="debit:Q", color=warna_seri([LABEL_EST, LABEL_REF], [WARNA_EST, WARNA_REF])),
        ]
        if menyala:
            lapis.append(alt.Chart(pd.DataFrame({"waktu": [r["waktu"]]})).mark_rule(color=NAVY).encode(x="waktu:T"))
        st.markdown(f'<div class="mat-card-title">{ikon("trend", 14)} Debit sesi {s_no}</div>', unsafe_allow_html=True)
        st.altair_chart(gaya(alt.layer(*lapis), tinggi=170), use_container_width=True)
    with bawah_kanan:
        sekarang = pd.Timestamp(ss.t_putar)
        lalu_ev = [e for e in EV if e[0] <= sekarang]
        terakhir = lalu_ev[-1] if lalu_ev else None
        dekat = [e for e in EV if abs((e[0] - sekarang).total_seconds()) < 18 * 3600][:8] or EV[:8]
        items = []
        for e in dekat:
            kelas = "baru" if e is terakhir else ("nanti" if e[0] > sekarang else "")
            ik = ("play", HIJAU) if e[2] == "on" else ("stop", "#6B7280")
            items.append(f'<li class="{kelas}"><span class="t">{HARI[e[0].weekday()]} {e[0]:%H:%M}</span>'
                         f'{ikon(ik[0], 14, ik[1])}<span>{e[1]}</span></li>')
        st.markdown(f'<div class="mat-card"><div class="mat-card-title">{ikon("wave", 14)} Peristiwa</div>'
                    f'<ul class="mat-events">{"".join(items)}</ul></div>', unsafe_allow_html=True)


with tab_putar:
    st.markdown(f'<div class="mat-section">{ikon("monitor", 18)} Putar ulang kondisi sumur dan pompa</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mat-note">Tekan <b>Putar</b> untuk memutar ulang rekaman seperti siaran langsung. '
                'Celah antar sesi dilewati otomatis. Segitiga kuning pada sumur menandai kedalaman acuan '
                '(sensor tekanan); garis biru adalah perkiraan dari sinyal listrik.</div>', unsafe_allow_html=True)
    putar_ulang()

# ---------------------------------------------------------------------------
# Grafik pompa
# ---------------------------------------------------------------------------
with tab_grafik:
    pilihan = ["Semua sesi"] + [f"Sesi {s} · {m:%d-%m %H:%M}" for s, m in zip(sesi["sesi"], sesi["mulai"])]
    pilih = st.selectbox("Tampilkan", pilihan, help="Pilih satu sesi untuk melihat detailnya.")
    d = df if pilih == "Semua sesi" else df[df["sesi"] == int(pilih.split()[1])]
    fx = "%d-%m %H:%M" if pilih == "Semua sesi" else "%H:%M"

    st.markdown(f'<div class="mat-section">{ikon("drop", 18)} Debit air</div>', unsafe_allow_html=True)
    st.markdown('<div class="mat-note">Perkiraan dari sinyal listrik dibanding flowmeter pembanding.</div>',
                unsafe_allow_html=True)
    st.altair_chart(grafik_est_ref(d, "debit_est", "debit_ref", "Debit (L/menit)", "L/menit", fx),
                    use_container_width=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f'<div class="mat-section">{ikon("bolt", 18)} Daya aktif pompa</div>', unsafe_allow_html=True)
        st.altair_chart(gaya(alt.Chart(d).mark_line(color=TOSKA, strokeWidth=1.8).encode(
            x=sumbu_waktu(fx), y=alt.Y("daya_aktif:Q", title="Daya (W)", scale=alt.Scale(zero=False)),
            detail="sesi:N", tooltip=[alt.Tooltip("waktu:T", format="%d-%m %H:%M:%S", title="Waktu"),
                                      alt.Tooltip("daya_aktif:Q", title="Daya (W)", format=".1f")]), 240),
            use_container_width=True)
    with c2:
        if "faktor_daya" in d.columns:
            st.markdown(f'<div class="mat-section">{ikon("wave", 18)} Faktor daya</div>', unsafe_allow_html=True)
            st.altair_chart(gaya(alt.Chart(d).mark_line(color="#6A5ACD", strokeWidth=1.8).encode(
                x=sumbu_waktu(fx), y=alt.Y("faktor_daya:Q", title="Faktor daya", scale=alt.Scale(zero=False)),
                detail="sesi:N", tooltip=[alt.Tooltip("waktu:T", format="%d-%m %H:%M:%S", title="Waktu"),
                                          alt.Tooltip("faktor_daya:Q", format=".3f")]), 240),
                use_container_width=True)

# ---------------------------------------------------------------------------
# Tren muka air
# ---------------------------------------------------------------------------
with tab_muka:
    st.markdown(f'<div class="mat-section">{ikon("ruler", 18)} Kedalaman muka air per sesi</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mat-note">Sumbu tegak dibalik: makin ke bawah berarti muka air makin dalam '
                '(sumur makin surut). Gunakan perkiraan sebagai <b>tren</b> (naik atau turun), bukan angka '
                'kedalaman tepat.</div>', unsafe_allow_html=True)
    if not ada_kd:
        st.info("Data tidak memuat kolom `kedalaman_est`.")
    else:
        kol = ["kedalaman_est"] + (["kedalaman_ref"] if ada_ref_kd else [])
        p = sesi[["sesi", "mulai", *kol]].melt(["sesi", "mulai"], var_name="kode", value_name="kedalaman")
        p["Seri"] = p["kode"].map({"kedalaman_est": LABEL_EST, "kedalaman_ref": LABEL_REF})
        dasar = alt.Chart(p).encode(
            x=alt.X("mulai:T", title=None, axis=alt.Axis(format="%d-%m %H:%M")),
            y=alt.Y("kedalaman:Q", title="Kedalaman muka air (m)", scale=alt.Scale(reverse=True, zero=False)),
            color=warna_seri([LABEL_EST, LABEL_REF], [WARNA_EST, WARNA_REF]),
            tooltip=["Seri:N", alt.Tooltip("sesi:Q", title="Sesi"),
                     alt.Tooltip("mulai:T", title="Mulai", format="%d-%m %H:%M"),
                     alt.Tooltip("kedalaman:Q", title="Kedalaman (m)", format=".2f")])
        lapis = [dasar.mark_line(strokeWidth=2.4), dasar.mark_point(filled=True, size=80)]
        if "set" in sesi.columns and (sesi["set"] == "uji").any():
            uji = sesi[sesi["set"] == "uji"]
            pita = pd.DataFrame({"mulai": [uji["mulai"].min() - pd.Timedelta(hours=1)],
                                 "selesai": [uji["selesai"].max() + pd.Timedelta(hours=1)], "t": ["Set uji"]})
            lapis.insert(0, alt.Chart(pita).mark_rect(color=KUNING, opacity=0.07).encode(
                x="mulai:T", x2="selesai:T"))
            lapis.insert(1, alt.Chart(pita).mark_text(align="left", dx=6, dy=10, color="#8A5A00", fontSize=11,
                                                      fontWeight="bold").encode(x="mulai:T", y=alt.value(0), text="t:N"))
        st.altair_chart(gaya(alt.layer(*lapis), 320), use_container_width=True)

        c1, c2, c3 = st.columns(3)
        d_est = sesi["kedalaman_est"].iloc[-1] - sesi["kedalaman_est"].iloc[0]
        c1.metric("Perubahan (perkiraan)", f"{tanda(d_est)} m",
                  help="Kedalaman sesi terakhir dikurangi sesi pertama. Positif = muka air turun.")
        if ada_ref_kd:
            d_ref = sesi["kedalaman_ref"].iloc[-1] - sesi["kedalaman_ref"].iloc[0]
            c2.metric("Perubahan (acuan)", f"{tanda(d_ref)} m")
            c3.metric("Galat kedalaman (set uji)", f"{fmt(gal_kd, 1)} %")
        with st.expander("Mengapa kedalaman hanya dipakai sebagai tren?"):
            st.markdown(
                "Daya listrik pompa naik lalu turun lagi ketika muka air makin dalam (lihat grafik *Daya vs "
                "kedalaman* di tab **Simulator apa-jika**). Akibatnya daya yang sama bisa muncul pada dua "
                "kedalaman berbeda. Model memakai fitur tambahan (faktor daya, bentuk arus) dan kalibrasi "
                "terhadap sensor tekanan, tetapi volume air dan kWh per m³ tetap lebih dapat diandalkan "
                "daripada angka kedalaman.")

# ---------------------------------------------------------------------------
# Sesi & kesehatan pompa
# ---------------------------------------------------------------------------
with tab_sesi:
    st.markdown(f'<div class="mat-section">{ikon("heart", 18)} Energi per m³ tiap sesi</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="mat-note">Pompa yang mulai aus atau tersumbat memerlukan energi lebih besar untuk '
                f'jumlah air yang sama. Sesi ditandai <b>Pantau</b> bila naik lebih dari {batas_sehat / 2:g}% dan '
                f'<b>Periksa</b> bila lebih dari {batas_sehat}% dibanding sesi pertama.</div>', unsafe_allow_html=True)
    sb = sesi.assign(label=[f"Sesi {s}" for s in sesi["sesi"]])
    acuan = pd.DataFrame({"y": [sesi["kwh_m3"].iloc[0] * (1 + batas_sehat / 100)],
                          "t": [f"batas periksa (+{batas_sehat}%)"]})
    batang = alt.Chart(sb).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=38).encode(
        x=alt.X("label:N", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("kwh_m3:Q", title="kWh per m³", scale=alt.Scale(zero=False, padding=12)),
        color=alt.Color("status:N", title=None, scale=alt.Scale(
            domain=["Normal", "Pantau", "Periksa"], range=[TOSKA, KUNING, MERAH])),
        tooltip=[alt.Tooltip("label:N", title="Sesi"), alt.Tooltip("mulai:T", title="Mulai", format="%d-%m %H:%M"),
                 alt.Tooltip("kwh_m3:Q", title="kWh/m³", format=".4f"),
                 alt.Tooltip("perubahan_persen:Q", title="Perubahan (%)", format="+.1f"), "status:N"])
    st.altair_chart(gaya(alt.layer(
        batang,
        alt.Chart(acuan).mark_rule(color=MERAH, strokeDash=[6, 4]).encode(y="y:Q"),
        alt.Chart(acuan).mark_text(align="right", x="width", dx=-4, dy=-7, color=MERAH, fontSize=11).encode(
            y="y:Q", text="t:N"),
    ), 280), use_container_width=True)

    st.markdown(f'<div class="mat-section">{ikon("tank", 18)} Ringkasan per sesi</div>', unsafe_allow_html=True)
    tabel = sesi.drop(columns=[c for c in ("selesai",) if c in sesi.columns]).copy()
    tabel["biaya_rp"] = tabel["energi_kwh"] * tarif
    st.dataframe(tabel, hide_index=True, use_container_width=True, column_config={
        "sesi": st.column_config.NumberColumn("Sesi", format="%d"),
        "mulai": st.column_config.DatetimeColumn("Mulai", format="DD-MM HH:mm"),
        "durasi_menit": st.column_config.NumberColumn("Durasi (menit)", format="%.0f"),
        "volume_m3": st.column_config.NumberColumn("Volume (m³)", format="%.3f"),
        "volume_ref_m3": st.column_config.NumberColumn("Volume acuan (m³)", format="%.3f"),
        "energi_kwh": st.column_config.NumberColumn("Energi (kWh)", format="%.3f"),
        "kwh_m3": st.column_config.NumberColumn("kWh/m³", format="%.4f"),
        "daya_w": st.column_config.NumberColumn("Daya rata-rata (W)", format="%.0f"),
        "faktor_daya": st.column_config.NumberColumn("Faktor daya", format="%.3f"),
        "kedalaman_est": st.column_config.NumberColumn("Kedalaman perk. (m)", format="%.2f"),
        "kedalaman_ref": st.column_config.NumberColumn("Kedalaman acuan (m)", format="%.2f"),
        "set": "Set",
        "perubahan_persen": st.column_config.NumberColumn("Perubahan kWh/m³ (%)", format="%+.1f"),
        "status": "Status",
        "biaya_rp": st.column_config.NumberColumn("Biaya (Rp)", format="%.0f"),
    })

# ---------------------------------------------------------------------------
# Simulator apa-jika
# ---------------------------------------------------------------------------
with tab_sim:
    st.markdown(f'<div class="mat-section">{ikon("pump", 18)} Simulator apa-jika: bagaimana jika sumur makin surut?'
                '</div>', unsafe_allow_html=True)
    st.markdown('<div class="mat-note">Geser kedalaman muka air dan lihat perubahan debit, daya, dan biaya. '
                'Model pompa sama dengan <code>sim/simulasi_pompa.py</code> (pompa rekaan, ilustratif).</div>',
                unsafe_allow_html=True)
    kol_in, kol_out = st.columns([1, 2.2], gap="large")
    with kol_in:
        kd = st.slider("Kedalaman muka air (m)", 2.0, 38.0, 13.0, 0.5)
        jam_hari = st.slider("Lama pompa menyala per hari (jam)", 0.5, 12.0, 1.5, 0.5)
        with st.expander("Parameter pompa (ilustratif)"):
            h0 = st.number_input("Tinggi angkat maksimum H₀ (m)", value=40.0, min_value=10.0, step=1.0)
            qmax = st.number_input("Debit maksimum (L/menit)", value=45.0, min_value=5.0, step=1.0)
            c_gesek = st.number_input("Rugi gesek pipa C", value=0.004, min_value=0.0, step=0.001, format="%.3f")
            eta = st.slider("Efisiensi pompa maksimum", 0.2, 0.8, 0.45, 0.01)
    pompa = Pompa(h0=h0, qmax=qmax, c=c_gesek, eta_p_max=eta)
    kd = min(kd, h0 - 0.5)
    q, h, p = (float(x) for x in pompa.titik_kerja(kd))
    spes = kwh_per_m3_sesaat(p, q)
    vol_hari = q * 60 * jam_hari / 1000
    biaya_bulan = p / 1000 * jam_hari * 30 * tarif
    kembar = kedalaman_kembar(pompa, kd)

    with kol_out:
        st.markdown('<div class="mat-kpis">' + "".join([
            kartu("Debit", fmt(q), "L/menit", f"tinggi angkat {fmt(h)} m", "", "drop"),
            kartu("Daya listrik", fmt(p, 0), "W", f"{fmt(spes, 3)} kWh/m³", "", "bolt"),
            kartu("Air per hari", fmt(vol_hari, 2), "m³", f"pompa {fmt(jam_hari, 1)} jam/hari", "", "tank"),
            kartu("Biaya listrik", f"Rp {fmt(biaya_bulan, 0)}", "", f"per bulan · Rp {fmt(spes * tarif, 0)}/m³",
                  "", "coins"),
        ]) + "</div>", unsafe_allow_html=True)
        if kembar is not None:
            st.warning(f"**Daya yang sama ({fmt(p, 0)} W) juga muncul pada kedalaman {fmt(kembar)} m.** Dari daya "
                       "saja, sistem tidak bisa membedakan kedua kedalaman ini. Karena itu model memakai faktor "
                       "daya, bentuk arus, dan kalibrasi, dan kedalaman ditampilkan sebagai tren.", icon="⚠️")
        else:
            st.info("Pada kedalaman ini daya listrik tidak memiliki kembaran: perkiraan kedalaman lebih "
                    "mudah dibedakan.", icon="ℹ️")

    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown(f'<div class="mat-section">{ikon("target", 18)} Titik kerja pompa</div>', unsafe_allow_html=True)
        hq = kurva_hq(pompa, kd)
        titik = pd.DataFrame({"debit": [q], "tinggi": [h]})
        st.altair_chart(gaya(alt.layer(
            alt.Chart(hq).mark_line(strokeWidth=2.4).encode(
                x=alt.X("debit:Q", title="Debit (L/menit)"), y=alt.Y("tinggi:Q", title="Tinggi angkat (m)"),
                color=alt.Color("Kurva:N", scale=alt.Scale(range=[NAVY, AIR])),
                strokeDash=alt.StrokeDash("Kurva:N", scale=alt.Scale(range=[[1, 0], [6, 4]]), legend=None)),
            alt.Chart(titik).mark_point(filled=True, size=160, color=MERAH, stroke="white", strokeWidth=2).encode(
                x="debit:Q", y="tinggi:Q", tooltip=[alt.Tooltip("debit:Q", format=".1f", title="Debit"),
                                                     alt.Tooltip("tinggi:Q", format=".1f", title="Tinggi angkat")]),
        ), 300), use_container_width=True)
    with g2:
        st.markdown(f'<div class="mat-section">{ikon("bolt", 18)} Daya vs kedalaman muka air</div>',
                    unsafe_allow_html=True)
        k = kurva(pompa)
        tk = pd.DataFrame({"kedalaman": [kd] + ([kembar] if kembar else []), "daya": [p] + ([p] if kembar else []),
                           "Titik": ["Kedalaman dipilih"] + (["Kedalaman kembar"] if kembar else [])})
        lapis = [
            alt.Chart(k).mark_line(color=TOSKA, strokeWidth=2.4).encode(
                x=alt.X("kedalaman:Q", title="Kedalaman muka air (m)"),
                y=alt.Y("daya:Q", title="Daya listrik (W)", scale=alt.Scale(zero=False)),
                tooltip=[alt.Tooltip("kedalaman:Q", format=".1f"), alt.Tooltip("daya:Q", format=".0f"),
                         alt.Tooltip("debit:Q", format=".1f")]),
            alt.Chart(pd.DataFrame({"y": [p]})).mark_rule(color="#8C99A6", strokeDash=[4, 4]).encode(y="y:Q"),
            alt.Chart(tk).mark_point(filled=True, size=150, stroke="white", strokeWidth=2).encode(
                x="kedalaman:Q", y="daya:Q",
                color=alt.Color("Titik:N", title=None, scale=alt.Scale(
                    domain=["Kedalaman dipilih", "Kedalaman kembar"], range=[MERAH, KUNING])),
                tooltip=["Titik:N", alt.Tooltip("kedalaman:Q", format=".1f"), alt.Tooltip("daya:Q", format=".0f")]),
        ]
        st.altair_chart(gaya(alt.layer(*lapis), 300), use_container_width=True)

# ---------------------------------------------------------------------------
# Validasi
# ---------------------------------------------------------------------------
with tab_validasi:
    st.markdown(f'<div class="mat-section">{ikon("target", 18)} Perkiraan dibanding alat ukur acuan</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="mat-note">Model dilatih pada set <b>kalibrasi</b> dan dinilai pada set <b>uji</b> '
                '(data yang tidak dipakai saat melatih). Angka galat yang dilaporkan adalah galat set uji.</div>',
                unsafe_allow_html=True)
    if not ada_ref_q:
        st.info("Data tidak memuat kolom acuan (`debit_ref`, `kedalaman_ref`).")
    else:
        rows = []
        himpunan = ["kalibrasi", "uji"] if "set" in df.columns else [None]
        for s in himpunan:
            dd = df if s is None else df[df["set"] == s]
            q_gal = float(((dd["debit_est"] - dd["debit_ref"]).abs() / dd["debit_ref"] * 100).mean())
            k_gal = (float(((dd["kedalaman_est"] - dd["kedalaman_ref"]).abs() / dd["kedalaman_ref"] * 100).mean())
                     if ada_kd and ada_ref_kd else np.nan)
            v_e, v_r = volume_m3(dd), volume_m3(dd, "debit_ref")
            rows.append({"Set": s or "semua", "Baris": len(dd), "Galat debit (%)": q_gal,
                         "Galat kedalaman (%)": k_gal, "Volume perkiraan (m³)": v_e, "Volume acuan (m³)": v_r,
                         "Selisih volume (%)": (v_e / v_r - 1) * 100 if v_r else np.nan})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, column_config={
            c: st.column_config.NumberColumn(format="%.2f") for c in
            ("Galat debit (%)", "Galat kedalaman (%)", "Volume perkiraan (m³)", "Volume acuan (m³)",
             "Selisih volume (%)")})

        def sebar(est, ref, judul, satuan):
            dd = df[["set", est, ref]].rename(columns={est: "est", ref: "ref"}) if "set" in df.columns else \
                df[[est, ref]].rename(columns={est: "est", ref: "ref"}).assign(set="semua")
            lo, hi = float(min(dd["est"].min(), dd["ref"].min())), float(max(dd["est"].max(), dd["ref"].max()))
            pad = (hi - lo) * 0.05 or 1
            garis = pd.DataFrame({"a": [lo - pad, hi + pad]})
            return gaya(alt.layer(
                alt.Chart(garis).mark_line(color="#8C99A6", strokeDash=[4, 4]).encode(x="a:Q", y="a:Q"),
                alt.Chart(dd).mark_circle(size=22, opacity=0.55).encode(
                    x=alt.X("ref:Q", title=f"Acuan ({satuan})", scale=alt.Scale(domain=[lo - pad, hi + pad])),
                    y=alt.Y("est:Q", title=f"Perkiraan ({satuan})", scale=alt.Scale(domain=[lo - pad, hi + pad])),
                    color=alt.Color("set:N", title=None, scale=alt.Scale(
                        domain=["kalibrasi", "uji"] if "set" in df.columns else ["semua"],
                        range=[AIR, MERAH] if "set" in df.columns else [AIR])),
                    tooltip=["set:N", alt.Tooltip("ref:Q", format=".2f"), alt.Tooltip("est:Q", format=".2f")]),
            ).properties(title=judul), 300)

        c1, c2 = st.columns(2, gap="large")
        c1.altair_chart(sebar("debit_est", "debit_ref", "Debit", "L/menit"), use_container_width=True)
        if ada_kd and ada_ref_kd:
            c2.altair_chart(sebar("kedalaman_est", "kedalaman_ref", "Kedalaman muka air", "m"),
                            use_container_width=True)
        st.caption("Titik di garis putus-putus berarti perkiraan sama dengan acuan. Titik yang membentuk garis datar "
                   "berarti model belum menangkap perubahan nilai acuan.")
        if simulasi:
            st.info("Pada data simulasi, galat dihitung dari hubungan yang sudah diketahui. Ini bukan klaim kinerja; "
                    "angka sebenarnya harus berasal dari rig dan sumur nyata.")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
with tab_data:
    st.markdown(f'<div class="mat-section">{ikon("tank", 18)} Data pengukuran</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mat-note">{fmt(len(df), 0)} baris · {len(df.columns)} kolom (termasuk kolom '
                '<code>sesi</code> yang dihitung dasbor)</div>', unsafe_allow_html=True)
    st.dataframe(df, hide_index=True, use_container_width=True, height=460, column_config={
        "waktu": st.column_config.DatetimeColumn("waktu", format="DD-MM-YYYY HH:mm:ss")})
    st.download_button("Unduh CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name=f"meter_air_tanah_{t0:%Y%m%d}.csv", mime="text/csv", icon=":material/download:")

# ---------------------------------------------------------------------------
# Tentang sistem
# ---------------------------------------------------------------------------
with tab_tentang:
    st.markdown(f'<div class="mat-section">{ikon("drop", 18)} Cara kerja sistem</div>', unsafe_allow_html=True)
    langkah = [
        ("bolt", "Ukur listrik pompa", "Sensor arus dan tegangan dipasang di panel pompa. Tidak ada yang "
         "dimasukkan ke sumur dan pipa tidak dipotong."),
        ("pump", "Terapkan kurva pompa", "Daya pompa bergantung pada debit dan tinggi angkat. Kurva pompa dan "
         "kalibrasi per pompa mengubah sinyal listrik menjadi perkiraan debit."),
        ("tank", "Hitung volume & tren", "Debit dijumlahkan menjadi volume air. Kedalaman muka air ditampilkan "
         "sebagai tren naik atau turun."),
        ("heart", "Pantau kesehatan pompa", "Kenaikan energi per m³ menandakan pompa aus, tersumbat, atau "
         "sumur makin surut."),
    ]
    st.markdown('<div class="mat-steps">' + "".join(
        f'<div class="mat-step"><div class="no">LANGKAH {i}</div><div class="ik">{ikon(ik, 22)}</div>'
        f'<h4>{j}</h4><p>{t}</p></div>' for i, (ik, j, t) in enumerate(langkah, 1)) + "</div>",
        unsafe_allow_html=True)

    kiri, kanan = st.columns([3, 2], gap="large")
    with kiri:
        for berkas, judul in (("diagram_blok.png", "Diagram blok"),
                              ("simulasi_pompa.png", "Simulasi prinsip (ilustratif)")):
            path = ROOT / "docs" / berkas
            if path.exists():
                st.markdown(f'<div class="mat-section">{ikon("cpu", 18)} {judul}</div>', unsafe_allow_html=True)
                st.image(str(path), use_container_width=True)
    with kanan:
        st.markdown(f'<div class="mat-section">{ikon("alert", 18)} Batasan penting</div>', unsafe_allow_html=True)
        st.markdown(
            "- Alat ini **bukan pengganti meter air resmi**. Fungsinya menguji silang dan memantau pompa yang "
            "belum bermeter.\n"
            "- Daya yang sama bisa muncul pada dua kedalaman berbeda, jadi kedalaman hanya dipakai sebagai "
            "**tren**.\n"
            "- Volume air dan kWh per m³ lebih dapat diandalkan daripada angka kedalaman.")
        st.markdown(f'<div class="mat-section">{ikon("shield", 18)} Keselamatan</div>', unsafe_allow_html=True)
        st.markdown(
            "- Pekerjaan pada panel pompa melibatkan listrik **220 V**.\n"
            "- Matikan MCB sebelum memasang sensor.\n"
            "- Gunakan **RCBO**.\n"
            "- Uji pertama di laboratorium dengan pendampingan dosen.")
        st.markdown(f'<div class="mat-section">{ikon("target", 18)} Pembeda</div>', unsafe_allow_html=True)
        st.markdown(
            "Prinsip ini sudah ada di literatur dan paten. Pembeda proyek ada pada penerapan untuk pompa fasilitas "
            "kota, kalibrasi dengan galat terukur, dan keluaran gabungan: energi per volume, tren muka air, serta "
            "kesehatan pompa.")
        st.info("**Status: tahap konsep (TKT 3).** Yang ada saat ini adalah simulasi, kerangka firmware yang belum "
                "diuji, dan dasbor ini. Belum ada hasil pengukuran.", icon="ℹ️")

st.markdown(footer(), unsafe_allow_html=True)
