import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login pengguna dengan UI Modern & Background Hero."""
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

    # Styling CSS Kustom untuk Portal Login
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Container Utama Login Card */
            .login-hero-card {
                background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
                border-radius: 20px;
                padding: 32px;
                color: white;
                box-shadow: 0 20px 40px rgba(0, 168, 232, 0.15);
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }

            .pln-hero-img {
                width: 100%;
                border-radius: 14px;
                object-fit: cover;
                height: 180px;
                margin-top: 15px;
                margin-bottom: 20px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            }

            .badge-status {
                background-color: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #ffb703;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 14px;
                border-radius: 30px;
                display: inline-block;
                margin-bottom: 12px;
            }

            .feature-list {
                list-style: none;
                padding: 0;
                margin: 15px 0 0 0;
                font-size: 0.88rem;
                color: #e2e8f0;
            }

            .feature-list li {
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            /* Form Card Sisi Kanan */
            div[data-testid="stForm"] {
                background-color: #0f172a !important;
                border: 1px solid #1e293b !important;
                border-radius: 20px !important;
                padding: 28px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
            }

            .login-header-title {
                font-size: 1.6rem;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 4px;
            }

            .login-header-sub {
                color: #94a3b8;
                font-size: 0.88rem;
                margin-bottom: 20px;
            }

            /* Custom Button Login */
            .stButton > button {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Cek Logo PLN
    logo_path = "logo_pln.png"
    if not os.path.exists(logo_path):
        logo_path = "assets/logo_pln.png"

    # Layout 2 Kolom (Sisi Kiri Banner/Gedung, Sisi Kanan Form Login)
    col_hero, col_login = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div class="login-hero-card">
                <div>
                    <span class="badge-status">⚡ PORTAL OPERASIONAL INTEGRATED</span>
                    <h2 style="margin: 0; font-weight: 800; font-size: 1.8rem;">Sistem Manajemen & Pelayanan Listrik PLN</h2>
                    <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 8px;">
                        Platform digital terpadu untuk efisiensi pembuatan surat, kalkulasi P2TL, deteksi KWH macet, dan analisis data operasional.
                    </p>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Gambar Gedung Operasional PLN / Infrastruktur Kelistrikan (Unsplash High Quality)
        st.markdown(
            '<img'
            ' src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop"'
            ' class="pln-hero-img" alt="Gedung PLN Operational Center">',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
                <div>
                    <ul class="feature-list">
                        <li>✅ Otomatisasi Generator Surat & Dokumen Multi-Halaman</li>
                        <li>✅ Kalkulator Akurat P2TL & Rekomendasi Konversi</li>
                        <li>✅ Sistem Aman dengan Proteksi Akses Berlapis</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_login:
        # Menampilkan Logo PLN
        if os.path.exists(logo_path):
            st.image(logo_path, width=110)
        else:
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png",
                width=100,
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