import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login pengguna dengan UI Adaptif (Dark/Light)."""
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

    # CSS Adaptif berdasarkan tema sistem/Streamlit
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Container Kiri & Kartu Adaptif */
            .hero-container-adaptive {
                background-color: var(--secondary-background-color);
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-radius: 24px;
                padding: 36px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            }

            .badge-status {
                background: rgba(14, 165, 233, 0.15);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #0284c7;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 14px;
                border-radius: 30px;
                display: inline-block;
                margin-bottom: 12px;
            }

            .pln-hero-img {
                width: 100%;
                height: 190px;
                object-fit: cover;
                border-radius: 16px;
                margin: 18px 0;
                border: 1px solid rgba(128, 128, 128, 0.2);
            }

            /* Custom Styling Form Login */
            div[data-testid="stForm"] {
                background-color: var(--secondary-background-color) !important;
                border: 1px solid rgba(128, 128, 128, 0.2) !important;
                border-radius: 24px !important;
                padding: 32px !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08) !important;
            }

            .stButton > button {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
                color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = "logo_pln.png"
    if not os.path.exists(logo_path):
        logo_path = "assets/logo_pln.png"

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col_hero, col_login = st.columns([1.2, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div class="hero-container-adaptive">
                <span class="badge-status">⚡ PORTAL OPERASIONAL INTEGRATED</span>
                <h1 style="font-weight: 800; font-size: 2rem; margin-top: 10px; margin-bottom: 12px; line-height: 1.2;">
                    Sistem Manajemen & Pelayanan Listrik PLN
                </h1>
                <p style="opacity: 0.8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 16px;">
                    Platform digital terpadu untuk efisiensi pembuatan surat, kalkulasi P2TL, deteksi KWH macet, dan analisis data operasional.
                </p>
                <img src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop" 
                     class="pln-hero-img" alt="Gedung PLN">
                <div style="opacity: 0.9; font-size: 0.9rem; line-height: 1.8;">
                    ⚡ <b>Otomatisasi Document Generator</b> (Multi-halaman PDF)<br>
                    ⚡ <b>Kalkulator Akurat P2TL</b> & Rekomendasi Tarif<br>
                    ⚡ <b>Sistem Terenkripsi</b> & Akses Kontrol Terintegrasi
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_login:
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        else:
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png",
                width=95,
            )

        st.markdown(
            "<h2 style='margin-bottom: 2px; font-weight: 800;'>🔒 Selamat"
            " Datang</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='opacity: 0.7; font-size: 0.9rem; margin-bottom:"
            " 20px;'>Silakan masuk menggunakan akun resmi terdaftar.</p>",
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