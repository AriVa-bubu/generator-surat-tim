import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfigurasi Halaman (Wajib di paling atas)
st.set_page_config(
    page_title="PLN Multi-Tools Operational",
    page_icon="⚡",
    layout="wide"
)

# 2. CSS Custom untuk Styling & Animasi Modern
st.markdown("""
<style>
    /* Animasi Gradasi Bergerak Header */
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

    /* Animasi Fade-In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stPageLink"] {
        animation: fadeIn 0.6s ease-in-out;
    }

    /* Styling & Hover Effect Kartu Modul */
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
""", unsafe_allow_html=True)

# 3. Database User Sederhana
USER_DB = {
    "admin": {
        "password": "admin123", 
        "nama": "Admin IT PLN", 
        "role": "Administrator"
    },
    "petugas": {
        "password": "pln2026", 
        "nama": "Budi Santoso (P2TL)", 
        "role": "Petugas Lapangan"
    }
}

# 4. Inisialisasi Session State Login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["user_info"] = {}

# 5. Fungsi Tampilan Form Login
def show_login_page():
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center;">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">⚡ Portal Operasional PLN</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">Silakan login menggunakan akun dinas Anda</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if submit_btn:
                if username_input in USER_DB:
                    if password_input == USER_DB[username_input]["password"]:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username_input
                        st.session_state["user_info"] = USER_DB[username_input]
                        st.success(f"Selamat datang, {USER_DB[username_input]['nama']}!")
                        st.rerun()
                    else:
                        st.error("❌ Password salah!")
                else:
                    st.error("❌ Username tidak ditemukan!")

# 6. Kontrol Utama Tampilan
if not st.session_state["logged_in"]:
    show_login_page()
else:
    # --- JIKA SUDAH LOGIN, TAMPILKAN DASHBOARD ---
    
    # Sidebar User Info & Logout
    with st.sidebar:
        st.markdown("### 👤 Profil Pengguna")
        st.write(f"**Nama:** {st.session_state['user_info']['nama']}")
        st.caption(f"Role: {st.session_state['user_info']['role']}")
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["user_info"] = {}
            st.rerun()
        st.divider()
        st.markdown("### 🔗 Link Layanan PLN")
        st.link_button("🌐 Portal Layanan & AP2T", "https://layanan.pln.co.id", use_container_width=True)
        st.link_button("📱 Download PLN Mobile", "https://play.google.com/store/apps/details?id=com.pln.pelanggan", use_container_width=True)

    # Header Banner Bergerak
    st.markdown(f"""
    <div class="header-banner">
        <h1 style="margin: 0; font-size: 1.8rem; color: #ffffff;">⚡ Dashboard Operasional PLN</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Selamat datang kembali, <b>{st.session_state['user_info']['nama']}</b>! Pilih modul pekerjaan di bawah ini.</p>
    </div>
    """, unsafe_allow_html=True)

    # Section Grid Modul
    st.subheader("🚀 Pilih Modul Operasional")
    
    col1, col2 = st.columns(2)

    with col1:
        st.page_link(
            "pages/1_Generator_Surat.py", 
            label="1. Generator Surat & Arsip (ZIP)\n\nBuat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara massal dari data Excel.", 
            icon="🚀",
            use_container_width=True
        )
        
        st.write("")

        st.page_link(
            "pages/2_Kalkulator_P2TL.py", 
            label="2. Kalkulator Simulasi P2TL\n\nHitung perkiraan tagihan susulan P2TL berdasarkan golongan tarif, jam nyala, dan pelanggaran.", 
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
            label="4. Generator QR Code Validasi\n\nBuat QR Code validasi dokumen/surat tugas/TTD secara otomatis yang dapat di-embed atau diunduh.", 
            icon="📱",
            use_container_width=True
        )

        st.write("")

        st.page_link(
            "pages/6_Kalkulator_Denda_BK.py", 
            label="6. Kalkulator Denda Keterlambatan (BK)\n\nHitung simulasi biaya keterlambatan (BK) tagihan listrik berdasarkan golongan tarif.", 
            icon="⚠️",
            use_container_width=True
        )

    st.divider()

    # Section Grafik Tren Interaktif
    st.subheader("📈 Pemantauan Aktivitas Operasional")
    chart_data = pd.DataFrame(
        np.random.randn(15, 3) + [12, 18, 15],
        columns=['Validasi P2TL', 'Clean Data AP2T', 'Generator Surat']
    )
    st.line_chart(chart_data)