import streamlit as st
import os
from PIL import Image
from utils import load_custom_css

# Config
logo_icon = "⚡"
if os.path.exists("logo_pln.png"):
    logo_icon = Image.open("logo_pln.png")

st.set_page_config(page_title="Kalkulator Biaya Tambah Daya", page_icon=logo_icon, layout="wide")
load_custom_css()

st.title("⚡ Kalkulator Estimasi Biaya Tambah Daya (PB/NJ)")
st.caption("Hitung perkiraan Biaya Penyambungan (BP) dan Uang Jaminan Langganan (UJL)")

col1, col2 = st.columns(2)

with col1:
    gol_tarif = st.selectbox("Golongan Tarif", ["R-1 / TR", "B-1 / TR", "I-1 / TR", "S-2 / TR"])
    daya_lama = st.number_input("Daya Lama (VA)", min_value=0, value=900, step=450)
    daya_baru = st.number_input("Daya Baru (VA)", min_value=450, value=2200, step=450)
    tarif_bp_per_va = st.number_input("Biaya Penyambungan per VA (Rp)", value=960)

with col2:
    ujl_per_va = st.number_input("Estimasi UJL per VA (Rp)", value=150)
    biaya_materai = st.selectbox("Biaya Materai (Rp)", [0, 10000], index=1)

if st.button("🧮 Hitung Estimasi Biaya", type="primary"):
    if daya_baru <= daya_lama:
        st.error("Daya Baru harus lebih besar dari Daya Lama!")
    else:
        selisih_daya = daya_baru - daya_lama
        total_bp = selisih_daya * tarif_bp_per_va
        total_ujl = selisih_daya * ujl_per_va
        total_biaya = total_bp + total_ujl + biaya_materai

        st.success("✅ Perhitungan Berhasil!")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Tambah Daya", f"{selisih_daya:,} VA")
        m2.metric("Biaya Penyambungan (BP)", f"Rp {total_bp:,.0f}")
        m3.metric("Estimasi UJL", f"Rp {total_ujl:,.0f}")

        st.info(f"### 💳 Total Estimasi Biaya: **Rp {total_biaya:,.0f}**")