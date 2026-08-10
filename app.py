import streamlit as st
import os
from PIL import Image
from utils import load_custom_css

# Load logo untuk Tab Browser (Favicon)
logo_icon = "⚡"
if os.path.exists("logo_pln.png"):
    logo_icon = Image.open("logo_pln.png")

st.set_page_config(
    page_title="PLN - Portal Operasional Digital",
    page_icon=logo_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Custom
load_custom_css()

# Header Portal
st.markdown("""
<div style="background-color: #0e4b75; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
    <h2 style="color: white; margin: 0;">⚡ Portal Operasional & Layanan Digital PLN</h2>
    <p style="color: #e0e0e0; margin: 5px 0 0 0;">Pusat alat bantu otomatisasi kerja harian PLN: Generator Surat, P2TL, Clean Data, QR Code & Kalkulator.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("🛠️ Pilih Modul Operasional (Klik Kartu / Gunakan Sidebar):")

# CSS khusus agar tombol page_link berukuran besar mirip kartu
st.markdown("""
<style>
div[data-testid="stPageLink-direct"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 15px;
    transition: all 0.3s ease;
}
div[data-testid="stPageLink-direct"]:hover {
    border-color: #38bdf8;
    background-color: #0f172a;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# Grid Kolom
col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/1_✉️_Generator_Surat.py", 
        label="1. Generator Surat & Arsip (ZIP)\n\nBuat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel.", 
        icon="✉️",
        use_container_width=True
    )
    
    st.write("")

    st.page_link(
        "pages/2_🧮_Hitung_P2TL.py", 
        label="2. Kalkulator Simulasi P2TL\n\nHitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pemakaian.", 
        icon="🧮",
        use_container_width=True
    )

    st.write("")

    st.page_link(
        "pages/5_⚡_Kalkulator_Tambah_Daya.py", 
        label="5. Kalkulator Tambah Daya (PB/NJ)\n\nHitung estimasi Biaya Penyambungan (BP), UJL, dan total biaya tambah daya pelanggan.", 
        icon="⚡",
        use_container_width=True
    )

with col2:
    st.page_link(
        "pages/3_🧹_Clean_Data_Excel.py", 
        label="3. Validator & Cleaning Data Excel\n\nBersihkan data mentah AP2T: Format otomatis mata uang (Rp), IDPEL 12 digit, dan standarisasi.", 
        icon="🧹",
        use_container_width=True
    )
    
    st.write("")

    st.page_link(
        "pages/4_📱_Generator_QR.py", 
        label="4. Generator QR Code Validasi\n\nBuat QR Code validasi dokumen/surat tugas secara otomatis yang dapat di-embed atau diunduh.", 
        icon="📱",
        use_container_width=True
    )