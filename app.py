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
    for codes, desc in WEATHER_CODE_MAP.items():
        if code in codes:
            return desc
    return "Kondisi Berawan 🌤️"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_current_weather(lat: float, lon: float) -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&current_weather=true"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()["current_weather"]


# =============================================================================
# STYLING — DESAIN MODERN
# =============================================================================

def inject_custom_style() -> None:
    st.markdown(
        """
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

            /* ---------- HEADER BANNER ---------- */
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .header-banner {
                position: relative;
                overflow: hidden;
                background: linear-gradient(-45deg, #0369a1, #0284c7, #0f172a, #075985);
                background-size: 300% 300%;
                animation: gradientBG 10s ease infinite;
                padding: 32px 36px;
                border-radius: 20px;
                color: white;
                margin-bottom: 24px;
                box-shadow: 0 15px 35px -8px rgba(2, 132, 199, 0.45);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .header-banner::before {
                content: "";
                position: absolute;
                inset: 0;
                background-image: radial-gradient(rgba(255,255,255,0.10) 1px, transparent 1px);
                background-size: 22px 22px;
                opacity: 0.6;
                pointer-events: none;
            }

            .header-status-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(74, 222, 128, 0.15);
                border: 1px solid rgba(74, 222, 128, 0.4);
                color: #4ade80;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 5px 12px;
                border-radius: 999px;
                margin-bottom: 14px;
                position: relative;
                z-index: 1;
            }

            .header-status-chip .dot {
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: #4ade80;
                box-shadow: 0 0 8px #4ade80;
                animation: pulse 1.8s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.35; }
            }

            .header-title {
                margin: 0;
                font-size: 2.2rem;
                font-weight: 800;
                letter-spacing: -0.5px;
                position: relative;
                z-index: 1;
            }

            .header-subtitle {
                margin: 10px 0 0 0;
                color: #e0f2fe;
                font-size: 1.02rem;
                max-width: 720px;
                line-height: 1.5;
                position: relative;
                z-index: 1;
            }

            /* ---------- KPI CARDS ---------- */
            .kpi-card {
                background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
                border: 1px solid #2b3a52;
                border-radius: 16px;
                padding: 18px 20px;
                height: 100%;
                transition: all 0.25s ease;
            }

            .kpi-card:hover {
                border-color: #38bdf8;
                transform: translateY(-3px);
                box-shadow: 0 10px 22px -6px rgba(56, 189, 248, 0.25);
            }

            .kpi-icon {
                font-size: 1.4rem;
                margin-bottom: 8px;
                display: inline-block;
            }

            .kpi-label {
                font-size: 0.78rem;
                color: #94a3b8;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.03em;
            }

            .kpi-value {
                font-size: 1.55rem;
                font-weight: 800;
                color: #f8fafc;
                margin: 4px 0 8px 0;
            }

            .kpi-delta {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-size: 0.75rem;
                font-weight: 700;
                color: #4ade80;
                background: rgba(74, 222, 128, 0.12);
                padding: 3px 9px;
                border-radius: 999px;
            }

            /* ---------- SECTION HEADING ---------- */
            .section-heading {
                font-size: 1.3rem;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 2px;
            }

            .section-subheading {
                font-size: 0.9rem;
                color: #94a3b8;
                margin-bottom: 18px;
            }

            /* ---------- MODULE CARDS (st.page_link) ---------- */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            div[data-testid="stPageLink"] {
                animation: fadeIn 0.5s ease-in-out;
                position: relative;
            }

            div[data-testid="stPageLink"] a {
                background: linear-gradient(160deg, #1e293b 0%, #16202f 100%) !important;
                border: 1px solid #2b3a52 !important;
                border-top: 3px solid #38bdf8 !important;
                border-radius: 14px !important;
                padding: 18px 22px !important;
                min-height: 112px !important;
                display: flex !important;
                align-items: center !important;
                gap: 14px !important;
                transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-decoration: none !important;
                position: relative !important;
            }

            div[data-testid="stPageLink"] a:hover {
                border-color: #38bdf8 !important;
                background: linear-gradient(160deg, #223049 0%, #16202f 100%) !important;
                transform: translateY(-4px) scale(1.015) !important;
                box-shadow: 0 14px 28px -8px rgba(56, 189, 248, 0.35) !important;
            }

            div[data-testid="stPageLink"] a:hover::after {
                content: "Buka →";
                position: absolute;
                bottom: 12px;
                right: 18px;
                font-size: 0.75rem;
                font-weight: 700;
                color: #38bdf8;
                opacity: 1;
            }

            div[data-testid="stPageLink"] a::after {
                content: "";
                opacity: 0;
                transition: opacity 0.25s ease;
            }

            div[data-testid="stPageLink"] a span {
                color: #f1f5f9 !important;
                font-size: 0.95rem !important;
                line-height: 1.45 !important;
            }

            div[data-testid="stPageLink"] a span[data-testid="stIconEmoji"] {
                font-size: 1.9rem !important;
                line-height: 1 !important;
            }

            /* Aksen warna berbeda tiap kartu modul */
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stPageLink"]:nth-of-type(1) a { border-top-color: #38bdf8 !important; }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stPageLink"]:nth-of-type(2) a { border-top-color: #a78bfa !important; }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stPageLink"]:nth-of-type(3) a { border-top-color: #fbbf24 !important; }
            div[data-testid="column"]:nth-of-type(2) div[data-testid="stPageLink"]:nth-of-type(1) a { border-top-color: #4ade80 !important; }
            div[data-testid="column"]:nth-of-type(2) div[data-testid="stPageLink"]:nth-of-type(2) a { border-top-color: #f472b6 !important; }

            /* ---------- INFO / EXPANDER ---------- */
            div[data-testid="stExpander"] {
                border: 1px solid #2b3a52 !important;
                border-radius: 12px !important;
            }

            /* ---------- WEATHER / K3 CARD ---------- */
            .k3-card {
                background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
                padding: 20px 22px;
                border-radius: 16px;
                border: 1px solid #2b3a52;
                height: 100%;
            }

            .k3-card h4 {
                margin-top: 0;
                color: #38bdf8;
                font-size: 1.02rem;
            }

            .k3-card ul {
                color: #cbd5e1;
                font-size: 0.9rem;
                padding-left: 20px;
                margin-bottom: 0;
                line-height: 1.6;
            }

            /* ---------- FOOTER ---------- */
            .footer-heading {
                font-size: 1rem;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 6px;
            }

            .copyright-bar {
                text-align: center;
                color: #64748b;
                font-size: 0.85rem;
                padding: 18px 0 4px 0;
                border-top: 1px solid #1e293b;
                margin-top: 8px;
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
            <div class="header-status-chip"><span class="dot"></span> SISTEM AKTIF &middot; v2.4.0</div>
            <h1 class="header-title">⚡ Portal Operasional & Layanan Digital PLN</h1>
            <p class="header-subtitle">
                Pusat otomasi kerja harian PLN: Pembuatan Surat Massal, P2TL, Validasi Excel,
                QR Code Generator & Kalkulator Tambah Daya — semua dalam satu platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str, delta: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <span class="kpi-delta">↑ {delta}</span>
    </div>
    """


def render_stats_banner() -> None:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(kpi_card("🛠️", "Modul Aktif", "5 Modul", "Siap Pakai"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card("⚡", "Sistem AP2T", "Terhubung", "Online"), unsafe_allow_html=True)
    with m3:
        st.markdown(kpi_card("📄", "Format Dokumen", "DOCX / PDF", "Otomatis"), unsafe_allow_html=True)
    with m4:
        st.markdown(kpi_card("🔒", "Keamanan Validasi", "QR Code", "Encrypted"), unsafe_allow_html=True)


def render_module_cards() -> None:
    st.markdown('<div class="section-heading">🚀 Pilih Modul Operasional</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subheading">Klik salah satu kartu di bawah untuk membuka modul.</div>',
        unsafe_allow_html=True,
    )
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
    st.markdown('<div class="section-heading">🔗 Akses Cepat Portal Resmi & Layanan PLN</div>', unsafe_allow_html=True)
    st.write("")
    col_link1, col_link2, col_link3 = st.columns(3)

    with col_link1:
        st.link_button("🌐 Website Resmi PLN", "https://www.pln.co.id", use_container_width=True)

    with col_link2:
        st.link_button("⚡ Portal Layanan & AP2T", "https://layanan.pln.co.id", use_container_width=True)

    with col_link3:
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
            <div class="footer-heading">⚡ Portal Operasional PLN</div>
            Aplikasi otomasi internal untuk mempercepat alur kerja harian pegawai:
            <ul style="color:#cbd5e1; font-size:0.9rem; padding-left:18px; margin-top:8px;">
                <li>Generator Surat & Mail Merge (.DOCX / .PDF)</li>
                <li>Kalkulator Simulasi P2TL & Tambah Daya</li>
                <li>Validasi & Cleaning Data AP2T Excel</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

    with footer_col2:
        st.markdown(
            """
            <div class="footer-heading">📞 Helpdesk & Support IT</div>
            Mengalami kendala sistem atau butuh penyesuaian template?
            <ul style="color:#cbd5e1; font-size:0.9rem; padding-left:18px; margin-top:8px;">
                <li><b>Email Support</b>: <code>24030214005@mhs.unesa.ac.id</code></li>
                <li><b>Group Telegram</b>: Tim Operasional & IT PLN</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "💬 Chat Admin IT via WhatsApp",
            "https://wa.me/6281933041691",
            use_container_width=True,
        )

    with footer_col3:
        st.markdown(
            """
            <div class="footer-heading">ℹ️ Info Sistem</div>
            <span style="color:#cbd5e1; font-size:0.9rem;">
                Versi: <code>v2.4.0</code><br>
                Status: 🟢 Normal<br>
                Environment: Production
            </span>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="copyright-bar">
            © 2026 <b>PT PLN (Persero)</b> — Tim Operasional & Layanan Digital. All Rights Reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_weather_widget() -> None:
    st.markdown('<div class="section-heading">🌤️ Informasi Cuaca & Kesiapsiagaan Lapangan</div>', unsafe_allow_html=True)
    st.write("")
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
                st.markdown(kpi_card("🌡️", "Suhu Udara", f"{temp} °C", cuaca_desc.split(" ")[-1]), unsafe_allow_html=True)
            with w_col2:
                st.markdown(kpi_card("💨", "Kecepatan Angin", f"{wind} km/h", "Live"), unsafe_allow_html=True)
            st.caption(f"Status saat ini: **{cuaca_desc}**")

        except requests.RequestException:
            st.warning("Gagal memuat data cuaca real-time. Pastikan server terhubung ke internet.")

    with col_status:
        st.markdown(
            """
            <div class="k3-card">
                <h4>⚠️ Himbauan Keselamatan Kerja (K3)</h4>
                <ul>
                    <li><b>Hujan Lebat / Petir:</b> Tunda pekerjaan pemeliharaan pada jaringan Tegangan Menengah (TM) & TR terbuka.</li>
                    <li><b>APD Lengkap:</b> Pastikan penggunaan Helm K3, Sarung Tangan Isolasi, dan Sepatu Safety.</li>
                    <li><b>Gunakan SOP Grounding:</b> Selalu pasang <i>Grounding Local</i> sebelum menyentuh penghantar.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_activity_trend() -> None:
    st.markdown('<div class="section-heading">📈 Tren Aktivitas & Pemantauan Operasional</div>', unsafe_allow_html=True)
    st.caption(
        "⚠️ Data di bawah ini masih **contoh/simulasi** — belum terhubung ke log penggunaan modul yang sebenarnya."
    )

    # TODO: ganti dengan data log penggunaan modul yang sebenarnya
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