import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login pengguna dengan Background Elegan khas PLN."""
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

    # Styling CSS Kustom untuk Background Elegan & Card Glassmorphism
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Background Elegan Gradien Mesh PLN Dark Theme */
            .stApp {
                background: radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.15) 0%, transparent 45%),
                            radial-gradient(circle at 85% 80%, rgba(3, 105, 161, 0.2) 0%, transparent 50%),
                            radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.8) 0%, #090d16 100%) !important;
                background-attachment: fixed !important;
            }

            /* Container Kartu Kiri (Hero) */
            .login-hero-card {
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.7));
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(56, 189, 248, 0.2);
                border-radius: 24px;
                padding: 32px;
                color: white;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            }

            .pln-hero-img-container {
                position: relative;
                overflow: hidden;
                border-radius: 16px;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .pln-hero-img {
                width: 100%;
                height: 200px;
                object-fit: cover;
                display: block;
                transition: transform 0.5s ease;
            }

            .pln-hero-img-container:hover .pln-hero-img {
                transform: scale(1.03);
            }

            .badge-status {
                background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(2, 132, 199, 0.3));
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38bdf8;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 14px;
                border-radius: 30px;
                display: inline-block;
                margin-bottom: 14px;
                letter-spacing: 0.5px;
            }

            .feature-list {
                list-style: none;
                padding: 0;
                margin: 18px 0 0 0;
                font-size: 0.88rem;
                color: #cbd5e1;
            }

            .feature-list li {
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            /* Container Form Sisi Kanan */
            div[data-testid="stForm"] {
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.85)) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 24px !important;
                padding: 32px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6) !important;
            }

            .login-header-title {
                font-size: 1.75rem;
                font-weight: 800;
                color: #f8fafc;
                margin-top: 8px;
                margin-bottom: 4px;
                letter-spacing: -0.5px;
            }

            .login-header-sub {
                color: #94a3b8;
                font-size: 0.88rem;
                margin-bottom: 24px;
            }

            /* Custom Styling Input & Button Login */
            .stTextInput > div > div {
                border-radius: 12px !important;
                background-color: rgba(15, 23, 42, 0.6) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
            }

            .stButton > button {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
                box-shadow: 0 10px 20px -5px rgba(2, 132, 199, 0.5) !important;
                transition: all 0.3s ease !important;
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 25px -5px rgba(2, 132, 199, 0.7) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Cek Logo PLN
    logo_path = "logo_pln.png"
    if not os.path.exists(logo_path):
        logo_path = "assets/logo_pln.png"

    # Alignment Spacing Atas
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Layout 2 Kolom
    col_hero, col_login = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div class="login-hero-card">
                <div>
                    <span class="badge-status">⚡ PORTAL OPERASIONAL INTEGRATED</span>
                    <h2 style="margin: 0; font-weight: 800; font-size: 1.85rem; line-height: 1.2; color: #ffffff;">
                        Sistem Manajemen & Pelayanan Listrik PLN
                    </h2>
                    <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 10px; line-height: 1.5;">
                        Platform digital terpadu untuk efisiensi pembuatan surat, kalkulasi P2TL, deteksi KWH macet, dan analisis data operasional.
                    </p>
                </div>
                
                <div class="pln-hero-img-container">
                    <img src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop" 
                         class="pln-hero-img" alt="Gedung PLN Operational Center">
                </div>

                <div>
                    <ul class="feature-list">
                        <li>⚡ Otomatisasi Generator Surat & Dokumen Multi-Halaman</li>
                        <li>⚡ Kalkulator Akurat P2TL & Rekomendasi Konversi</li>
                        <li>⚡ Sistem Keamanan Akses Terenkripsi & Terintegrasi</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_login:
        # Menampilkan Logo PLN
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        else:
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png",
                width=95,
            )

        st.markdown(
            '<div class="login-header-title">🔒 Selamat Datang</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-header-sub">Silakan masuk menggunakan akun'
            " resmi terdaftar.</div>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input(
                "Password", type="password", placeholder="Masukkan password"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button(
                "🔑 Masuk ke Portal", type="primary", use_container_width=True
            )

            if submit:
                hashed_input = make_hash(password)
                saved_pass = credentials.get(username)

                if saved_pass and (
                    saved_pass == password or saved_pass == hashed_input
                ):
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
            st.write(
                "👤 Login sebagai: **"
                f"{st.session_state.get('username', 'User').upper()}**"
            )
            if st.button("🚪 Keluar / Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()