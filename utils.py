import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
        /* Sembunyikan teks asli 'app' di seluruh halaman */
        [data-testid="stSidebarNav"] li:first-child a span {
            display: none;
        }
        
        /* Ganti dengan teks '🏠 Beranda Utama' */
        [data-testid="stSidebarNav"] li:first-child a::after {
            content: "🏠 Beranda Utama";
            font-weight: 500;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)