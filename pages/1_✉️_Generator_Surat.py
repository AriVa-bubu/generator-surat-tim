import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import zipfile
import re
import subprocess
import tempfile
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_path = "logo_pln.png"
logo_base64 = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)

st.set_page_config(
    page_title="Generator Surat - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 168, 232, 0.2);
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .hero-logo-img {
        width: 70px;
        height: auto;
        border-radius: 8px;
        background: white;
        padding: 4px;
    }

    .hero-badge {
        background-color: #ffb703;
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }

    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
    }

    .step-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }

    .step-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
    }

    .step-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .step-number {
        background: linear-gradient(135deg, #0284c7, #0369a1);
        color: white;
        font-size: 0.85rem;
        font-weight: 700;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    .stat-card {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 10px;
        padding: 14px 18px;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }
    .stat-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 2px;
    }

    div[data-testid="stFileUploader"] {
        background-color: #1e293b;
        border: 1px dashed #475569;
        border-radius: 12px;
        padding: 8px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else '⚡'

st.markdown(f"""
<div class="hero-banner">
    <div>{logo_html}</div>
    <div>
        <span class="hero-badge">MODUL 1</span>
        <div class="hero-title">✉️ Generator Surat & Arsip Otomatis</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown("""
    1. **Upload File Excel**: Pastikan kolom header berada di baris paling atas.
    2. **Upload Template Word**: Gunakan tag `{{ NAMA_KOLOM }}` di dalam file `.docx`.
    3. **Pilihan Folder**: Pilih kolom `TANGGAL` atau `ULP` untuk mengelompokkan hasil ke sub-folder digital di dalam ZIP.
    4. **Output PDF**: Jika memilih PDF, dokumen otomatis dikonversi oleh server secara instan.
    """)

st.markdown("""
<div class="step-card">
    <div class="step-header">
        <div class="step-title">
            <span class="step-number">1</span> Unggah Sumber Data & Template
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 Data Excel Target (`.xlsx`)**")
    excel_file = st.file_uploader("Pilih file excel", type=["xlsx", "xls"], key="excel_uploader")

with col2:
    st.markdown("**📝 Template Surat (`.docx`)**")
    word_file = st.file_uploader("Pilih template word", type=["docx"], key="word_uploader")

if excel_file and word_file:
    try:
        df = pd.read_excel(excel_file)
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x) if col.dtype == "object" else col)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📈 Ringkasan Data Rencana Cetak")
        s1, s2, s3 = st.columns(3)
        
        with s1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Surat Dicetak</div>
                <div class="stat-value">{len(df)} Dokumen</div>
            </div>
            """, unsafe_allow_html=True)
            
        with s2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Variabel Kolom Excel</div>
                <div class="stat-value">{len(df.columns)} Kolom</div>
            </div>
            """, unsafe_allow_html=True)

        with s3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Status File Template</div>
                <div class="stat-value" style="color:#4ade80;">Ready ✓</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📋 Pratinjau Data Excel:")
        st.dataframe(df.head(5), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-title">
                    <span class="step-number">2</span> Pengaturan File & Pengarsipan
                </div>
            </div>
        """, unsafe_allow_html=True)

        c_opt1, c_opt2, c_opt3 = st.columns(3)

        with c_opt1:
            naming_column = st.selectbox(
                "Penamaan File Berdasarkan:",
                options=df.columns.tolist(),
                index=0
            )

        with c_opt2:
            options_folder = ["Tanpa Folder (1 Folder Utama)"] + df.columns.tolist()
            folder_column = st.selectbox(
                "Pengelompokan Sub-Folder (ZIP):",
                options=options_folder,
                index=0,
                help="Pilih kolom TANGGAL atau ULP untuk membagi file ke sub-folder otomatis."
            )

        with c_opt3:
            output_format = st.radio(
                "Format File Keluaran:",
                options=["DOCX (Word)", "PDF Format"],
                horizontal=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("⚡ MULAI PROSES GENERATE SURAT", type="primary", use_container_width=True)

        if generate_btn:
            zip_buffer = io.BytesIO()
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(df)
            is_pdf = "PDF" in output_format

            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for idx, row in df.iterrows():
                        status_text.text(f"⏳ Mengolah Surat {idx + 1} dari {total_rows} ({output_format})...")
                        
                        context = {}
                        for col in df.columns:
                            val = row[col]
                            if isinstance(val, pd.Timestamp):
                                context[str(col)] = val.strftime("%d-%m-%Y")
                            else:
                                context[str(col)] = "" if pd.isna(val) else str(val)
                        
                        doc_tpl = DocxTemplate(word_file)
                        doc_tpl.render(context)
                        
                        filename_val = str(row[naming_column]).strip()
                        clean_filename = re.sub(r'[\\/*?:"<>|]', "", filename_val)
                        
                        folder_path = ""
                        if folder_column != "Tanpa Folder (1 Folder Utama)":
                            raw_folder_val = row[folder_column]
                            if isinstance(raw_folder_val, pd.Timestamp):
                                clean_folder_name = raw_folder_val.strftime("%Y-%m-%d")
                            else:
                                clean_folder_name = re.sub(r'[\\/*?:"<>|]', "", str(raw_folder_val).strip())
                            
                            if clean_folder_name:
                                folder_path = f"{clean_folder_name}/"
                        
                        if is_pdf:
                            temp_docx_path = os.path.join(temp_dir, f"temp_{idx}.docx")
                            doc_tpl.save(temp_docx_path)
                            
                            cmd = ["libreoffice", "--headless", "--convert-to", "pdf", temp_docx_path, "--outdir", temp_dir]
                            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
                            generated_pdf = os.path.join(temp_dir, f"temp_{idx}.pdf")
                            if os.path.exists(generated_pdf):
                                with open(generated_pdf, "rb") as pdf_file:
                                    pdf_data = pdf_file.read()
                                
                                zip_file.writestr(f"{folder_path}Surat_{clean_filename}.pdf", pdf_data)
                                os.remove(generated_pdf)
                            if os.path.exists(temp_docx_path):
                                os.remove(temp_docx_path)
                        else:
                            doc_io = io.BytesIO()
                            doc_tpl.save(doc_io)
                            zip_file.writestr(f"{folder_path}Surat_{clean_filename}.docx", doc_io.getvalue())
                        
                        progress_bar.progress((idx + 1) / total_rows)

            status_text.empty()
            progress_bar.empty()
            
            st.toast("🎉 Semua surat berhasil dibuat!", icon="⚡")
            st.success(f"🎉 Selesai! Berhasil memproses **{total_rows} surat** secara otomatis.")
            
            st.download_button(
                label=f"⬇️ UNDUH ARSIP SURAT (.ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"Arsip_Surat_PLN_{'PDF' if is_pdf else 'DOCX'}.zip",
                mime="application/zip",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan sistem: {str(e)}")

else:
    st.info("💡 **Petunjuk:** Silakan unggah **File Excel** dan **Template Word** di atas untuk membuka panel pengaturan.")
