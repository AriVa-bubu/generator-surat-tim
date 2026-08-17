import hashlib
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login dengan Full Background Gedung & Form Login Menyatu Elegan."""
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

    # URL Logo PLN Transparan Resmi (SVG/PNG)
    pln_transparent_logo = "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png"

    # Styling CSS Adaptif & Elegan
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
            }

            /* Full Background Gambar Gedung Modern */
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

            /* Styling Form Login Glassmorphism Minimalis & Menyatu */
            div[data-testid="stForm"] {
                background: rgba(15, 23, 42, 0.75) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                border-radius: 24px !important;
                padding: 36px 32px 32px 32px !important;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
            }

            @media (prefers-color-scheme: light) {
                div[data-testid="stForm"] {
                    background: rgba(255, 255, 255, 0.88) !important;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
                }
            }

            /* Styling Logo PLN Tanpa Background Putih */
            .pln-logo-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 16px;
            }

            .pln-logo-img {
                height: 64px;
                width: auto;
                object-fit: contain;
                filter: drop-shadow(0px 6px 12px rgba(0, 0, 0, 0.4));
            }

            /* Header Label di Dalam Form */
            .login-header-title {
                text-align: center;
                font-weight: 800;
                font-size: 1.5rem;
                margin-bottom: 4px;
                letter-spacing: -0.02em;
            }

            .login-header-subtitle {
                text-align: center;
                opacity: 0.8;
                font-size: 0.88rem;
                margin-bottom: 24px;
                line-height: 1.4;
            }

            /* Tombol Login Merah Elegan */
            .stButton > button {
                background: linear-gradient(135deg, #ff4b4b 0%, #dc2626 100%) !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.5rem !important;
                font-size: 1rem !important;
                color: white !important;
                box-shadow: 0 10px 20px -5px rgba(220, 38, 38, 0.5) !important;
                transition: all 0.2s ease !important;
            }

            .stButton > button:hover {
                box-shadow: 0 12px 24px -4px rgba(220, 38, 38, 0.7) !important;
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
        with st.form("login_form"):
            # Header & Logo PLN Transparan Dimasukkan ke Dalam Form
            st.markdown(
                f"""
                <div class="pln-logo-container">
                    <img src="{pln_transparent_logo}" class="pln-logo-img" alt="Logo PLN">
                </div>
                <h2 class="login-header-title">🔒 Selamat Datang</h2>
                <p class="login-header-subtitle">Sistem Manajemen & Pelayanan Listrik PLN</p>
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