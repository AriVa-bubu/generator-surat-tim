import hashlib
import os
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login dengan Full Background Gedung & Minimalist Login Card."""
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

    # CSS Custom: Modern Glassmorphism Centered Login
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Full Background Gambar Gedung */
            .stApp {
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
                background-image: linear-gradient(135deg, rgba(11, 15, 25, 0.85) 0%, rgba(9, 13, 22, 0.90) 100%),
                                  url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
            }

            @media (prefers-color-scheme: light) {
                .stApp {
                    background-image: linear-gradient(135deg, rgba(248, 250, 252, 0.85) 0%, rgba(226, 232, 240, 0.90) 100%),
                                      url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
                }
            }

            /* Styling Kartu Form Login Glassmorphism Centered */
            div[data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.78) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 24px !important;
                padding: 40px 36px 32px 36px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
            }

            @media (prefers-color-scheme: light) {
                div[data-testid="stForm"] {
                    background: rgba(255, 255, 255, 0.88) !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
                }
            }

            /* Logo Styling tanpa background putih ekstra */
            .pln-logo-wrapper {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
            }

            .pln-logo-img {
                width: 72px;
                height: auto;
                object-fit: contain;
                mix-blend-mode: multiply;
                filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.3));
            }

            /* Header Title & Subtitle di dalam Card */
            .login-card-title {
                text-align: center;
                font-size: 1.6rem;
                font-weight: 800;
                margin-bottom: 6px;
                letter-spacing: -0.02em;
            }

            .login-card-subtitle {
                text-align: center;
                opacity: 0.8;
                font-size: 0.88rem;
                margin-bottom: 28px;
                line-height: 1.4;
            }

            /* Tombol Login Merah Coral Modern (Bukan Biru) */
            .stButton > button {
                background: linear-gradient(135deg, #ff5252 0%, #ff3b30 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 0.98rem !important;
                color: white !important;
                box-shadow: 0 10px 20px -5px rgba(255, 59, 48, 0.4) !important;
                transition: all 0.2s ease !important;
            }

            .stButton > button:hover {
                box-shadow: 0 12px 24px -4px rgba(255, 59, 48, 0.6) !important;
                transform: translateY(-1px);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # Layout Terpusat (Centered 1 Kolom)
    _, col_center, _ = st.columns([1, 1.1, 1])

    with col_center:
        # URL Logo PLN Resmi Clean
        logo_url = (
            "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png"
        )

        with st.form("login_form"):
            # Logo, Judul & Subtitle dimasukkan ke dalam Form Card agar menyatu rapi
            st.markdown(
                f"""
                <div class="pln-logo-wrapper">
                    <img src="{logo_url}" class="pln-logo-img" alt="Logo PLN">
                </div>
                <h2 class="login-card-title">🔒 Selamat Datang</h2>
                <p class="login-card-subtitle">Sistem Manajemen & Pelayanan Listrik PLN</p>
                """,
                unsafe_allow_html=True,
            )

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