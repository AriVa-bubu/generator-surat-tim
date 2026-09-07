"""
Modul autentikasi sederhana untuk Portal Operasional PLN.

Cara pakai:
    from auth import check_login, render_logout_button

    check_login()            # taruh di paling atas, setelah st.set_page_config()
    render_logout_button()   # taruh di sidebar, bisa dipanggil kapan saja setelah login

Password TIDAK disimpan sebagai teks polos di kode. Simpan hash-nya di
file `.streamlit/secrets.toml` (lokal) atau di menu "Secrets" Streamlit
Community Cloud (saat deploy). Lihat SECRETS_TEMPLATE di bawah untuk formatnya.
"""

import hashlib

import streamlit as st

SECRETS_TEMPLATE = """
# .streamlit/secrets.toml
# JANGAN commit file ini ke Git — tambahkan ke .gitignore

[credentials]
admin = "GANTI_DENGAN_HASH_PASSWORD_ADMIN"
operator1 = "GANTI_DENGAN_HASH_PASSWORD_OPERATOR"
"""


def hash_password(password: str) -> str:
    """Ubah password teks-biasa menjadi hash SHA-256 (hex)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _get_credentials() -> dict:
    try:
        return dict(st.secrets["credentials"])
    except (KeyError, FileNotFoundError):
        return {}


def check_login() -> None:
    """
    Gerbang login. Jika user belum login, tampilkan form login dan
    hentikan eksekusi halaman (st.stop()) sampai berhasil login.
    """
    if st.session_state.get("authenticated", False):
        return

    credentials = _get_credentials()

    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
            html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

            .login-card {
                max-width: 420px;
                margin: 60px auto 0 auto;
                background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
                border: 1px solid #2b3a52;
                border-radius: 18px;
                padding: 32px 32px 8px 32px;
                box-shadow: 0 20px 40px -12px rgba(2, 132, 199, 0.35);
            }
            .login-title {
                font-size: 1.4rem;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 4px;
            }
            .login-subtitle {
                font-size: 0.9rem;
                color: #94a3b8;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 1.2, 1])
    with center_col:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-title">🔒 Portal Operasional PLN</div>
                <div class="login-subtitle">Masuk dengan akun yang terdaftar untuk melanjutkan.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submitted = st.form_submit_button("🔑 Masuk", use_container_width=True, type="primary")

        if not credentials:
            st.warning(
                "⚠️ Belum ada kredensial yang dikonfigurasi. Admin perlu mengisi "
                "`st.secrets['credentials']` (lihat `auth.SECRETS_TEMPLATE`)."
            )

        if submitted:
            stored_hash = credentials.get(username.strip())
            if stored_hash and stored_hash == hash_password(password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username.strip()
                st.rerun()
            else:
                st.error("❌ Username atau password salah.")

    st.stop()


def render_logout_button() -> None:
    """Tampilkan info user & tombol logout di sidebar. Panggil setelah check_login()."""
    if not st.session_state.get("authenticated", False):
        return

    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] .stButton > button {
                    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
                    border: none !important;
                    border-radius: 10px !important;
                    font-weight: 700 !important;
                    color: white !important;
                    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
                }
                section[data-testid="stSidebar"] .stButton > button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 8px 16px -6px rgba(220, 38, 38, 0.5) !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        username = st.session_state.get("username", "-")
        initial = username[:1].upper() if username else "?"

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:10px; padding:12px 14px;
                        background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
                        border:1px solid #2b3a52; border-radius:12px; margin: 4px 0 10px 0;">
                <div style="width:36px; height:36px; border-radius:50%; flex-shrink:0;
                            background: linear-gradient(135deg, #0284c7, #0369a1);
                            display:flex; align-items:center; justify-content:center;
                            font-weight:800; color:white; font-size:0.95rem;">
                    {initial}
                </div>
                <div style="line-height:1.3;">
                    <div style="font-size:0.72rem; color:#94a3b8; text-transform:uppercase; font-weight:700; letter-spacing:0.03em;">
                        Login sebagai
                    </div>
                    <div style="font-size:0.95rem; font-weight:700; color:#f8fafc;">
                        {username}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Keluar / Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()