import base64
import io
import os
import statistics

import pandas as pd
import streamlit as st

# =============================================================================
# HELPERS
# =============================================================================

def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


SQRT3 = 1.732

TARIF_REFERENSI = [
    ("R-1/TR 450 VA", 415.00),
    ("R-1/TR 900 VA (bersubsidi)", 605.00),
    ("R-1/TR 900 VA (non-subsidi/RTM)", 1352.00),
    ("R-1/TR 1.300 VA", 1444.70),
    ("R-1/TR 2.200 VA", 1444.70),
    ("R-2/TR 3.500–5.500 VA", 1699.53),
    ("R-3/TR,TM > 6.600 VA", 1699.53),
    ("B-2/TR 6.600 VA–200 kVA", 1444.70),
    ("B-3/TM,TT > 200 kVA", 1114.74),
    ("I-3/TM > 200 kVA", 1114.74),
    ("I-4/TT > 30.000 kVA", 996.74),
    ("P-1/TR 6.600 VA–200 kVA", 1699.53),
]


def calc_rata_rata(nilai_bulanan: list) -> float:
    nilai_valid = [v for v in nilai_bulanan if v is not None]
    return statistics.mean(nilai_valid) if nilai_valid else 0.0


def calc_arus_3phase(tegangan, arus_r, arus_s, arus_t, pf, jam_nyala_per_hari, jumlah_hari) -> float:
    rata_arus = statistics.mean([arus_r, arus_s, arus_t])
    daya_kw = (tegangan * rata_arus * SQRT3 * pf) / 1000
    total_jam = jam_nyala_per_hari * jumlah_hari
    return daya_kw * total_jam


def calc_arus_1phase(tegangan, arus, pf, jam_nyala_per_hari, jumlah_hari) -> float:
    daya_kw = (tegangan * arus * pf) / 1000
    total_jam = jam_nyala_per_hari * jumlah_hari
    return daya_kw * total_jam


def calc_tegangan_turun(v_supply, v_display, arus, cos_a, total_jam) -> float:
    selisih_v = v_supply - v_display
    return (selisih_v * arus * cos_a * total_jam) / 1000


def kpi_card(icon: str, label: str, value: str, delta: str, tone: str = "neutral") -> str:
    tone_colors = {
        "neutral": ("#94a3b8", "rgba(148, 163, 184, 0.12)"),
        "danger": ("#fca5a5", "rgba(239, 68, 68, 0.15)"),
        "success": ("#86efac", "rgba(34, 197, 94, 0.15)"),
    }
    color, bg = tone_colors.get(tone, tone_colors["neutral"])
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <span class="kpi-delta" style="color:{color}; background:{bg};">{delta}</span>
    </div>
    """


def build_excel_summary(rows: list) -> bytes:
    df = pd.DataFrame(rows, columns=["Item", "Nilai"])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Ringkasan Koreksi P2TL", index=False)
    return buffer.getvalue()


# =============================================================================
# KONFIGURASI HALAMAN & STYLE
# =============================================================================

logo_path = "logo_pln.png"
logo_base64 = get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""

st.set_page_config(
    page_title="Koreksi Token P2TL - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }

        .hero-banner {
            background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
            border-radius: 16px; padding: 24px 28px; color: white; margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 168, 232, 0.2);
            display: flex; align-items: center; gap: 20px;
        }
        .hero-logo-img { width: 70px; height: auto; border-radius: 8px; background: white; padding: 4px; }
        .hero-badge {
            background-color: #ffb703; color: #000; font-weight: 800; font-size: 0.75rem;
            padding: 4px 12px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 6px;
        }
        .hero-title { font-size: 1.8rem; font-weight: 800; margin: 0; }

        .step-card {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 22px; margin-bottom: 20px;
        }
        .step-header {
            display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
            border-bottom: 1px solid #334155; padding-bottom: 10px;
        }
        .step-title { font-size: 1.15rem; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 10px; }
        .step-number {
            background: linear-gradient(135deg, #0284c7, #0369a1); color: white; font-size: 0.85rem; font-weight: 700;
            width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
        }

        .kpi-card {
            background: linear-gradient(160deg, #1e293b 0%, #172033 100%); border: 1px solid #2b3a52;
            border-radius: 16px; padding: 18px 20px; height: 100%;
        }
        .kpi-icon { font-size: 1.4rem; margin-bottom: 8px; display: inline-block; }
        .kpi-label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em; }
        .kpi-value { font-size: 1.55rem; font-weight: 800; color: #f8fafc; margin: 4px 0 8px 0; }
        .kpi-delta {
            display: inline-flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 700;
            padding: 3px 9px; border-radius: 999px;
        }

        .stButton > button {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; border: none !important;
            border-radius: 10px !important; font-weight: 700 !important; padding: 0.75rem 1.5rem !important;
        }

        .result-banner-tagih {
            background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); border: 1px solid #ef4444;
            border-radius: 16px; padding: 24px 28px; margin: 12px 0;
        }
        .result-banner-kembali {
            background: linear-gradient(135deg, #14532d 0%, #052e16 100%); border: 1px solid #22c55e;
            border-radius: 16px; padding: 24px 28px; margin: 12px 0;
        }
        .result-label { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #e2e8f0; margin-bottom: 6px; }
        .result-value { font-size: 2rem; font-weight: 800; color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_html = (
    f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else "⚡"
)

st.markdown(
    f"""
    <div class="hero-banner">
        <div>{logo_html}</div>
        <div>
            <span class="hero-badge">MODUL 8</span>
            <div class="hero-title">⚖️ Koreksi Token P2TL (Tagihan / Pengembalian)</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. Pilih **metode perhitungan** sesuai kondisi lapangan/berita acara P2TL — replikasi 4 metode
           yang biasa dipakai (rata-rata pemakaian, arus 3 phase, arus 1 phase, tegangan turun salah satu phase).
        2. Isi data pengukuran sesuai metode yang dipilih, lalu isi **EMIN** (energi minimum, kWh)
           dan **tarif per kWh** yang berlaku untuk golongan/daya pelanggan tersebut.
        3. Sistem menghitung selisih antara pemakaian hasil koreksi dan EMIN, dikalikan jumlah bulan periode anomali,
           lalu dikonversi ke Rupiah/token.
        4. **Selisih positif** → kWh kurang tagih, perlu **tambahan tagihan/token** ke pelanggan.
           **Selisih negatif** → pelanggan terlanjur membayar lebih, perlu **dikembalikan**.
        5. Angka EMIN dan tarif sebaiknya dicek ulang sesuai golongan tarif & ketentuan P2TL terbaru — sistem ini
           hanya alat bantu hitung, bukan pengganti verifikasi berita acara resmi.
        """
    )

# =============================================================================
# STEP 1 — PILIH METODE
# =============================================================================

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">1</span> Pilih Metode Perhitungan</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metode = st.radio(
    "Metode:",
    [
        "📊 Rata-rata Pemakaian (3 / 6 Bulan)",
        "🔌 Berdasarkan Arus 3 Phase",
        "🔌 Berdasarkan Arus 1 Phase",
        "⚡ Tegangan Turun (Salah Satu Phase Tidak Terukur)",
    ],
    horizontal=False,
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">2</span> Data Pengukuran / Riwayat Pemakaian</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pemakaian_terhitung = 0.0
jumlah_bulan_periode = 1

if metode.startswith("📊"):
    sub_metode = st.selectbox("Jumlah bulan pembanding:", ["3 Bulan Terakhir", "6 Bulan Terakhir"])
    n_bulan = 3 if sub_metode == "3 Bulan Terakhir" else 6

    cols = st.columns(min(n_bulan, 3))
    nilai_bulanan = []
    for i in range(n_bulan):
        with cols[i % 3]:
            v = st.number_input(f"Pemakaian Bulan {i + 1} (kWh)", min_value=0.0, value=0.0, step=1.0, key=f"bln_{i}")
            nilai_bulanan.append(v)

    pemakaian_terhitung = calc_rata_rata(nilai_bulanan)
    st.caption(f"📐 Rata-rata pemakaian: **{pemakaian_terhitung:,.2f} kWh/bulan**")

elif metode.startswith("🔌 Berdasarkan Arus 3"):
    c1, c2, c3 = st.columns(3)
    with c1:
        tegangan = st.number_input("Tegangan (V)", min_value=0.0, value=380.0, step=1.0)
        pf = st.number_input("Faktor Daya (Cos φ)", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
    with c2:
        arus_r = st.number_input("Arus R (A)", min_value=0.0, value=0.0, step=0.1)
        arus_s = st.number_input("Arus S (A)", min_value=0.0, value=0.0, step=0.1)
        arus_t = st.number_input("Arus T (A)", min_value=0.0, value=0.0, step=0.1)
    with c3:
        jam_nyala = st.number_input("Jam Nyala per Hari (jam)", min_value=0.0, value=20.0, step=0.5)
        jumlah_hari = st.number_input("Jumlah Hari Periode", min_value=1, value=30, step=1)

    pemakaian_terhitung = calc_arus_3phase(tegangan, arus_r, arus_s, arus_t, pf, jam_nyala, jumlah_hari)
    st.caption(
        f"📐 Rata-rata arus: **{statistics.mean([arus_r, arus_s, arus_t]):.3f} A** · "
        f"Pemakaian terhitung: **{pemakaian_terhitung:,.2f} kWh**"
    )

elif metode.startswith("🔌 Berdasarkan Arus 1"):
    c1, c2, c3 = st.columns(3)
    with c1:
        tegangan = st.number_input("Tegangan (V)", min_value=0.0, value=220.0, step=1.0)
    with c2:
        arus = st.number_input("Arus (A)", min_value=0.0, value=0.0, step=0.1)
        pf = st.number_input("Faktor Daya (Cos φ)", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
    with c3:
        jam_nyala = st.number_input("Jam Nyala per Hari (jam)", min_value=0.0, value=12.0, step=0.5)
        jumlah_hari = st.number_input("Jumlah Hari Periode", min_value=1, value=30, step=1)

    pemakaian_terhitung = calc_arus_1phase(tegangan, arus, pf, jam_nyala, jumlah_hari)
    st.caption(f"📐 Pemakaian terhitung: **{pemakaian_terhitung:,.2f} kWh**")

else:  # Tegangan Turun
    c1, c2, c3 = st.columns(3)
    with c1:
        v_supply = st.number_input("V Supply (V)", min_value=0.0, value=220.0, step=1.0)
        v_display = st.number_input("V Display (V)", min_value=0.0, value=0.0, step=1.0)
    with c2:
        arus = st.number_input("Arus (A)", min_value=0.0, value=0.0, step=0.1)
        cos_a = st.number_input("Cos α", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
    with c3:
        total_jam = st.number_input("Total Jam (JN × Jumlah Hari)", min_value=0.0, value=0.0, step=1.0)

    selisih_v = v_supply - v_display
    pemakaian_terhitung = calc_tegangan_turun(v_supply, v_display, arus, cos_a, total_jam)
    st.caption(f"📐 Selisih tegangan: **{selisih_v:.1f} V** · Pemakaian tidak terukur: **{pemakaian_terhitung:,.2f} kWh**")

# =============================================================================
# STEP 3 — EMIN, TARIF, PERIODE
# =============================================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">3</span> EMIN, Tarif & Periode Anomali</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    emin = st.number_input(
        "EMIN — Energi Minimum (kWh/bulan)",
        min_value=0.0,
        value=40.0,
        step=1.0,
        help="Standar EMin biasanya mengacu pada ketentuan jam nyala minimum × daya (kVA) sesuai golongan tarif. Sesuaikan dengan aturan yang berlaku.",
    )
with c2:
    tarif_per_kwh = st.number_input("Tarif per kWh (Rp)", min_value=0.0, value=1352.0, step=1.0)
with c3:
    jumlah_bulan_periode = st.number_input(
        "Jumlah Bulan Periode Anomali", min_value=1, value=1, step=1,
        help="Berapa bulan koreksi ini berlaku, misalnya sejak P2TL terakhir atau sejak indikasi macet/pelanggaran terdeteksi.",
    )

with st.expander("💡 Tabel referensi tarif per kWh (Q2 2026 — cek ulang tarif terbaru di pln.co.id)"):
    tarif_df = pd.DataFrame(TARIF_REFERENSI, columns=["Golongan Tarif", "Tarif (Rp/kWh)"])
    st.dataframe(tarif_df, use_container_width=True, hide_index=True)

# =============================================================================
# HASIL
# =============================================================================

selisih_per_bulan = pemakaian_terhitung - emin
total_selisih_kwh = selisih_per_bulan * jumlah_bulan_periode
total_nominal = total_selisih_kwh * tarif_per_kwh

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### 📊 Hasil Perhitungan")

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(kpi_card("🔎", "Pemakaian Terhitung", f"{pemakaian_terhitung:,.2f} kWh", "per bulan"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("📏", "EMIN", f"{emin:,.2f} kWh", "batas minimum"), unsafe_allow_html=True)
with k3:
    tone = "danger" if selisih_per_bulan >= 0 else "success"
    label = "Kurang Tagih" if selisih_per_bulan >= 0 else "Kelebihan Tagih"
    st.markdown(
        kpi_card("⚖️", "Selisih per Bulan", f"{selisih_per_bulan:,.2f} kWh", label, tone),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

if total_nominal >= 0:
    st.markdown(
        f"""
        <div class="result-banner-tagih">
            <div class="result-label">🔴 TOKEN YANG HARUS DITAGIHKAN KE PELANGGAN</div>
            <div class="result-value">Rp {total_nominal:,.0f}</div>
            <div style="color:#fecaca; font-size:0.9rem; margin-top:6px;">
                Setara {total_selisih_kwh:,.2f} kWh selama {jumlah_bulan_periode} bulan periode anomali
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="result-banner-kembali">
            <div class="result-label">🟢 TOKEN YANG HARUS DIKEMBALIKAN KE PELANGGAN</div>
            <div class="result-value">Rp {abs(total_nominal):,.0f}</div>
            <div style="color:#bbf7d0; font-size:0.9rem; margin-top:6px;">
                Setara {abs(total_selisih_kwh):,.2f} kWh selama {jumlah_bulan_periode} bulan periode anomali
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
rows = [
    ("Metode", metode),
    ("Pemakaian Terhitung (kWh/bulan)", round(pemakaian_terhitung, 2)),
    ("EMIN (kWh/bulan)", round(emin, 2)),
    ("Selisih per Bulan (kWh)", round(selisih_per_bulan, 2)),
    ("Jumlah Bulan Periode Anomali", jumlah_bulan_periode),
    ("Total Selisih (kWh)", round(total_selisih_kwh, 2)),
    ("Tarif per kWh (Rp)", tarif_per_kwh),
    ("Total Nominal (Rp)", round(total_nominal, 0)),
    ("Status", "Tambahan Tagihan" if total_nominal >= 0 else "Pengembalian ke Pelanggan"),
]

excel_bytes = build_excel_summary(rows)
st.download_button(
    "⬇️ UNDUH RINGKASAN PERHITUNGAN (.XLSX)",
    data=excel_bytes,
    file_name="Ringkasan_Koreksi_Token_P2TL.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
