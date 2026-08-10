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

# Styling Khusus untuk Card & Layout
st.markdown("""
<style>
    /* Styling Banner Header */
    .header-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Styling Tombol Page Link Agar Berbentuk Kartu Mewah */
    div[data-testid="stPageLink-direct"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        min-height: 120px !important;
        transition: all 0.3s ease-in-out !important;
    }
    div[data-testid="stPageLink-direct"]:hover {
        border-color: #38bdf8 !important;
        background-color: #0f172a !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. HEADER BANNER
st.markdown("""
<div class="header-banner">
    <h1 style="margin: 0; font-size: 2rem; color: white;">⚡ Portal Operasional & Layanan Digital PLN</h1>
    <p style="margin: 8px 0 0 0; color: #e0f2fe; font-size: 1rem;">
        Pusat otomasi kerja harian PLN: Pembuatan Surat Massal, P2TL, Validasi Excel, QR Code Generator & Kalkulator Tambah Daya.
    </p>
</div>
""", unsafe_allow_html=True)

# 2. STATS / METRICS BANNER (Bikin Halaman Rame & Profesional)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="🛠️ Modul Aktif", value="5 Modul", delta="Siap Pakai")
with m2:
    st.metric(label="⚡ Sistem AP2T", value="Terhubung", delta="Online")
with m3:
    st.metric(label="📄 Format Dokumen", value="DOCX / PDF", delta="Otomatis")
with m4:
    st.metric(label="🔒 Keamanan Validasi", value="QR Code", delta="Encrypted")

st.divider()

# 3. KARTU MODUL OPERASIONAL
st.subheader("🚀 Pilih Modul Operasional")

col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/1_Generator_Surat.py", 
        label="1. Generator Surat & Arsip (ZIP)\n\nBuat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel.", 
        icon="✉️",
        use_container_width=True
    )
    
    st.write("")

    st.page_link(
        "pages/2_Hitung_P2TL.py", 
        label="2. Kalkulator Simulasi P2TL\n\nHitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pemakaian.", 
        icon="🧮",
        use_container_width=True
    )

    st.write("")

    st.page_link(
        "pages/5_Kalkulator_Tambah_Daya.py", 
        label="5. Kalkulator Tambah Daya (PB/NJ)\n\nHitung estimasi Biaya Penyambungan (BP), UJL, dan total biaya tambah daya pelanggan.", 
        icon="⚡",
        use_container_width=True
    )

with col2:
    st.page_link(
        "pages/3_Clean_Data_Excel.py", 
        label="3. Validator & Cleaning Data Excel\n\nBersihkan data mentah AP2T: Format otomatis mata uang (Rp), IDPEL 12 digit, dan standarisasi.", 
        icon="🧹",
        use_container_width=True
    )
    
    st.write("")

    st.page_link(
        "pages/4_Generator_QR.py", 
        label="4. Generator QR Code Validasi\n\nBuat QR Code validasi dokumen/surat tugas secara otomatis yang dapat di-embed atau diunduh.", 
        icon="📱",
        use_container_width=True
    )

st.divider()

# 4. PENGUMUMAN & FAQ (Pelengkap Tampilan Bawah)
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.info("""
    ### 📢 Catatan & Panduan Penggunaan
    * **Data Keamanan**: Seluruh proses pengolahan file Excel dan Dokumen dilakukan secara *in-memory* tanpa menyimpan data di server public.
    * **Format Template**: Gunakan format variabel `{NAMA}`, `{IDPEL}`, `{ALAMAT}` untuk *mail merge* di modul Generator Surat.
    """)

with col_info2:
    with st.expander("❓ Butuh Bantuan / Kendala Sistem?"):
        st.write("""
        Jika menemukan error saat mengunggah data Excel atau mengunduh hasil ZIP:
        1. Pastikan ekstensi file adalah `.xlsx` atau `.csv`.
        2. Pastikan tidak ada karakter aneh di judul kolom Excel.
        3. Hubungi Admin Operasional IT unit terdekat.
        """)
st.divider()

# 5. LINK AKSES CEPAT LAYANAN RESMI PLN
st.subheader("🔗 Akses Cepat Portal Resmi PLN")

link_col1, link_col2, link_col3 = st.columns(3)

with link_col1:
    st.link_button(
        label="🌐 Website Resmi PLN", 
        url="https://www.pln.co.id", 
        use_container_width=True
    )

with link_col2:
    st.link_button(
        label="⚡ Web AP2T / Portal Layanan", 
        url="https://layanan.pln.co.id",  # Bisa diganti URL portal internal AP2T unit kamu
        use_container_width=True
    )

with link_col3:
    st.link_button(
        label="📱 Informasi PLN Mobile", 
        url="https://web.pln.co.id/pelanggan/layanan-online", 
        use_container_width=True
    )
st.divider()

# --- WIDGET CUACA & STATUS SIAGA LAPANGAN ---
st.subheader("🌤️ Informasi Cuaca & Kesiapsiagaan Lapangan")

col_weather, col_status = st.columns([1, 1])

with col_weather:
    # Embedded Weather Widget (Otomatis menyesuaikan area / Surabaya & sekitarnya)
    st.markdown("""
    <div style="background: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; text-align: center;">
        <iframe src="https://i.w3schools.com/tags/showiframe.asp?filename=tryhtml_iframe" style="display:none"></iframe>
        <a class="weatherwidget-io" href="https://forecast7.com/id/neg7d25112d75/surabaya/" data-label_1="KONDISI CUACA" data-label_2="OPERASIONAL PLN" data-theme="dark" data-basecolor="#1e293b" data-accent="#0284c7" data-textcolor="#ffffff">KONDISI CUACA OPERASIONAL PLN</a>
        <script>
        !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');
        </script>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    st.markdown("""
    <div style="background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 100%;">
        <h4 style="margin-top:0; color: #38bdf8;">⚠️ Himbauan Keselamatan Kerja (K3)</h4>
        <ul style="color: #cbd5e1; font-size: 0.95rem; padding-left: 20px; margin-bottom: 0;">
            <li><b>Hujan Lebat / Petir:</b> Tunda pekerjaan pemeliharaan pada jaringan Tegangan Menengah (TM) & Tegangan Rendah (TR) terbuka.</li>
            <li><b>APD Lengkap:</b> Pastikan penggunaan Helm K3, Sarung Tangan Isolasi (Insulated Gloves), dan Sepatu Safety sebelum naik pekarangan/tiang.</li>
            <li><b>Gunakan SOP Grounding:</b> Selalu pasang <i>Grounding Local</i> sebelum menyentuh penghantar yang dipadamkan.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)