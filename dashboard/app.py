"""Dasbor METER-AIR-TANAH (Streamlit).

Jalankan:  streamlit run dashboard/app.py
Sumber data: CSV (contoh simulasi di data/sample, atau unggah CSV hasil rig).
Nanti diganti membaca dari basis data (Supabase) tanpa mengubah fungsi hitung.
"""
from pathlib import Path
import streamlit as st
from logika import muat, volume_m3, energi_kwh, kwh_per_m3, galat_persen, tren_harian

CONTOH = Path(__file__).resolve().parents[1] / "data" / "sample" / "pengukuran_sim.csv"

st.set_page_config(page_title="METER-AIR-TANAH", layout="wide")
st.title("METER-AIR-TANAH")
st.caption("Perkiraan volume air tanah, tren muka air, dan kesehatan pompa dari sinyal listrik pompa.")

with st.sidebar:
    st.header("Sumber data")
    unggah = st.file_uploader("Unggah CSV pengukuran", type="csv")
    df = muat(unggah if unggah is not None else CONTOH)
    simulasi = unggah is None
    if simulasi:
        st.warning("Menampilkan DATA SIMULASI, bukan hasil pengukuran.")
    st.write(f"{len(df)} baris, {df['waktu'].min():%d %b %Y} sampai {df['waktu'].max():%d %b %Y}")

tab1, tab2, tab3 = st.tabs(["Ringkasan", "Tren muka air", "Validasi"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Volume air (perkiraan)", f"{volume_m3(df):.2f} m³")
    c2.metric("Energi pompa", f"{energi_kwh(df):.2f} kWh")
    c3.metric("Energi per volume", f"{kwh_per_m3(df):.2f} kWh/m³")
    st.line_chart(df.set_index("waktu")[["daya_aktif"]])

with tab2:
    st.write("Rata-rata per jam. Gunakan sebagai **tren** (naik atau turun), bukan angka kedalaman tepat.")
    st.line_chart(tren_harian(df, "kedalaman_est"))

with tab3:
    st.write("Perbandingan estimasi terhadap alat pembanding (flowmeter dan sensor tekanan).")
    c1, c2 = st.columns(2)
    c1.metric("Galat debit (set uji)", f"{galat_persen(df, 'debit_est', 'debit_ref'):.1f} %")
    c2.metric("Galat kedalaman (set uji)", f"{galat_persen(df, 'kedalaman_est', 'kedalaman_ref'):.1f} %")
    st.line_chart(df.set_index("waktu")[["debit_ref", "debit_est"]])
    if simulasi:
        st.info("Pada data simulasi, galat kecil karena data dibuat dengan hubungan yang sudah diketahui. "
                "Ini bukan klaim kinerja; angka sebenarnya harus berasal dari rig dan sumur nyata.")
