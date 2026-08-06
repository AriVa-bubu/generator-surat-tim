import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_path = "logo_pln.png"
logo_base64 = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)

st.set_page_config(
   st.set_page_config(
    page_title="PLN - Portal Operasional Digital",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
        border-radius: 16px;
        padding: 32px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(0, 168, 232, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 24px;
    }
    
    .hero-logo-img {
        width: 85px;
        height: auto;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        background: white;
        padding: 4px;
    }

    .hero-content {
        flex-grow: 1;
    }

    .hero-badge {
        background-color: #ffb703;
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: inline-block;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #e0f2fe;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    .feature-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    .feature-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else '⚡'

st.markdown(f"""
<div class="hero-banner">
    <div>
        {logo_html}
    </div>
    <div class="hero-content">
        <span class="hero-badge">⚡ PLN MULTI-TOOLS PLATFORM</span>
        <div class="hero-title">
            Portal Operasional & Layanan Digital
        </div>
        <p class="hero-subtitle">
            Pusat alat bantu otomatisasi kerja harian PLN: Pembuatan Surat Massal, P2TL, Validasi Excel & QR Code Generator.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🛠️ Pilih Modul Operasional (Gunakan Menu Sidebar Kiri):")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✉️</div>
        <div class="feature-title">1. Generator Surat & Arsip (ZIP)</div>
        <div class="feature-desc">
            Buat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel. Otomatis terkelompokkan ke dalam sub-folder berdasarkan TANGGAL atau ULP.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧮</div>
        <div class="feature-title">2. Kalkulator Simulasi P2TL</div>
        <div class="feature-desc">
            Hitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pemakaian kVARh/kWh dengan akurasi formula standar PLN.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧹</div>
        <div class="feature-title">3. Validator & Cleaning Data Excel</div>
        <div class="feature-desc">
            Bersihkan data mentah AP2T: Format otomatis mata uang (Rp), pengecekan 12 digit IDPEL, dan standarisasi penulisan nama/alamat.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔳</div>
        <div class="feature-title">4. Generator QR Code Validasi</div>
        <div class="feature-desc">
            Buat QR Code validasi dokumen/surat tugas secara otomatis yang dapat di-embed atau diunduh langsung untuk kebutuhan verifikasi verifikator/pelanggan.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.success("👈 Pilih salah satu menu di atas untuk mulai!")
import streamlit as st

st.set_page_config(page_title="PLN Multi Tools", page_icon="⚡", layout="wide")

# Sembunyikan item pertama (yaitu 'app') dari list navigasi sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] li:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)