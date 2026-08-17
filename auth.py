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
                background-image: linear-gradient(135deg, rgba(11, 15, 25, 0.82) 0%, rgba(9, 13, 22, 0.88) 100%),
                                  url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
            }

            @media (prefers-color-scheme: light) {
                .stApp {
                    background-image: linear-gradient(135deg, rgba(248, 250, 252, 0.82) 0%, rgba(226, 232, 240, 0.88) 100%),
                                      url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop") !important;
                }
            }

            /* Styling Kartu Form Login Glassmorphism Centered */
            div[data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.75) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 24px !important;
                padding: 40px 36px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
            }

            @media (prefers-color-scheme: light) {
                div[data-testid="stForm"] {
                    background: rgba(255, 255, 255, 0.85) !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
                }
            }

            /* Logo Styling */
            .pln-logo-wrapper {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
            }

            .pln-logo-img {
                width: 68px;
                height: auto;
                object-fit: contain;
                filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.3));
            }

            /* Tombol Login Merah Coral */
            .stButton > button {
                background: linear-gradient(135deg, #ff4b4b 0%, #ff3b30 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
                color: white !important;
                box-shadow: 0 10px 20px -5px rgba(255, 75, 75, 0.4) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # Layout Terpusat (Centered 1 Kolom)
    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        # Logo PLN Transparan & Rapi
        logo_url = (
            "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png"
        )

        with st.form("login_form"):
            # Logo, Title, dan Subtitle diletakkan DI DALAM form agar menyatu di dalam kartu
            st.markdown(
                f"""
                <div class="pln-logo-wrapper">
                    <img src="{logo_url}" class="pln-logo-img" alt="Logo PLN">
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "<h2 style='text-align: center; margin-bottom: 4px; font-weight:"
                " 800;'>🔒 Selamat Datang</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; opacity: 0.8; font-size: 0.9rem;"
                " margin-bottom: 24px;'>Sistem Manajemen & Pelayanan Listrik"
                " PLN</p>",
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