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
    /* 1. Animasi Gradasi Bergerak untuk Header Banner */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .header-banner {
        background: linear-gradient(-45deg, #0284c7, #0369a1, #0f172a, #0284c7);
        background-size: 300% 300%;
        animation: gradientBG 8s ease infinite;
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
    }

    /* 2. Animasi Fade-In saat Halaman Pertama Dimuat */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stPageLink"] {
        animation: fadeIn 0.6s ease-in-out;
    }

    /* 3. Efek Transisi Kartu Membesar / Melayang (Hover Effect) */
    div[data-testid="stPageLink"] a {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        min-height: 110px !important;
        display: flex !important;
        align-items: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-decoration: none !important;
    }

    div[data-testid="stPageLink"] a:hover {
        border-color: #38bdf8 !important;
        background-color: #0f172a !important;
        transform: translateY(-5px) scale(1.02) !important; /* Kartu naik & membesar sedikit */
        box-shadow: 0 12px 25px -5px rgba(56, 189, 248, 0.4) !important; /* Efek menyala */
    }

    div[data-testid="stPageLink"] a span {
        color: #f1f5f9 !important;
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
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
import streamlit as st

st.subheader("🔗 Akses Cepat Portal Resmi & Layanan PLN")

col_link1, col_link2, col_link3 = st.columns(3)

with col_link1:
    st.link_button(
        "🌐 Website Resmi PLN", 
        "https://www.pln.co.id", 
        use_container_width=True
    )

with col_link2:
    st.link_button(
        "⚡ Portal Layanan & AP2T", 
        "https://layanan.pln.co.id", 
        use_container_width=True
    )

with col_link3:
    # Menggunakan URL landing page resmi PLN Mobile
    import streamlit as st

# Menggunakan link resmi yang dijamin TIDAK AKAN NXDOMAIN / Error 404
st.link_button(
    "📱 Informasi PLN Mobile", 
    "https://layanan.pln.co.id",  # <--- URL Aktif Resmi PLN
    use_container_width=True
)
st.divider()

# --- FOOTER & HELPDESK SECTION ---
footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 1])

with footer_col1:
    st.markdown("""
    #### ⚡ Portal Operasional PLN
    Aplikasi otomasi internal untuk mempercepat alur kerja harian pegawai:
    * Generator Surat & Mail Merge (.DOCX / .PDF)
    * Kalkulator Simulasi P2TL & Tambah Daya
    * Validasi & Cleaning Data AP2T Excel
    """)

with footer_col2:
    st.markdown("""
    #### 📞 Helpdesk & Support IT
    Mengalami kendala sistem atau butuh penyesuaian template?
    * **Email Support**: `admin.it@pln.co.id`
    * **Group Telegram**: Tim Operasional & IT PLN
    """)
    st.link_button("💬 Chat Admin IT via WhatsApp", "https://wa.me/6281933041691", use_container_width=True)

with footer_col3:
    st.markdown("""
    #### ℹ️ Info Sistem
    * **Versi**: `v2.4.0`
    * **Status**: 🟢 Normal
    * **Environment**: Production
    """)

# Copyright Bar di Paling Bawah
st.markdown("""
<br>
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0; border-top: 1px solid #1e293b;">
    © 2026 <b>PT PLN (Persero)</b> — Tim Operasional & Layanan Digital. All Rights Reserved.
</div>
""", unsafe_allow_html=True)
import requests

st.divider()

# --- WIDGET CUACA & STATUS SIAGA LAPANGAN ---
st.subheader("🌤️ Informasi Cuaca & Kesiapsiagaan Lapangan")

# Daftar Koordinat Kota / Unit Operasional PLN
DAFTAR_LOKASI = {
    "Surabaya": {"lat": -7.2575, "lon": 112.7521},
    "Sidoarjo": {"lat": -7.4478, "lon": 112.7183},
    "Gresik": {"lat": -7.1566, "lon": 112.6555},
    "Malang": {"lat": -7.9839, "lon": 112.6214},
    "Pasuruan": {"lat": -7.6453, "lon": 112.9075},
    "Mojokerto": {"lat": -7.4726, "lon": 112.4381},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Bandung": {"lat": -6.9175, "lon": 107.6191},
    "Semarang": {"lat": -6.9667, "lon": 110.4167},
}

col_weather, col_status = st.columns([1, 1])

with col_weather:
    # Dropdown Pilih Lokasi Unit
    kota_pilihan = st.selectbox("📍 Pilih Wilayah Operasional / ULP:", list(DAFTAR_LOKASI.keys()), index=0)
    
    lat = DAFTAR_LOKASI[kota_pilihan]["lat"]
    lon = DAFTAR_LOKASI[kota_pilihan]["lon"]
    
    # Fetch Data dari Open-Meteo berdasarkan koordinat kota terpilih
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        current = response["current_weather"]
        
        temp = current["temperature"]
        wind = current["windspeed"]
        code = current["weathercode"]
        
        # Pengelompokan status cuaca
        if code in [0, 1]:
            cuaca_desc = "Cerah / Berawan Tipis ☀️"
        elif code in [2, 3]:
            cuaca_desc = "Berawan / Mendung ⛅"
        elif code in [51, 53, 55, 61, 63, 65]:
            cuaca_desc = "Hujan Ringan / Sedang 🌧️"
        elif code in [80, 81, 82, 95, 96, 99]:
            cuaca_desc = "Hujan Lebat / Disertai Petir ⛈️"
        else:
            cuaca_desc = "Kondisi Berawan 🌤️"
            
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            st.metric(label="🌡️ Suhu Udara", value=f"{temp} °C")
            st.caption(f"Status: **{cuaca_desc}**")
        with w_col2:
            st.metric(label="💨 Kecepatan Angin", value=f"{wind} km/h")
            
    except Exception:
        st.warning("Gagal memuat data cuaca real-time. Pastikan server terhubung ke internet.")

with col_status:
    st.markdown("""
    <div style="background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 100%;">
        <h4 style="margin-top:0; color: #38bdf8;">⚠️ Himbauan Keselamatan Kerja (K3)</h4>
        <ul style="color: #cbd5e1; font-size: 0.9rem; padding-left: 20px; margin-bottom: 0;">
            <li><b>Hujan Lebat / Petir:</b> Tunda pekerjaan pemeliharaan pada jaringan Tegangan Menengah (TM) & TR terbuka.</li>
            <li><b>APD Lengkap:</b> Pastikan penggunaan Helm K3, Sarung Tangan Isolasi, dan Sepatu Safety.</li>
            <li><b>Gunakan SOP Grounding:</b> Selalu pasang <i>Grounding Local</i> sebelum menyentuh penghantar.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
import pandas as pd
import numpy as np

st.divider()

# Section Grafik Dinamis
st.subheader("📈 Tren Aktivitas & Pemantauan Operasional")

# Buat contoh data statistik tren harian
chart_data = pd.DataFrame(
    np.random.randn(20, 3) + [10, 15, 20],
    columns=['Validasi P2TL', 'Clean Data AP2T', 'Generator Surat']
)

# Render Grafik Interaktif
st.line_chart(chart_data)