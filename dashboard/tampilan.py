"""Elemen visual dasbor METER-AIR-TANAH: CSS, ikon, banner, diagram sumur, dan gauge (HTML/SVG murni)."""
import math

# Palet bertema air
NAVY = "#0D2B3E"
BIRU = "#0E6BA8"
AIR = "#1F8FC9"
TOSKA = "#0F8C8A"
KUNING = "#C98A12"
MERAH = "#B4413C"
HIJAU = "#2E7D5B"
ABU = "#C9D1DB"
TEKS2 = "#5B6573"

# Ikon garis sederhana (viewBox 24x24, stroke)
_IKON = {
    "drop": '<path d="M12 2.7s-6 6.6-6 11.3a6 6 0 0 0 12 0c0-4.7-6-11.3-6-11.3z"/>',
    "pump": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2"/>'
            '<path d="M12 3v7M12 14v7M3 12h7M14 12h7"/>',
    "tank": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/>'
            '<path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "ruler": '<path d="M21.3 8.7 8.7 21.3a1 1 0 0 1-1.4 0l-4.6-4.6a1 1 0 0 1 0-1.4L15.3 2.7a1 1 0 0 1 1.4 0'
             'l4.6 4.6a1 1 0 0 1 0 1.4z"/><path d="m7.5 10.5 2 2M10.5 7.5l2 2M13.5 4.5l2 2M4.5 13.5l2 2"/>',
    "bolt": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "trend": '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
    "down": '<path d="M22 17 13.5 8.5 8.5 13.5 2 7"/><path d="M16 17h6v-6"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
           '<path d="M9 2v3M15 2v3M9 19v3M15 19v3M19 9h3M19 15h3M2 9h3M2 15h3"/>',
    "wave": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "wifi": '<path d="M5 12.6a10 10 0 0 1 14 0M8.5 16.1a5 5 0 0 1 7 0M2 8.8a15 15 0 0 1 20 0"/><path d="M12 20h.01"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "coins": '<circle cx="9" cy="9" r="6"/><path d="M15.4 9.6A6 6 0 1 1 9.6 15.4"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>'
             '<path d="M3.5 12h5l1.5-3 3 6 1.5-3h6"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>'
             '<path d="M12 9v4M12 17h.01"/>',
    "power": '<path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.8 0"/>',
    "play": '<path d="m6 3 14 9-14 9z"/>',
    "stop": '<rect x="5" y="5" width="14" height="14" rx="2"/>',
}


def ikon(nama, ukuran=18, warna="currentColor", tebal=2):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ukuran}" height="{ukuran}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{warna}" stroke-width="{tebal}" stroke-linecap="round" '
            f'stroke-linejoin="round" style="vertical-align:middle;flex-shrink:0">{_IKON[nama]}</svg>')


CSS = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1400px;}
footer {visibility: hidden;}
h1, h2, h3 {letter-spacing: -0.01em;}

/* ---------- Banner ---------- */
.mat-hero {position:relative; overflow:hidden; border-radius:14px; padding:1.6rem 1.8rem 1.5rem;
    margin-bottom:1.1rem; color:#fff;
    background: radial-gradient(900px 260px at 90% -10%, rgba(64,196,220,.35), transparent 60%),
                linear-gradient(125deg, #0A2233 0%, #0D3A55 50%, #0E6BA8 100%);}
.mat-hero-ombak {position:absolute; left:0; right:0; bottom:0; width:100%; height:46px; opacity:.5;
    pointer-events:none;}
.mat-hero-ombak path {animation:mat-ombak 9s ease-in-out infinite alternate;}
@keyframes mat-ombak {to {transform:translateX(-60px);}}
.mat-hero-inner {position:relative; display:flex; gap:2rem; justify-content:space-between; align-items:center;
    flex-wrap:wrap; padding-bottom:.4rem;}
.mat-eyebrow {font-size:.72rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
    color:#8FD3E6; margin-bottom:.35rem; display:flex; align-items:center; gap:.4rem;}
.mat-title {font-size:2rem; font-weight:800; line-height:1.15; margin:0; color:#fff !important;
    padding:0 !important;}
.mat-title span {color:#7FDBEA;}
.mat-sub {color:#D2E6F0; font-size:.95rem; margin-top:.4rem; max-width:640px; line-height:1.5;}
.mat-meta {display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; font-size:.8rem;
    color:#B9D5E4; margin-top:.9rem;}
.mat-meta b {color:#fff; font-weight:600;}
.mat-meta .sep {color:rgba(255,255,255,.3);}
.mat-badge {display:inline-flex; align-items:center; gap:.3rem; padding:.22rem .65rem; border-radius:999px;
    font-weight:700; font-size:.7rem; letter-spacing:.05em;}
.mat-badge.sim {background:#FFF1D6; color:#7A4F00;}
.mat-badge.ukur {background:#D8F0E3; color:#1E5E43;}

.mat-flow {display:flex; flex-wrap:wrap; max-width:100%; align-items:center; gap:.35rem; background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.14); border-radius:12px; padding:.8rem 1rem;}
.mat-flow-node {display:flex; flex-direction:column; align-items:center; gap:.3rem; min-width:62px;
    font-size:.68rem; color:#D2E6F0; text-align:center;}
.mat-flow-node .bulat {width:40px; height:40px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2);}
.mat-flow-line {width:34px; height:3px; margin-bottom:1.1rem; border-radius:3px;
    background:repeating-linear-gradient(90deg,#7FDBEA 0 7px,transparent 7px 12px);
    background-size:24px 3px; animation:mat-geser 1s linear infinite;}
.mat-flow-line.listrik {height:2px; background:repeating-linear-gradient(90deg,#F6C343 0 5px,transparent 5px 10px);
    background-size:20px 2px; animation-duration:.7s;}
@keyframes mat-geser {to {background-position:24px 0;}}

/* ---------- Kartu KPI ---------- */
.mat-kpis {display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:.75rem; margin-bottom:1rem;}
.mat-kpi {position:relative; background:#FFFFFF; border:1px solid #E1E6ED; border-radius:12px;
    padding:.9rem 1rem; box-shadow:0 1px 2px rgba(16,24,40,.04); transition:transform .15s, box-shadow .15s;}
.mat-kpi:hover {transform:translateY(-2px); box-shadow:0 6px 16px rgba(16,24,40,.08);}
.mat-kpi::before {content:""; position:absolute; left:0; top:12px; bottom:12px; width:3px;
    border-radius:0 3px 3px 0; background:var(--aksen, #0E6BA8);}
.mat-kpi-head {display:flex; align-items:center; gap:.45rem;}
.mat-kpi-ikon {width:28px; height:28px; border-radius:8px; display:flex; align-items:center;
    justify-content:center; background:var(--aksen-bg, #E3F1F9); color:var(--aksen, #0E6BA8);}
.mat-kpi-label {font-size:.72rem; color:#5B6573; font-weight:600; text-transform:uppercase;
    letter-spacing:.04em; line-height:1.25;}
.mat-kpi-value {font-size:1.6rem; font-weight:700; color:#0D2B3E; margin-top:.45rem;
    font-variant-numeric:tabular-nums;}
.mat-kpi-value small {font-size:.9rem; font-weight:600; color:#5B6573; margin-left:.2rem;}
.mat-kpi-sub {font-size:.78rem; margin-top:.15rem; color:#5B6573;}
.mat-kpi-sub.ok {color:#1E7A50;} .mat-kpi-sub.bad {color:#B4413C;} .mat-kpi-sub.warn {color:#9A6700;}

.mat-note {font-size:.85rem; color:#5B6573; margin:-.2rem 0 .6rem 0;}
.mat-section {font-size:1.05rem; font-weight:650; color:#0D2B3E; margin:.4rem 0 .15rem 0;
    display:flex; align-items:center; gap:.45rem;}

/* ---------- Putar ulang ---------- */
.mat-live {display:flex; align-items:center; gap:1rem; flex-wrap:wrap; background:#F5FAFC;
    border:1px solid #DCE8EF; border-radius:12px; padding:.7rem 1rem; margin:.3rem 0 .8rem;}
.mat-jam {font-size:1.9rem; font-weight:700; color:#0D2B3E; font-variant-numeric:tabular-nums;}
.mat-jam small {display:block; font-size:.72rem; font-weight:600; color:#5B6573; letter-spacing:.04em;}
.mat-chip {display:inline-flex; align-items:center; gap:.35rem; padding:.3rem .75rem; border-radius:999px;
    font-weight:700; font-size:.78rem; letter-spacing:.04em;}
.mat-chip.on {background:#DFF1FA; color:#0B5B8F;}
.mat-chip.off {background:#E9ECF0; color:#3D4652;}
.mat-chip.ok {background:#E3F4EA; color:#1E6B47;}
.mat-chip.warn {background:#FFF1D6; color:#7A4F00;}
.mat-dot {width:8px; height:8px; border-radius:50%; background:currentColor; animation:mat-kedip 1.2s infinite;}
@keyframes mat-kedip {50% {opacity:.25;}}
.mat-progress {flex:1; min-width:160px; height:6px; background:#E1E6ED; border-radius:6px; overflow:hidden;}
.mat-progress > div {height:100%; background:linear-gradient(90deg,#0E6BA8,#1FB5C9);}

.mat-card {background:#fff; border:1px solid #E1E6ED; border-radius:12px; padding:.9rem 1rem; margin-bottom:.7rem;}
.mat-card-title {font-size:.75rem; font-weight:700; color:#5B6573; text-transform:uppercase;
    letter-spacing:.05em; margin-bottom:.4rem; display:flex; align-items:center; gap:.4rem;}
.mat-big {font-size:1.5rem; font-weight:700; color:#0D2B3E; font-variant-numeric:tabular-nums;}
.mat-big small {font-size:.85rem; font-weight:600; color:#5B6573; margin-left:.2rem;}
.mat-row {display:flex; justify-content:space-between; font-size:.82rem; color:#4A5563; padding:.22rem 0;
    border-bottom:1px dashed #E7ECF1;}
.mat-row:last-child {border-bottom:none;}
.mat-row b {color:#0D2B3E; font-variant-numeric:tabular-nums;}

.mat-svg .alir {stroke-dasharray:9 7; animation:mat-alir linear infinite;}
@keyframes mat-alir {to {stroke-dashoffset:-32;}}
.mat-svg .putar {transform-box:fill-box; transform-origin:center; animation:mat-putar linear infinite;}
@keyframes mat-putar {to {transform:rotate(360deg);}}
.mat-svg .riak {animation:mat-riak 2.4s ease-in-out infinite alternate;}
@keyframes mat-riak {to {transform:translateX(-8px);}}

.mat-events {list-style:none; padding:0; margin:0; font-size:.85rem;}
.mat-events li {display:flex; gap:.6rem; align-items:center; padding:.42rem 0; border-bottom:1px dashed #E1E6ED;
    color:#3D4652;}
.mat-events li:last-child {border-bottom:none;}
.mat-events .t {font-variant-numeric:tabular-nums; color:#5B6573; min-width:92px; font-size:.8rem;}
.mat-events li.baru {color:#0D2B3E; font-weight:600;}
.mat-events li.nanti {opacity:.4;}

/* ---------- Tentang ---------- */
.mat-steps {display:grid; grid-template-columns:repeat(auto-fit, minmax(170px,1fr)); gap:.8rem; margin:.4rem 0 1rem;}
.mat-step {background:#fff; border:1px solid #E1E6ED; border-radius:12px; padding:1rem;}
.mat-step .no {font-size:.7rem; font-weight:700; color:#0E6BA8; letter-spacing:.08em;}
.mat-step .ik {width:40px; height:40px; border-radius:10px; background:#E3F1F9; color:#0E6BA8;
    display:flex; align-items:center; justify-content:center; margin:.4rem 0 .6rem;}
.mat-step h4 {font-size:.95rem; margin:0 0 .3rem; color:#0D2B3E; padding:0;}
.mat-step p {font-size:.83rem; color:#4A5563; margin:0; line-height:1.5;}

.mat-footer {margin-top:2.5rem; padding-top:1rem; border-top:1px solid #E1E6ED; font-size:.78rem;
    color:#5B6573; display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem;}

[data-testid="stSidebar"] h3 {font-size:.78rem; text-transform:uppercase; letter-spacing:.06em;
    color:#5B6573; margin-top:.6rem;}
.mat-brand {display:flex; align-items:center; gap:.55rem; padding:.2rem 0 .6rem; border-bottom:1px solid #D7E3EA;
    margin-bottom:.4rem;}
.mat-brand .logo {width:34px; height:34px; border-radius:9px; background:linear-gradient(135deg,#0D3A55,#0E6BA8);
    display:flex; align-items:center; justify-content:center;}
.mat-brand b {display:block; font-size:.9rem; color:#0D2B3E; line-height:1.1;}
.mat-brand span {font-size:.72rem; color:#5B6573;}
.stTabs [data-baseweb="tab-list"] {gap:.15rem; border-bottom:1px solid #E1E6ED; flex-wrap:wrap;}
.stTabs [data-baseweb="tab"] {padding:.55rem .85rem; font-weight:600;}
</style>
"""

_OMBAK = """
<svg class="mat-hero-ombak" viewBox="0 0 1200 46" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 26 C150 6 300 46 450 26 S750 6 900 26 S1150 46 1300 26 V46 H0Z" fill="rgba(127,219,234,.18)"/>
  <path d="M0 34 C200 18 350 46 550 32 S850 18 1050 34 S1250 40 1300 34 V46 H0Z" fill="rgba(127,219,234,.22)"
        style="animation-duration:12s"/>
</svg>
"""


def banner(simulasi, nama_berkas, perangkat, rentang):
    badge = (f'<span class="mat-badge sim">{ikon("alert", 12)} DATA SIMULASI</span>' if simulasi
             else f'<span class="mat-badge ukur">{ikon("shield", 12)} DATA PENGUKURAN</span>')

    def node(nama_ikon, label, warna="#fff"):
        return (f'<div class="mat-flow-node"><div class="bulat">{ikon(nama_ikon, 20, warna)}</div>'
                f'{label}</div>')

    alur = (node("drop", "Sumur", "#7FDBEA") + '<div class="mat-flow-line"></div>'
            + node("pump", "Pompa") + '<div class="mat-flow-line"></div>'
            + node("tank", "Tandon") + '<div class="mat-flow-line listrik"></div>'
            + node("cpu", "Sensor<br>listrik", "#F6C343") + '<div class="mat-flow-line listrik"></div>'
            + node("monitor", "Dasbor"))
    return f"""
<div class="mat-hero">
  <div class="mat-hero-inner">
    <div>
      <div class="mat-eyebrow">{ikon("drop", 13, "#7FDBEA")} Pemantauan sumur dan pompa air tanah</div>
      <h1 class="mat-title">METER-<span>AIR-TANAH</span></h1>
      <div class="mat-sub">Perkiraan volume air tanah yang diambil, tren muka air sumur, dan kesehatan pompa
        dari sinyal listrik pompa, tanpa memasang apa pun ke dalam sumur atau memotong pipa.</div>
      <div class="mat-meta">{badge}
        <span>Berkas <b>{nama_berkas}</b></span><span class="sep">|</span>
        <span>Perangkat <b>{perangkat}</b></span><span class="sep">|</span><span>{rentang}</span>
      </div>
    </div>
    <div class="mat-flow">{alur}</div>
  </div>{_OMBAK}
</div>"""


def brand_sidebar():
    return (f'<div class="mat-brand"><div class="logo">{ikon("drop", 18, "#7FDBEA")}</div>'
            '<div><b>Meter Air Tanah</b><span>Volume · Muka air · Kesehatan pompa</span></div></div>')


def kartu(label, nilai, satuan="", sub="", kelas="", nama_ikon="drop"):
    aksen = {"ok": ("#1E7A50", "#E3F4EA"), "bad": (MERAH, "#FBE4E2"),
             "warn": ("#9A6700", "#FFF1D6")}.get(kelas, (BIRU, "#E3F1F9"))
    return (f'<div class="mat-kpi" style="--aksen:{aksen[0]};--aksen-bg:{aksen[1]}">'
            f'<div class="mat-kpi-head"><div class="mat-kpi-ikon">{ikon(nama_ikon, 16)}</div>'
            f'<div class="mat-kpi-label">{label}</div></div>'
            f'<div class="mat-kpi-value">{nilai}<small>{satuan}</small></div>'
            f'<div class="mat-kpi-sub {kelas}">{sub}</div></div>')


def footer():
    return ('<div class="mat-footer"><span>METER-AIR-TANAH · UNS Innovation Hackathon 2026 · '
            'Sub-tema C: manajemen energi dan lingkungan perkotaan</span>'
            '<span>Status: tahap konsep (TKT 3). Bukan pengganti meter air resmi.</span></div>')


# ---------------------------------------------------------------------------
# Diagram sumur hidup (untuk putar ulang)
# ---------------------------------------------------------------------------
def svg_sumur(menyala, debit, daya, kedalaman_est, kedalaman_ref, isi_tandon, volume_sesi,
              kedalaman_maks=30.0, kapasitas_l=1100):
    """Penampang sumur: muka air tanah, pompa permukaan, pipa ke tandon, sensor listrik, dan ESP32."""
    TANAH, BAWAH = 112, 322
    skala = (BAWAH - TANAH - 6) / kedalaman_maks

    def y_dari(k):
        return TANAH + max(0.0, min(k, kedalaman_maks)) * skala

    y_ma = y_dari(kedalaman_est)
    alir = 'class="alir"' if menyala else ""
    dur = max(0.35, 2.4 - debit / 22) if menyala else 0
    anim = f'style="animation-duration:{dur:.2f}s"' if menyala else ""
    w_pipa = AIR if menyala else "#B8C4CF"
    w_kabel = "#E0A526" if menyala else "#B8C4CF"

    s = [f'<svg class="mat-svg" viewBox="0 0 820 340" width="100%" xmlns="http://www.w3.org/2000/svg" '
         'font-family="sans-serif">',
         '<defs><pattern id="pasir" width="10" height="10" patternUnits="userSpaceOnUse">'
         '<circle cx="2" cy="3" r="1" fill="#D9CDBB"/><circle cx="7" cy="8" r="1" fill="#D9CDBB"/></pattern>'
         '<pattern id="akuifer" width="12" height="12" patternUnits="userSpaceOnUse">'
         '<circle cx="3" cy="4" r="1.3" fill="#A9D3E8"/><circle cx="9" cy="10" r="1.3" fill="#A9D3E8"/></pattern>'
         '<linearGradient id="langit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F9FC"/>'
         '<stop offset="1" stop-color="#FFFFFF"/></linearGradient></defs>']
    # langit, tanah kering, akuifer
    s.append(f'<rect x="0" y="0" width="820" height="{TANAH}" fill="url(#langit)"/>')
    s.append(f'<rect x="0" y="{TANAH}" width="820" height="{y_ma - TANAH:.1f}" fill="#F1EADF"/>')
    s.append(f'<rect x="0" y="{TANAH}" width="820" height="{y_ma - TANAH:.1f}" fill="url(#pasir)"/>')
    s.append(f'<rect x="0" y="{y_ma:.1f}" width="820" height="{340 - y_ma:.1f}" fill="#DCEEF6"/>')
    s.append(f'<rect x="0" y="{y_ma:.1f}" width="820" height="{340 - y_ma:.1f}" fill="url(#akuifer)"/>')
    s.append(f'<line x1="0" y1="{TANAH}" x2="820" y2="{TANAH}" stroke="#8C7B65" stroke-width="2.5"/>')
    s.append(f'<line x1="0" y1="{y_ma:.1f}" x2="820" y2="{y_ma:.1f}" stroke="{AIR}" stroke-width="1.6" '
             'stroke-dasharray="6 5"/>')
    s.append(f'<text x="812" y="{y_ma - 6:.1f}" text-anchor="end" font-size="11" font-weight="700" fill="{BIRU}">'
             f'Muka air tanah (perkiraan) {_koma(kedalaman_est)} m</text>')
    s.append(f'<text x="812" y="{TANAH + 16}" text-anchor="end" font-size="10" fill="#8C7B65">Tanah</text>')
    s.append(f'<text x="812" y="334" text-anchor="end" font-size="10" fill="{BIRU}">Akuifer (lapisan pembawa air)</text>')

    # penggaris kedalaman
    s.append(f'<line x1="104" y1="{TANAH}" x2="104" y2="{BAWAH}" stroke="#8C99A6" stroke-width="1"/>')
    for k in range(0, int(kedalaman_maks) + 1, 5):
        y = y_dari(k)
        s.append(f'<line x1="98" y1="{y:.1f}" x2="104" y2="{y:.1f}" stroke="#8C99A6"/>'
                 f'<text x="94" y="{y + 3.5:.1f}" text-anchor="end" font-size="9.5" fill="{TEKS2}">{k} m</text>')

    # sumur (casing) dan air di dalamnya
    s.append(f'<rect x="148" y="{TANAH - 18}" width="36" height="{BAWAH - TANAH + 18}" fill="#FFFFFF" '
             'stroke="#7D8A97" stroke-width="2"/>')
    s.append(f'<rect x="150" y="{y_ma:.1f}" width="32" height="{BAWAH - y_ma:.1f}" fill="#9FD0EA"/>')
    s.append(f'<g class="riak"><path d="M150 {y_ma:.1f} q4 -3 8 0 t8 0 t8 0 t8 0 t8 0" fill="none" '
             f'stroke="{AIR}" stroke-width="1.5"/></g>')
    s.append(f'<text x="166" y="{TANAH - 24}" text-anchor="middle" font-size="10" font-weight="700" '
             f'fill="{NAVY}">Sumur</text>')
    # penanda acuan
    if kedalaman_ref is not None:
        yr = y_dari(kedalaman_ref)
        s.append(f'<path d="M190 {yr:.1f} l9 -5 v10 z" fill="{KUNING}"/>'
                 f'<line x1="184" y1="{yr:.1f}" x2="232" y2="{yr:.1f}" stroke="{KUNING}" stroke-width="1.4" '
                 'stroke-dasharray="3 3"/>'
                 f'<text x="236" y="{yr + 4:.1f}" font-size="10" font-weight="700" fill="#8A5A00">'
                 f'acuan {_koma(kedalaman_ref)} m</text>')

    # pipa isap di dalam sumur
    s.append(f'<line x1="166" y1="{BAWAH - 8}" x2="166" y2="96" stroke="{w_pipa}" stroke-width="5" {alir} {anim}/>')
    s.append(f'<rect x="159" y="{BAWAH - 10}" width="14" height="8" rx="2" fill="#7D8A97"/>')
    s.append(f'<line x1="166" y1="96" x2="218" y2="96" stroke="{w_pipa}" stroke-width="5" {alir} {anim}/>')

    # pompa
    s.append(f'<rect x="218" y="72" width="76" height="40" rx="9" fill="#EAF4FA" stroke="{BIRU}" stroke-width="2"/>')
    kelas_putar = 'class="putar"' if menyala else ""
    putar = f'style="animation-duration:{max(0.25, 1.2 - debit / 50):.2f}s"' if menyala else ""
    s.append(f'<g {kelas_putar} {putar}><circle cx="240" cy="92" r="13" fill="#fff" stroke="{BIRU}" stroke-width="2"/>'
             f'<path d="M240 79 v26 M227 92 h26 M231 83 l18 18 M249 83 l-18 18" stroke="{BIRU}" stroke-width="1.6"/></g>')
    s.append(f'<text x="276" y="90" text-anchor="middle" font-size="10" font-weight="700" fill="{NAVY}">POMPA</text>')
    s.append(f'<text x="276" y="103" text-anchor="middle" font-size="9" font-weight="700" '
             f'fill="{HIJAU if menyala else "#8C99A6"}">{"MENYALA" if menyala else "MATI"}</text>')

    # pipa tekan ke tandon
    s.append(f'<path d="M294 84 H596 V18 H654 V26" fill="none" stroke="{w_pipa}" stroke-width="5" '
             f'stroke-linejoin="round" {alir} {anim}/>')
    # tandon
    tinggi_t = 72
    isi = max(0.0, min(isi_tandon, 1.0))
    s.append(f'<line x1="626" y1="98" x2="620" y2="{TANAH}" stroke="#7D8A97" stroke-width="3"/>'
             f'<line x1="690" y1="98" x2="696" y2="{TANAH}" stroke="#7D8A97" stroke-width="3"/>')
    s.append(f'<rect x="616" y="26" width="84" height="{tinggi_t}" rx="10" fill="#fff" stroke="{BIRU}" stroke-width="2"/>')
    s.append(f'<rect x="618" y="{26 + 2 + (tinggi_t - 4) * (1 - isi):.1f}" width="80" '
             f'height="{(tinggi_t - 4) * isi:.1f}" rx="8" fill="#9FD0EA"/>')
    s.append(f'<text x="658" y="60" text-anchor="middle" font-size="15" font-weight="800" fill="{NAVY}">'
             f'{isi * 100:.0f}%</text>')
    s.append(f'<text x="658" y="76" text-anchor="middle" font-size="9" fill="{TEKS2}">Tandon {kapasitas_l:,} L</text>'
             .replace(",", "."))
    if menyala:
        s.append(f'<path d="M654 26 v{max(2, (tinggi_t - 4) * (1 - isi) - 2):.0f}" stroke="{AIR}" stroke-width="3" '
                 f'class="alir" style="animation-duration:.6s"/>')

    # panel listrik, sensor, ESP32
    s.append(f'<rect x="330" y="10" width="92" height="46" rx="8" fill="#F7F9FC" stroke="#8C99A6"/>')
    s.append(f'<g transform="translate(338 22)">{ikon("power", 20, NAVY)}</g>')
    s.append(f'<text x="364" y="30" font-size="10" font-weight="700" fill="{NAVY}">Panel</text>'
             f'<text x="364" y="43" font-size="10" fill="{TEKS2}">pompa</text>')
    kabel_anim = 'class="alir" style="animation-duration:.7s"' if menyala else ""
    s.append(f'<path d="M330 33 H256 V72" fill="none" stroke="{w_kabel}" stroke-width="3" {kabel_anim}/>')
    s.append(f'<circle cx="300" cy="33" r="10" fill="none" stroke="{KUNING}" stroke-width="3"/>')
    s.append(f'<text x="300" y="60" text-anchor="middle" font-size="9" fill="{TEKS2}">Sensor CT</text>')
    s.append(f'<path d="M300 23 V6 H452 V12" fill="none" stroke="{KUNING}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    s.append(f'<rect x="440" y="12" width="104" height="44" rx="8" fill="#FFF8E8" stroke="{KUNING}"/>')
    s.append(f'<text x="492" y="30" text-anchor="middle" font-size="10" font-weight="700" fill="#7A4F00">ESP32</text>')
    s.append(f'<text x="492" y="44" text-anchor="middle" font-size="9" fill="#7A4F00">V, I, daya, PF</text>')
    s.append(f'<g transform="translate(552 18)">{ikon("wifi", 18, KUNING if menyala else "#B8C4CF")}</g>')

    # meteran volume
    s.append(f'<rect x="330" y="{TANAH + 14}" width="196" height="64" rx="10" fill="#0D2B3E" opacity=".92"/>')
    s.append(f'<text x="344" y="{TANAH + 32}" font-size="9" font-weight="700" fill="#8FD3E6" letter-spacing="1">'
             'VOLUME SESI INI (PERKIRAAN)</text>')
    s.append(f'<text x="344" y="{TANAH + 62}" font-size="26" font-weight="800" fill="#FFFFFF" '
             f'font-family="ui-monospace,Consolas,monospace">{_koma(volume_sesi, 3)}</text>')
    s.append(f'<text x="512" y="{TANAH + 62}" text-anchor="end" font-size="13" font-weight="700" fill="#8FD3E6">m³</text>')
    s.append(f'<text x="560" y="{TANAH + 34}" font-size="10" fill="{TEKS2}">Debit</text>'
             f'<text x="560" y="{TANAH + 52}" font-size="15" font-weight="800" fill="{NAVY}">{_koma(debit)} L/mnt</text>'
             f'<text x="560" y="{TANAH + 70}" font-size="10" fill="{TEKS2}">Daya {_koma(daya, 0)} W</text>')
    s.append("</svg>")
    return "".join(s)


def _koma(x, des=1):
    s = f"{x:,.{des}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def svg_gauge(nilai, maks, satuan, label, warna=AIR, tanda=None):
    """Gauge setengah lingkaran. tanda = garis acuan opsional."""
    f = max(0.0, min(nilai / maks, 1.0)) if maks else 0
    busur = "M 20 100 A 80 80 0 0 1 180 100"
    garis = ""
    if tanda is not None and maks:
        fb = max(0.0, min(tanda / maks, 1.0))
        xb, yb = 100 - 80 * math.cos(math.pi * fb), 100 - 80 * math.sin(math.pi * fb)
        xi, yi = 100 - 93 * math.cos(math.pi * fb), 100 - 93 * math.sin(math.pi * fb)
        garis = f'<line x1="{xb:.1f}" y1="{yb:.1f}" x2="{xi:.1f}" y2="{yi:.1f}" stroke="{NAVY}" stroke-width="2.5"/>'
    return f"""
<svg viewBox="0 0 200 130" width="100%" style="max-width:250px;display:block;margin:auto"
     xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <path d="{busur}" fill="none" stroke="#EDF0F4" stroke-width="16" stroke-linecap="round"/>
  <path d="{busur}" fill="none" stroke="{warna}" stroke-width="16" stroke-linecap="round"
        pathLength="100" stroke-dasharray="{f * 100:.1f} 100"/>
  {garis}
  <text x="100" y="88" text-anchor="middle" font-size="28" font-weight="800" fill="{NAVY}">{_koma(nilai)}</text>
  <text x="100" y="106" text-anchor="middle" font-size="11" fill="{TEKS2}">{satuan} · {label}</text>
  <text x="20" y="124" text-anchor="middle" font-size="9" fill="{TEKS2}">0</text>
  <text x="180" y="124" text-anchor="middle" font-size="9" fill="{TEKS2}">{maks:.0f}</text>
</svg>"""
