import hashlib
import streamlit as st


def make_hash(password: str) -> str:
    """Mengubah string password biasa menjadi kode Hash SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login():
    """Memeriksa status login pengguna."""
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

    # Form Login
    st.markdown("### 🔒 Portal Operasional PLN")
    st.caption("Masuk dengan akun yang terdaftar untuk melanjutkan.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("🔑 Masuk", type="primary")

        if submit:
            hashed_input = make_hash(password)
            saved_pass = credentials.get(username)

            # Cek cocok teks biasa ATAU cocok kode hash
            if saved_pass and (
                saved_pass == password or saved_pass == hashed_input
            ):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("❌ Username atau password salah.")

    st.stop()


def render_logout_button():
    """Menampilkan tombol logout di sidebar."""
    if st.session_state.get("logged_in", False):
        with st.sidebar:
            st.write(f"👤 Login sebagai: **{st.session_state.get('username', 'User')}**")
            if st.button("🚪 Keluar / Logout"):
                st.session_state.logged_in = False
                st.rerun()