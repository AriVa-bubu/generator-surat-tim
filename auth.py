import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login dengan Full Background Gedung Adaptif (Dark/Light)."""
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

    # CSS Custom: Background Full Gedung dengan Adaptasi Tema (Light / Dark)
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* --- BASE BACKGROUND FULL GEDUNG --- */
            .stApp {
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }

            /* 1. STYLING DEFAULT / DARK MODE */
            .stApp {
                background-image: linear-gradient(135deg, rgba(11, 15, 25, 0.88) 0%, rgba(9, 13, 22, 0.92) 100%),
                                  url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
            }

            .hero-container-adaptive {
                background: rgba(15, 23, 42, 0.65);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
                padding: 36px;
                color: #ffffff;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }

            div[data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.8) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 24px !important;
                padding: 32px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6) !important;
            }

            .badge-status {
                background: rgba(14, 165, 233, 0.25);
                border: 1px solid rgba(56, 189, 248, 0.5);
                color: #38bdf8;
                font-weight: 700;
                font-size: 0.75rem;
                padding: 6px 14px;
                border-radius: 30px;
                display: inline-block;
                margin-bottom: 12px;
            }

            /* 2. OVERRIDE OTOMATIS SAAT TEMA LIGHT / TERANG AK TIF */
            @media (prefers-color-scheme: light) {
                .stApp {
                    background-image: linear-gradient(135deg, rgba(248, 250, 252, 0.88) 0%, rgba(226, 232, 240, 0.92) 100%),
                                      url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
                }

                .hero-container-adaptive {
                    background: rgba(255, 255, 255, 0.75);
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    color: #0f172a;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
                }

                .hero-container-adaptive p, .hero-container-adaptive div {
                    color: #334155 !important;
                }

                div[data-testid="stForm"] {
                    background: rgba(255, 255, 255, 0.85) !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
                }

                .badge-status {
                    background: rgba(2, 132, 199, 0.15);
                    border: 1px solid rgba(2, 132, 199, 0.4);
                    color: #0284c7;
                }
            }

            /* Styling Button Universal */
            .stButton > button {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
                color: white !important;
                box-shadow: 0 10px 20px -5px rgba(2, 132, 199, 0.5) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = "logo_pln.png"
    if not os.path.exists(logo_path):
        logo_path = "assets/logo_pln.png"

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    col_hero, col_login = st.columns([1.2, 1], gap="large")

    with col_hero:
        st.markdown(
            """
            <div class="hero-container-adaptive">
                <span class="badge-status">⚡ PORTAL OPERASIONAL INTEGRATED</span>
                <h1 style="font-weight: 800; font-size: 2.2rem; margin-top: 10px; margin-bottom: 12px; line-height: 1.2;">
                    Sistem Manajemen & Pelayanan Listrik PLN
                </h1>
                <p style="font-size: 1rem; line-height: 1.6; margin-bottom: 24px;">
                    Platform digital terpadu untuk efisiensi pembuatan surat, kalkulasi P2TL, deteksi KWH macet, dan analisis data operasional secara <i>real-time</i>.
                </p>
                <div style="font-size: 0.95rem; line-height: 2;">
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
            "<p style='opacity: 0.8; font-size: 0.9rem; margin-bottom:"
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