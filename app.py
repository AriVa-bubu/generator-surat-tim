import os

import numpy as np
import pandas as pd
import requests
import streamlit as st
from PIL import Image

from utils import load_custom_css

# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================
import streamlit as st
import hashlib

# 1. Konfigurasi Halaman (Harus di baris paling atas Streamlit)
st.set_page_config(
    page_title="PLN Multi-Tools Operational",
    page_icon="⚡",
    layout="wide"
)

# 2. Database User Sederhana (Username : Password Hashing)
# Untuk keamanan, password di-hash menggunakan SHA-256
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Contoh Hash Password:
# "admin123" -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
# "pln2026"  -> a6c3c52e4604d5ff186632fa5f05b1c93a02bb80e92fae3f16d1f0579e49a896
USER_DB = {
    "admin": {"password_hash": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9", "nama": "Admin IT PLN", "role": "Administrator"},
    "petugas": {"password_hash": "a6c3c52e4604d5ff186632fa5f05b1c93a02bb80e92fae3f16d1f0579e49a896", "nama": "Budi Santoso (P2TL)", "role": "Petugas Lapangan"}
}

# 3. Inisialisasi Session State Login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["user_info"] = {}

# 4. Fungsi Tampilan Form Login
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>⚡ Portal Operasional PLN</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Silakan login menggunakan akun dinas Anda</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if submit_btn:
                if username_input in USER_DB:
                    hashed_pwd = make_hash(password_input)
                    if hashed_pwd == USER_DB[username_input]["password_hash"]:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username_input
                        st.session_state["user_info"] = USER_DB[username_input]
                        st.success(f"Selamat datang, {USER_DB[username_input]['nama']}!")
                        st.rerun()  # Refresh halaman otomatis
                    else:
                        st.error("Password salah!")
                else:
                    st.error("Username tidak ditemukan!")

# 5. Logika Akses Halaman
if not st.session_state["logged_in"]:
    show_login_page()
else:
    # --- JIKA SUDAH LOGIN, TAMPILKAN DASHBOARD UTAMA ---
    
    # Widget User di Sidebar + Tombol Logout
    with st.sidebar:
        st.write(f"👤 **{st.session_state['user_info']['nama']}**")
        st.caption(f"Role: {st.session_state['user_info']['role']}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["user_info"] = {}
            st.rerun()
        st.divider()

    # --- SELURUH KODE DASHBOARD KAMU YANG LAMA DIPASANG DI SINI ---
    st.title("🚀 Dashboard Utama Portal PLN")
    st.write(f"Halo **{st.session_state['user_info']['nama']}**, pilih modul di bawah untuk mulai bekerja.")
    
    # ... (Sisa kode kartu modul, widget cuaca, footer, dll.)
logo_icon = "⚡"
if os.path.exists("logo_pln.png"):
    logo_icon = Image.open("logo_pln.png")

st.set_page_config(
    page_title="PLN - Portal Operasional Digital",
    page_icon=logo_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_custom_css()

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

WEATHER_CODE_MAP = {
    (0, 1): "Cerah / Berawan Tipis ☀️",
    (2, 3): "Berawan / Mendung ⛅",
    (51, 53, 55, 61, 63, 65): "Hujan Ringan / Sedang 🌧️",
    (80, 81, 82, 95, 96, 99): "Hujan Lebat / Disertai Petir ⛈️",
}


def describe_weather_code(code: int) -> str:
    """Terjemahkan kode cuaca Open-Meteo jadi deskripsi Bahasa Indonesia."""
    for codes, desc in WEATHER_CODE_MAP.items():
        if code in codes:
            return desc
    return "Kondisi Berawan 🌤️"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_current_weather(lat: float, lon: float) -> dict:
    """Ambil cuaca terkini dari Open-Meteo. Di-cache 10 menit agar hemat request."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()["current_weather"]


# =============================================================================
# STYLING KHUSUS (CARD & LAYOUT)
# =============================================================================

def inject_custom_style() -> None:
    st.markdown(
        """
        <style>
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

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            div[data-testid="stPageLink"] {
                animation: fadeIn 0.6s ease-in-out;
            }

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
                transform: translateY(-5px) scale(1.02) !important;
                box-shadow: 0 12px 25px -5px rgba(56, 189, 248, 0.4) !important;
            }

            div[data-testid="stPageLink"] a span {
                color: #f1f5f9 !important;
                font-size: 0.95rem !important;
                line-height: 1.4 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# BAGIAN-BAGIAN HALAMAN
# =============================================================================

def render_header() -> None:
    st.markdown(
        """
        <div class="header-banner">
            <h1 style="margin: 0; font-size: 2rem; color: white;">⚡ Portal Operasional & Layanan Digital PLN</h1>
            <p style="margin: 8px 0 0 0; color: #e0f2fe; font-size: 1rem;">
                Pusat otomasi kerja harian PLN: Pembuatan Surat Massal, P2TL, Validasi Excel,
                QR Code Generator & Kalkulator Tambah Daya.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_banner() -> None:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="🛠️ Modul Aktif", value="5 Modul", delta="Siap Pakai")
    with m2:
        st.metric(label="⚡ Sistem AP2T", value="Terhubung", delta="Online")
    with m3:
        st.metric(label="📄 Format Dokumen", value="DOCX / PDF", delta="Otomatis")
    with m4:
        st.metric(label="🔒 Keamanan Validasi", value="QR Code", delta="Encrypted")


def render_module_cards() -> None:
    st.subheader("🚀 Pilih Modul Operasional")
    col1, col2 = st.columns(2)

    with col1:
        st.page_link(
            "pages/1_Generator_Surat.py",
            label=(
                "1. Generator Surat & Arsip (ZIP)\n\n"
                "Buat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel."
            ),
            icon="✉️",
            use_container_width=True,
        )
        st.write("")
        st.page_link(
            "pages/2_Hitung_P2TL.py",
            label=(
                "2. Kalkulator Simulasi P2TL\n\n"
                "Hitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pemakaian."
            ),
            icon="🧮",
            use_container_width=True,
        )
        st.write("")
        st.page_link(
            "pages/5_Kalkulator_Tambah_Daya.py",
            label=(
                "5. Kalkulator Tambah Daya (PB/NJ)\n\n"
                "Hitung estimasi Biaya Penyambungan (BP), UJL, dan total biaya tambah daya pelanggan."
            ),
            icon="⚡",
            use_container_width=True,
        )

    with col2:
        st.page_link(
            "pages/3_Clean_Data_Excel.py",
            label=(
                "3. Validator & Cleaning Data Excel\n\n"
                "Bersihkan data mentah AP2T: Format otomatis mata uang (Rp), IDPEL 12 digit, dan standarisasi."
            ),
            icon="🧹",
            use_container_width=True,
        )
        st.write("")
        st.page_link(
            "pages/4_Generator_QR.py",
            label=(
                "4. Generator QR Code Validasi\n\n"
                "Buat QR Code validasi dokumen/surat tugas secara otomatis yang dapat di-embed atau diunduh."
            ),
            icon="📱",
            use_container_width=True,
        )


def render_info_section() -> None:
    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.info(
            """
            ### 📢 Catatan & Panduan Penggunaan
            * **Data Keamanan**: Seluruh proses pengolahan file Excel dan Dokumen dilakukan
              secara *in-memory* tanpa menyimpan data di server public.
            * **Format Template**: Gunakan format variabel `{NAMA}`, `{IDPEL}`, `{ALAMAT}`
              untuk *mail merge* di modul Generator Surat.
            """
        )

    with col_info2:
        with st.expander("❓ Butuh Bantuan / Kendala Sistem?"):
            st.write(
                """
                Jika menemukan error saat mengunggah data Excel atau mengunduh hasil ZIP:
                1. Pastikan ekstensi file adalah `.xlsx` atau `.csv`.
                2. Pastikan tidak ada karakter aneh di judul kolom Excel.
                3. Hubungi Admin Operasional IT unit terdekat.
                """
            )


def render_quick_links() -> None:
    st.subheader("🔗 Akses Cepat Portal Resmi & Layanan PLN")
    col_link1, col_link2, col_link3 = st.columns(3)

    with col_link1:
        st.link_button(
            "🌐 Website Resmi PLN",
            "https://www.pln.co.id",
            use_container_width=True,
        )

    with col_link2:
        st.link_button(
            "⚡ Portal Layanan & AP2T",
            "https://layanan.pln.co.id",
            use_container_width=True,
        )

    with col_link3:
        # Link Play Store resmi PLN Mobile (berbeda dari Portal AP2T di atas)
        st.link_button(
            "📱 Unduh PLN Mobile",
            "https://play.google.com/store/apps/details?id=com.icon.pln123",
            use_container_width=True,
        )


def render_footer() -> None:
    footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 1])

    with footer_col1:
        st.markdown(
            """
            #### ⚡ Portal Operasional PLN
            Aplikasi otomasi internal untuk mempercepat alur kerja harian pegawai:
            * Generator Surat & Mail Merge (.DOCX / .PDF)
            * Kalkulator Simulasi P2TL & Tambah Daya
            * Validasi & Cleaning Data AP2T Excel
            """
        )

    with footer_col2:
        st.markdown(
            """
            #### 📞 Helpdesk & Support IT
            Mengalami kendala sistem atau butuh penyesuaian template?
            * **Email Support**: `24030214005@mhs.unesa.ac.id`
            * **Group Telegram**: Tim Operasional & IT PLN
            """
        )
        st.link_button(
            "💬 Chat Admin IT via WhatsApp",
            "https://wa.me/6281933041691",
            use_container_width=True,
        )

    with footer_col3:
        st.markdown(
            """
            #### ℹ️ Info Sistem
            * **Versi**: `v2.4.0`
            * **Status**: 🟢 Normal
            * **Environment**: Production
            """
        )

    st.markdown(
        """
        <br>
        <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 15px 0; border-top: 1px solid #1e293b;">
            © 2026 <b>PT PLN (Persero)</b> — Tim Operasional & Layanan Digital. All Rights Reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_weather_widget() -> None:
    st.subheader("🌤️ Informasi Cuaca & Kesiapsiagaan Lapangan")
    col_weather, col_status = st.columns(2)

    with col_weather:
        kota_pilihan = st.selectbox(
            "📍 Pilih Wilayah Operasional / ULP:",
            list(DAFTAR_LOKASI.keys()),
            index=0,
        )
        lokasi = DAFTAR_LOKASI[kota_pilihan]

        try:
            current = fetch_current_weather(lokasi["lat"], lokasi["lon"])
            temp = current["temperature"]
            wind = current["windspeed"]
            cuaca_desc = describe_weather_code(current["weathercode"])

            w_col1, w_col2 = st.columns(2)
            with w_col1:
                st.metric(label="🌡️ Suhu Udara", value=f"{temp} °C")
                st.caption(f"Status: **{cuaca_desc}**")
            with w_col2:
                st.metric(label="💨 Kecepatan Angin", value=f"{wind} km/h")

        except requests.RequestException:
            st.warning("Gagal memuat data cuaca real-time. Pastikan server terhubung ke internet.")

    with col_status:
        st.markdown(
            """
            <div style="background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 100%;">
                <h4 style="margin-top:0; color: #38bdf8;">⚠️ Himbauan Keselamatan Kerja (K3)</h4>
                <ul style="color: #cbd5e1; font-size: 0.9rem; padding-left: 20px; margin-bottom: 0;">
                    <li><b>Hujan Lebat / Petir:</b> Tunda pekerjaan pemeliharaan pada jaringan Tegangan Menengah (TM) & TR terbuka.</li>
                    <li><b>APD Lengkap:</b> Pastikan penggunaan Helm K3, Sarung Tangan Isolasi, dan Sepatu Safety.</li>
                    <li><b>Gunakan SOP Grounding:</b> Selalu pasang <i>Grounding Local</i> sebelum menyentuh penghantar.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_activity_trend() -> None:
    st.subheader("📈 Tren Aktivitas & Pemantauan Operasional")
    st.caption(
        "⚠️ Data di bawah ini masih **contoh/simulasi** — belum terhubung ke log penggunaan modul yang sebenarnya."
    )

    # TODO: ganti dengan data log penggunaan modul yang sebenarnya
    # (misalnya dari file/DB yang mencatat setiap kali modul dipakai)
    chart_data = pd.DataFrame(
        np.random.randn(20, 3) + [10, 15, 20],
        columns=["Validasi P2TL", "Clean Data AP2T", "Generator Surat"],
    )
    st.line_chart(chart_data)


# =============================================================================
# RENDER HALAMAN
# =============================================================================

def main() -> None:
    inject_custom_style()

    render_header()
    render_stats_banner()
    st.divider()

    render_module_cards()
    st.divider()

    render_info_section()
    st.divider()

    render_quick_links()
    st.divider()

    render_footer()
    st.divider()

    render_weather_widget()
    st.divider()

    render_activity_trend()


if __name__ == "__main__":
    main()