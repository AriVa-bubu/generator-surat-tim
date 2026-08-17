import datetime as dt
import os

import streamlit as st
from PIL import Image

from auth import check_login, render_logout_button
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

# Gerbang login — halaman berhenti di sini jika belum login
check_login()
render_logout_button()

load_custom_css()

HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

K3_TIPS = [
    "Selalu pasang Grounding Local sebelum menyentuh penghantar bertegangan.",
    "Pastikan APD lengkap: Helm K3, Sarung Tangan Isolasi, dan Sepatu Safety sebelum bekerja di lapangan.",
    "Tunda pekerjaan pemeliharaan jaringan terbuka saat hujan lebat atau petir.",
    "Cek kondisi tangga dan alat kerja sebelum naik ke jaringan TM/TR.",
    "Jangan pernah bekerja sendirian pada instalasi bertegangan — selalu gunakan sistem buddy.",
    "Laporkan segera kabel kendor, tiang miring, atau gardu yang terlihat tidak normal.",
    "Pastikan Alat Pelindung Diri (APD) diperiksa rutin, tidak ada yang robek atau rusak.",
    "Gunakan alat uji tegangan sebelum menyatakan jaringan benar-benar padam.",
    "Jaga jarak aman minimal dari jaringan Tegangan Menengah saat menggunakan alat panjang/logam.",
    "Istirahat cukup sebelum shift lapangan — kelelahan adalah penyebab umum kecelakaan kerja.",
]

# =============================================================================
# DATA MODUL (dipakai untuk render & pencarian)
# =============================================================================

MODULES = [
    {
        "no": 1, "file": "pages/1_Generator_Surat.py", "icon": "✉️",
        "title": "Generator Surat & Arsip (ZIP)",
        "desc": "Buat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel.",
    },
    {
        "no": 2, "file": "pages/2_Hitung_P2TL.py", "icon": "🧮",
        "title": "Kalkulator Simulasi P2TL",
        "desc": "Hitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pemakaian.",
    },
    {
        "no": 3, "file": "pages/3_Clean_Data_Excel.py", "icon": "🧹",
        "title": "Validator & Cleaning Data Excel",
        "desc": "Bersihkan data mentah AP2T: Format otomatis mata uang (Rp), IDPEL 12 digit, dan standarisasi.",
    },
    {
        "no": 4, "file": "pages/4_Generator_QR.py", "icon": "📱",
        "title": "Generator QR Code Validasi",
        "desc": "Buat QR Code validasi dokumen/surat tugas secara otomatis yang dapat di-embed atau diunduh.",
    },
    {
        "no": 5, "file": "pages/5_Kalkulator_Tambah_Daya.py", "icon": "⚡",
        "title": "Kalkulator Tambah Daya (PB/NJ)",
        "desc": "Hitung estimasi Biaya Penyambungan (BP), UJL, dan total biaya tambah daya pelanggan.",
    },
    {
        "no": 6, "file": "pages/6_Deteksi_KWH_Macet.py", "icon": "🔎",
        "title": "Deteksi kWh Macet",
        "desc": "Deteksi stand meter yang tidak bergerak dari data DPP dan rekap status per pelanggan.",
    },
    {
        "no": 7, "file": "pages/7_Prediksi_Token_Prabayar.py", "icon": "🔋",
        "title": "Prediksi Sisa Token Prabayar",
        "desc": "Proyeksikan sisa token pelanggan prabayar dan rata-rata pemakaian harian dari riwayat pembelian.",
    },
    {
        "no": 8, "file": "pages/8_Koreksi_Token_P2TL.py", "icon": "⚖️",
        "title": "Koreksi Token P2TL",
        "desc": "Hitung kWh kurang tagih atau kelebihan tagih dan konversinya ke nominal token/Rupiah.",
    },
    {
        "no": 9, "file": "pages/9_Kalkulator_Konversi_Listrik.py", "icon": "🔌",
        "title": "Kalkulator Konversi Listrik",
        "desc": "Konversi cepat Tegangan × Arus menjadi Daya (Watt) dan Energi (kWh) untuk perhitungan lapangan.",
    },
]


def get_greeting(hour: int) -> tuple[str, str]:
    if 4 <= hour < 11:
        return "Selamat Pagi", "☀️"
    if 11 <= hour < 15:
        return "Selamat Siang", "🌤️"
    if 15 <= hour < 18:
        return "Selamat Sore", "🌇"
    return "Selamat Malam", "🌙"


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

            .greeting-card {
                background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
                padding: 20px 22px;
                border-radius: 16px;
                border: 1px solid #2b3a52;
                height: 100%;
            }
            .greeting-emoji { font-size: 1.8rem; margin-bottom: 6px; display: inline-block; }
            .greeting-text { font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin: 2px 0 4px 0; }
            .greeting-date { font-size: 0.9rem; color: #94a3b8; }

            @media (max-width: 640px) {
                .header-title { font-size: 1.5rem !important; }
                .k3-card, .greeting-card { padding: 16px !important; }
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
            <div class="header-status-chip"><span class="dot"></span> SISTEM AKTIF &middot; v2.5.0</div>
            <h1 class="header-title">⚡ Portal Operasional & Layanan Digital PLN</h1>
            <p class="header-subtitle">
                Pusat otomasi kerja harian PLN: Pembuatan Surat Massal, P2TL, Validasi Excel,
                QR Code Generator, Kalkulator Tambah Daya, & Konversi Listrik — semua dalam satu platform.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_info_panel() -> None:
    st.markdown('<div class="section-heading">👋 Info Hari Ini</div>', unsafe_allow_html=True)

    now = dt.datetime.now()
    greeting, emoji = get_greeting(now.hour)
    hari = HARI_ID[now.weekday()]
    bulan = BULAN_ID[now.month - 1]
    tanggal_lengkap = f"{hari}, {now.day} {bulan} {now.year}"
    pekan_ke = now.isocalendar()[1]

    tip = K3_TIPS[dt.date.today().toordinal() % len(K3_TIPS)]

    col_greet, col_tip = st.columns(2)

    with col_greet:
        st.markdown(
            f"""
            <div class="greeting-card">
                <span class="greeting-emoji">{emoji}</span>
                <div class="greeting-text">{greeting}!</div>
                <div class="greeting-date">{tanggal_lengkap} &middot; Pukul {now.strftime('%H:%M')} &middot; Pekan ke-{pekan_ke}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_tip:
        st.markdown(
            f"""
            <div class="k3-card">
                <h4>⚠️ Tips K3 Hari Ini</h4>
                <ul><li>{tip}</li></ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_module_search() -> None:
    st.markdown('<div class="section-heading">🚀 Cari & Pilih Modul Operasional</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-subheading">Ketik kata kunci untuk mencari dari {len(MODULES)} modul yang tersedia, atau klik langsung kartu di bawah.</div>',
        unsafe_allow_html=True,
    )

    keyword = st.text_input(
        "Cari modul:",
        placeholder="🔍 Contoh: surat, P2TL, token, QR...",
        label_visibility="collapsed",
    )

    if keyword.strip():
        kw = keyword.strip().lower()
        filtered = [
            m for m in MODULES
            if kw in m["title"].lower() or kw in m["desc"].lower()
        ]
    else:
        filtered = MODULES

    if not filtered:
        st.warning(f"Tidak ada modul yang cocok dengan kata kunci **'{keyword}'**.")
        return

    col1, col2 = st.columns(2)
    for i, m in enumerate(filtered):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.page_link(
                m["file"],
                label=f"{m['no']}. {m['title']}\n\n{m['desc']}",
                icon=m["icon"],
                use_container_width=True,
            )
            st.write("")


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
                Versi: <code>v2.5.0</code><br>
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


# =============================================================================
# RENDER HALAMAN
# =============================================================================

def main() -> None:
    inject_custom_style()

    render_header()
    render_quick_info_panel()
    st.divider()

    render_module_search()
    st.divider()

    render_info_section()
    st.divider()

    render_quick_links()
    st.divider()

    render_footer()


if __name__ == "__main__":
    main()