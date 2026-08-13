import streamlit as st
import os
from PIL import Image

# --- KONFIGURASI HALAMAN (WAJIB PALING ATAS) ---
logo_path = "logo_pln.png"
logo_icon = "⚡"
if os.path.exists(logo_path):
    logo_icon = Image.open(logo_path)

st.set_page_config(
    page_title="Kalkulator Konversi Listrik - PLN Platform",
    page_icon=logo_icon,
    layout="wide"
)

# --- GUARD / PROTEKSI HALAMAN (WAJIB LOGIN) ---
from auth import check_login, render_logout_button
check_login()
render_logout_button()
# ----------------------------------------------

# --- KODE MODUL FITUR ---
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1100px; }
    .hero-banner {
        background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
        border-radius: 16px; padding: 24px 28px; color: white; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
    }
    .hero-logo-img { width: 70px; height: auto; border-radius: 8px; background: white; padding: 4px; }
    .hero-badge { background-color: #ffb703; color: #000; font-weight: 800; font-size: 0.75rem; padding: 4px 12px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 6px; }
    .hero-title { font-size: 1.8rem; font-weight: 800; margin: 0; }
    .result-box {
        background-color: #0f172a;
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 24px;
        color: white;
        height: 100%;
    }
    .result-box h4 { margin-top: 0; color: #38bdf8; }
    .result-box p { font-size: 1.05rem; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else '⚡'

st.markdown(f"""
<div class="hero-banner">
    <div>{logo_html}</div>
    <div>
        <span class="hero-badge">MODUL 9</span>
        <div class="hero-title">🔌 Kalkulator Konversi Listrik (V × I → Daya/Energi)</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("Konversi cepat **Tegangan × Arus → Daya (Watt) & Energi (kWh)**, dipakai untuk perhitungan lapangan sehari-hari.")

col_input, col_result = st.columns([1.3, 1])

with col_input:
    fasa = st.radio("Jenis Fasa:", ["1 Fasa", "3 Fasa"], horizontal=True)
    tegangan = st.number_input("Tegangan (V):", min_value=0.0, value=220.0, step=1.0)
    arus = st.number_input("Arus (A):", min_value=0.0, value=5.0, step=0.1)
    cos_phi = st.number_input("Faktor Daya (cos φ):", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
    durasi_jam = st.number_input("Durasi Pemakaian (jam):", min_value=0.0, value=1.0, step=0.5)

if fasa == "1 Fasa":
    daya_watt = tegangan * arus * cos_phi
else:
    daya_watt = 1.732 * tegangan * arus * cos_phi  # √3 untuk sistem 3 fasa

energi_kwh = (daya_watt * durasi_jam) / 1000

with col_result:
    st.markdown(
        f"""
        <div class="result-box">
            <h4>📊 Hasil Konversi</h4>
            <p><b>Daya:</b> {daya_watt:,.2f} Watt ({daya_watt/1000:,.3f} kW)</p>
            <p style="margin-bottom:0;"><b>Energi:</b> {energi_kwh:,.3f} kWh (selama {durasi_jam:g} jam)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
with st.expander("ℹ️ Rumus yang digunakan"):
    st.markdown("""
    - **1 Fasa**: `Daya (W) = V × I × cos φ`
    - **3 Fasa**: `Daya (W) = √3 × V × I × cos φ`
    - **Energi (kWh)** = `Daya (W) × Durasi (jam) ÷ 1000`
    """)