import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login pengguna dengan UI Modern & Rapi."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    # Ambil data kredensial dari Streamlit Secrets
    credentials = st.secrets.get("credentials", {})

    if not credentials:
        st.warning(
            "⚠️ Belum ada kredensial yang dikonfigurasi di Streamlit Secrets."
        )
        st.stop()

    # Custom CSS
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Background Utama */
            .stApp {
                background: radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.12) 0%, transparent 40%),
                            radial-gradient(circle at 80% 80%, rgba(3, 105, 161, 0.15) 0%, transparent 40%),
                            #0b0f19 !important;
            }

            .badge-status {
                background: rgba(14, 165, 233, 0.2);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38bdf8;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 14px;
                border-radius: 30px;
                display: inline-block;
                margin-bottom: 12px;
            }

            /* Style Gambar Hero */
            .pln-hero-img {
                width: 100%;
                height: 190px;
                object-fit: cover;
                border-radius: 16px;
                margin: 15px 0;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            }

            /* Form Styling */
            div[data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.8) !important;
                backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 20px !important;
                padding: 28px !important;
                box-shadow: 0 20px 40px rgba(0,0,0,0.5) !important;
            }

            .stButton > button {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 700 !important;
                padding: 0.7rem 1.5rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = "logo_pln.png"
    if not os.path.exists(logo_path):
        logo_path = "assets/logo_pln.png"

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col_hero, col_login = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown('<span class="badge-status">⚡ PORTAL OPERASIONAL INTEGRATED</span>', unsafe_allow_html=True)
        st.markdown("<h2 style='color: white; font-weight: 800; margin-top: 5px;'>Sistem Manajemen & Pelayanan Listrik PLN</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Platform digital terpadu untuk efisiensi pembuatan surat, kalkulasi P2TL, deteksi KWH macet, dan analisis data operasional.</p>", unsafe_allow_html=True)
        
        # Gambar Gedung
        st.markdown('<img src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop" class="pln-hero-img" alt="Gedung PLN">', unsafe_allow_html=True)
        
        # Feature List
        st.markdown("""
            <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.8;">
                ⚡ Otomatisasi Generator Surat & Dokumen Multi-Halaman<br>
                ⚡ Kalkulator Akurat P2TL & Rekomendasi Konversi<br>
                ⚡ Sistem Keamanan Akses Terenkripsi & Terintegrasi
            </div>
        """, unsafe_allow_html=True)

    with col_login:
        if os.path.exists(logo_path):
            st.image(logo_path, width=95)
        else:
            st.image("https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png", width=90)

        st.markdown("<h3 style='color: white; margin-bottom: 2px;'>🔒 Selamat Datang</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px;'>Silakan masuk menggunakan akun resmi terdaftar.</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🔑 Masuk ke Portal", type="primary", use_container_width=True)

            if submit:
                hashed_input = make_hash(password)
                saved_pass = credentials.get(username)

                if saved_pass and (saved_pass == password or saved_pass == hashed_input):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login berhasil! Mengalihkan...")
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah.")

    st.stop()


def render_logout_button():
    """Menampilkan tombol logout di sidebar."""
    if st.session_state.get("logged_in", False):
        with st.sidebar:
            st.markdown("---")
            st.write(f"👤 Login sebagai: **{st.session_state.get('username', 'User').upper()}**")
            if st.button("🚪 Keluar / Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()