import streamlit as st
import os
import base64
import streamlit as st

# --- GUARD / PROTEKSI HALAMAN (WAJIB LOGIN) ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("🔒 Akses Ditolak! Anda harus login terlebih dahulu di Dashboard Utama.")
    st.info("Silakan buka menu 'app' atau 'Dashboard' di sidebar untuk melakukan login.")
    st.stop()  # SCRIPT DITENTIKAN DI SINI, FITUR DI BAWAHNYA TIDAK AKAN RENDER
# ----------------------------------------------

# --- KODE MODUL FITUR KAMU DI BAWAH INI ---
st.title("📄 Generator Surat & Arsip")
# ... Sisa kode fitur modul kamu
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_path = "logo_pln.png"
logo_base64 = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)

st.set_page_config(
    page_title="Simulasi P2TL - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide"
)
from auth import check_login, render_logout_button
check_login()
render_logout_button()
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 168, 232, 0.2);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .hero-logo-img {
        width: 70px;
        height: auto;
        border-radius: 8px;
        background: white;
        padding: 4px;
    }

    .hero-badge {
        background-color: #ffb703;
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }

    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
    }

    .result-box {
        background-color: #0f172a;
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 24px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else '⚡'

st.markdown(f"""
<div class="hero-banner">
    <div>{logo_html}</div>
    <div>
        <span class="hero-badge">MODUL 2</span>
        <div class="hero-title">🧮 Simulator Hitung Tagihan Susulan (P2TL)</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("Hitung estimasi **Tagihan Susulan (TS)** berdasarkan Jenis Pelanggaran P2TL & Golongan Tarif.")

col1, col2 = st.columns(2)

with col1:
    golongan = st.selectbox("Golongan Tarif Pelanggan:", ["R-1 / TR (900 VA)", "R-1 / TR (1.300 VA)", "R-1 / TR (2.200 VA)", "B-1 / TR (5.500 VA)", "I-2 / TM (>200 kVA)"])
    daya_va = st.number_input("Daya Terpasang (VA):", min_value=450, max_value=1000000, value=1300, step=450)
    jenis_p2tl = st.selectbox("Jenis Pelanggaran P2TL:", [
        "Golongan I (Pempengaruhan Batas Daya / MCB)",
        "Golongan II (Pempengaruhan Pengukuran / KWH Meter)",
        "Golongan III (Pempengaruhan Batas Daya & Pengukuran)",
        "Golongan IV (Pelanggaran Bukan Pelanggan)"
    ])

with col2:
    jam_nyala = st.number_input("Estimasi Jam Nyala per Bulan:", min_value=1, max_value=720, value=400)
    tarif_kwh = st.number_input("Biaya per kWh (Rp):", min_value=500.0, max_value=3000.0, value=1444.70, step=10.0)
    lama_bulan = st.number_input("Lama Pelanggaran (Bulan):", min_value=1, max_value=24, value=6)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🧮 Hitung Estimasi Tagihan Susulan", type="primary", use_container_width=True):
    # Formulas (Simulated)
    kwh_bulan = (daya_va / 1000) * jam_nyala
    biaya_kwh_dasar = kwh_bulan * tarif_kwh
    
    multiplier = 2 if "Golongan I" in jenis_p2tl else (3 if "Golongan II" in jenis_p2tl else 4)
    total_ts = biaya_kwh_dasar * lama_bulan * multiplier
    denda = total_ts * 0.1

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-box">
        <h4>📊 Rincian Simulasi Tagihan Susulan:</h4>
        <hr style="border-color:#334155;">
        <p><b>Estimasi kWh / Bulan:</b> {kwh_bulan:,.2f} kWh</p>
        <p><b>Tagihan Susulan Pemakaian Listrik:</b> Rp {total_ts:,.2f}</p>
        <p><b>Estimasi Denda Tambahan:</b> Rp {denda:,.2f}</p>
        <h3 style="color:#38bdf8; margin-top:10px;">TOTAL ESTIMASI BEBAN P2TL: Rp {total_ts + denda:,.2f}</h3>
    </div>
    """, unsafe_allow_html=True)
