import streamlit as st
import qrcode
import io
import os
import base64
import streamlit as st

# --- GUARD / PROTEKSI HALAMAN (WAJIB LOGIN) ---
st.set_page_config(...)   # HARUS paling atas
from auth import check_login, render_logout_button
check_login()
render_logout_button()
# baru kode fitur di bawahnya
# ----------------------------------------------

# --- KODE MODUL FITUR KAMU DI BAWAH INI ---
st.title("📄 Generator Surat & Arsip")
# ... Sisa kode fitur modul kamu
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_path = "logo_pln.png"
logo_base64 = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)

st.set_page_config(
    page_title="Generator QR Code - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide"
)
from auth import check_login, render_logout_button
check_login()
render_logout_button() 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1100px; }
    .hero-banner {
        background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
        border-radius: 16px; padding: 24px 28px; color: white; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
    }
    .hero-logo-img { width: 70px; height: auto; border-radius: 8px; background: white; padding: 4px; }
    .hero-badge { background-color: #ffb703; color: #000; font-weight: 800; font-size: 0.75rem; padding: 4px 12px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 6px; }
    .hero-title { font-size: 1.8rem; font-weight: 800; margin: 0; }
</style>
""", unsafe_allow_html=True)

logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else '⚡'

st.markdown(f"""
<div class="hero-banner">
    <div>{logo_html}</div>
    <div>
        <span class="hero-badge">MODUL 4</span>
        <div class="hero-title">🔳 Generator QR Code Validasi Surat</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    no_surat = st.text_input("Nomor Surat / Agenda:", "0123/STH.01.01/ULP-KOTA/2026")
    nama_petugas = st.text_input("Nama Penandatangan / Petugas:", "Bambang Kurniawan")
    idpel = st.text_input("IDPEL / Target Pelanggan:", "531200984123")

with col2:
    st.markdown("**Pratinjau Teks yang Tersimpan di QR Code:**")
    data_qr = f"DOKUMEN RESMI PLN\nNo. Agenda: {no_surat}\nPetugas: {nama_petugas}\nIDPEL: {idpel}\nStatus: VALID & TERVERIFIKASI"
    st.code(data_qr)

if st.button("🔳 Buat QR Code Sekarang", type="primary", use_container_width=True):
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(data_qr)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img_qr.save(buf, format="PNG")
    byte_im = buf.getvalue()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(byte_im, caption="QR Code Validasi Dokumen", width=250)
        st.download_button(
            label="⬇️ Unduh Gambar QR Code (.PNG)",
            data=byte_im,
            file_name=f"QR_Validasi_{idpel}.png",
            mime="image/png",
            use_container_width=True
        )
