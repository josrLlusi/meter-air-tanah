"""Simulator apa-jika: model pompa yang sama dengan sim/simulasi_pompa.py.

Kurva pompa H = H0 - K Q^2, kurva sistem H = kedalaman + C Q^2, efisiensi pompa parabola di sekitar BEP.
Semua parameter ILUSTRATIF (pompa rekaan), bukan data pompa tertentu.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

RHO, G = 1000.0, 9.81


@dataclass
class Pompa:
    h0: float = 40.0        # tinggi angkat shut-off [m]
    qmax: float = 45.0      # debit maksimum [L/menit]
    c: float = 0.004        # rugi gesek pipa [m/(L/menit)^2]
    qbep: float = 25.0      # debit titik efisiensi terbaik [L/menit]
    eta_p_max: float = 0.45
    eta_m: float = 0.70

    @property
    def k(self):
        return self.h0 / self.qmax ** 2

    def eta_pompa(self, q):
        x = np.asarray(q) / self.qbep
        return np.clip(self.eta_p_max * (2 * x - x ** 2), 0.05, None)

    def titik_kerja(self, kedalaman):
        """Debit [L/menit], tinggi angkat [m], daya listrik [W] pada kedalaman muka air [m]."""
        kedalaman = np.asarray(kedalaman, dtype=float)
        q = np.sqrt(np.clip(self.h0 - kedalaman, 0, None) / (self.k + self.c))
        h = self.h0 - self.k * q ** 2
        p_hid = RHO * G * (q / 60000.0) * h
        p_el = p_hid / (self.eta_pompa(q) * self.eta_m)
        return q, h, p_el

    def kedalaman_maks(self):
        return self.h0


def kwh_per_m3_sesaat(daya_w, debit_lpm):
    """Energi spesifik: kW / (m3/jam)."""
    return (daya_w / 1000.0) / (debit_lpm * 0.06) if debit_lpm > 0 else float("nan")


def kurva(pompa, dari=1.0, sampai=None, n=200):
    sampai = sampai or pompa.h0 - 1
    d = np.linspace(dari, sampai, n)
    q, h, p = pompa.titik_kerja(d)
    return pd.DataFrame({"kedalaman": d, "debit": q, "tinggi": h, "daya": p,
                         "kwh_m3": (p / 1000.0) / (q * 0.06)})


def kedalaman_kembar(pompa, kedalaman, toleransi_w=1.0):
    """Kedalaman lain yang menghasilkan daya listrik (hampir) sama. None bila tidak ada.
    Inilah alasan kedalaman hanya dipakai sebagai tren."""
    _, _, p0 = pompa.titik_kerja(kedalaman)
    k = kurva(pompa, n=2000)
    lain = k[(k["kedalaman"] - kedalaman).abs() > 1.0]
    if lain.empty:
        return None
    i = (lain["daya"] - float(p0)).abs().idxmin()
    if abs(lain.loc[i, "daya"] - float(p0)) > max(toleransi_w, 0.01 * float(p0)):
        return None
    return float(lain.loc[i, "kedalaman"])


def kurva_hq(pompa, kedalaman, n=120):
    """Kurva pompa dan kurva sistem untuk grafik titik kerja."""
    q = np.linspace(0, pompa.qmax, n)
    return pd.DataFrame({
        "debit": np.concatenate([q, q]),
        "tinggi": np.concatenate([pompa.h0 - pompa.k * q ** 2, kedalaman + pompa.c * q ** 2]),
        "Kurva": ["Kurva pompa"] * n + ["Kurva sistem (sumur + pipa)"] * n,
    })
