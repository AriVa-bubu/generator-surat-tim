import streamlit as st
import pandas as pd
import io
import os
import base64
import streamlit as st

st.set_page_config(...)   # HARUS paling atas
from auth import check_login, render_logout_button
check_login()
render_logout_button()
# baru kode fitur di bawahnya

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
    page_title="Clean Data Excel - PLN Platform",
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
        <span class="hero-badge">MODUL 3</span>
        <div class="hero-title">🧹 Cleaning & Standarisasi Data Excel AP2T</div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_excel = st.file_uploader("Upload Excel mentah dari AP2T (.xlsx):", type=["xlsx", "xls"])

if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    st.markdown("##### 📋 Data Asli (Sebelum Dibersihkan):")
    st.dataframe(df.head(), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        format_rp = st.checkbox("Format Angka Tagihan/Rupiah ke 'Rp X.XXX.XXX,-'", value=True)
        trim_space = st.checkbox("Hapus Spasi Ganda & Spasi Ujung Teks", value=True)
    with col2:
        proper_case = st.checkbox("Ubah Format Nama ke Huruf Kapital Sesuai (Proper Case)", value=True)

    if st.button("✨ Bersihkan & Format Excel", type="primary", use_container_width=True):
        cleaned_df = df.copy()

        if trim_space:
            cleaned_df = cleaned_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

        if proper_case:
            cleaned_df = cleaned_df.apply(lambda col: col.map(lambda x: x.title() if isinstance(x, str) else x))

        if format_rp:
            for col in cleaned_df.columns:
                if "RUPIAH" in str(col).upper() or "TAGIHAN" in str(col).upper() or "BIAYA" in str(col).upper():
                    cleaned_df[col] = cleaned_df[col].apply(lambda x: f"Rp {int(x):,},-".replace(",", ".") if pd.notnull(x) and isinstance(x, (int, float)) else x)

        st.success("✅ Data berhasil dibersihkan & diformat!")
        st.markdown("##### 📋 Hasil Data yang Sudah Bersih:")
        st.dataframe(cleaned_df.head(), use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name='Data_Bersih')

        st.download_button(
            label="⬇️ Unduh Excel Hasil Cleaning (.xlsx)",
            data=output.getvalue(),
            file_name="Data_Pelanggan_Cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
