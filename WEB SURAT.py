import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import zipfile
import re
import subprocess
import tempfile
import os

# -----------------------------------------------------------------------------
# CONFIG & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Generator Surat Otomatis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS UNTUK UI/UX MEWAH & MODERN
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Hero Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #0284c7 100%);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 35px 40px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* Step Card Container */
    .step-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    .step-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 8px 20px -6px rgba(56, 189, 248, 0.15);
    }

    .step-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
        border-bottom: 1px solid #334155;
        padding-bottom: 12px;
    }

    .step-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .step-number {
        background: #0284c7;
        color: white;
        font-size: 0.9rem;
        font-weight: 700;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    /* Status Badges */
    .badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-success {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    div[data-testid="stFileUploader"] {
        background-color: #0f172a;
        border: 1px dashed #475569;
        border-radius: 12px;
        padding: 10px;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #38bdf8;
    }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HERO HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">
        ✉️ Generator Surat Otomatis
    </div>
    <p class="hero-subtitle">
        Buat puluhan hingga ratusan surat resmi (.DOCX / .PDF) secara otomatis dan instan dari data Excel & Template Word.
    </p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PANDUAN PENGGUNAAN (EXPANDER)
# -----------------------------------------------------------------------------
with st.expander("❓ **Petunjuk & Cara Penggunaan (Klik untuk Membuka)**"):
    st.markdown("""
    1. **Siapkan File Excel (`.xlsx`)**: Pastikan baris pertama berisi **Nama Kolom** (contoh: `NAMA`, `IDPEL`, `ALAMAT`, `TANGGAL`).
    2. **Siapkan Template Word (`.docx`)**: Gunakan format tag Jinja2 dengan tanda kurung keriting ganda `{{ NAMA }}` atau `{{ IDPEL }}` di posisi yang ingin diisi otomatis.
    3. **Pilih Format Output**: Anda bisa memilih hasil keluaran berupa **DOCX (Word)** atau **PDF**.
    4. **Unggah Berkas**: Masukkan kedua file pada **Langkah 1** di bawah ini.
    5. **Generate & Download**: Klik tombol buat surat lalu unduh file `.ZIP` hasil konversi.
    """)


# -----------------------------------------------------------------------------
# LANGKAH 1: UNGGAH BERKAS
# -----------------------------------------------------------------------------
st.markdown("""
<div class="step-card">
    <div class="step-header">
        <div class="step-title">
            <span class="step-number">1</span> Unggah Dokumen Sumber
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 1. File Excel Data Pelanggan/Target**")
    excel_file = st.file_uploader(
        "Upload data (.xlsx, .xls)",
        type=["xlsx", "xls"],
        key="excel_uploader",
        help="File berisi daftar nama, alamat, ID, dll."
    )

with col2:
    st.markdown("**📝 2. File Template Surat Word**")
    word_file = st.file_uploader(
        "Upload template (.docx)",
        type=["docx"],
        key="word_uploader",
        help="Template surat dengan placeholder {{ NAMA }}, {{ IDPEL }}, dll."
    )


# -----------------------------------------------------------------------------
# LANGKAH 2: PRATINJAU DATA & DETEKSI VARIABLE
# -----------------------------------------------------------------------------
if excel_file and word_file:
    try:
        df = pd.read_excel(excel_file)
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x) if col.dtype == "object" else col)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-title">
                    <span class="step-number">2</span> Pratinjau Data & Pengecekan
                </div>
                <span class="badge badge-success">✓ File Terdeteksi</span>
            </div>
        """, unsafe_allow_html=True)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Total Baris Data", f"{len(df)} Data")
        with m_col2:
            st.metric("Jumlah Kolom", f"{len(df.columns)} Kolom")
        with m_col3:
            st.metric("Pilihan Output", "DOCX / PDF")

        st.markdown("##### 📋 Pratinjau 5 Baris Data Pertama:")
        st.dataframe(df.head(), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------------------------------------------------------------
        # LANGKAH 3: PROSES GENERATE SURAT
        # -----------------------------------------------------------------------------
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-title">
                    <span class="step-number">3</span> Pengaturan & Proses Surat
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_opt1, col_opt2 = st.columns(2)

        with col_opt1:
            naming_column = st.selectbox(
                "Pilih Kolom Excel untuk Penamaan File Surat:",
                options=df.columns.tolist(),
                index=0,
                help="Contoh: Jika memilih kolom 'NAMA', nama file akan menjadi 'Surat_SRIANTINI'"
            )

        with col_opt2:
            output_format = st.radio(
                "Pilih Format File Output di dalam ZIP:",
                options=["DOCX (Word)", "PDF"],
                horizontal=True,
                help="Jika memilih PDF, file Word akan otomatis dikonversi ke PDF sebelum dikompresi."
            )

        generate_btn = st.button("🚀 Buat Semua Surat Sekarang", type="primary", use_container_width=True)

        if generate_btn:
            zip_buffer = io.BytesIO()
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(df)
            is_pdf = "PDF" in output_format

            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for idx, row in df.iterrows():
                        status_text.text(f"⏳ Memproses surat {idx + 1} dari {total_rows} ({output_format})...")
                        
                        context = {}
                        for col in df.columns:
                            val = row[col]
                            context[str(col)] = "" if pd.isna(val) else str(val)
                        
                        doc_tpl = DocxTemplate(word_file)
                        doc_tpl.render(context)
                        
                        filename_val = str(row[naming_column]).strip()
                        clean_filename = re.sub(r'[\\/*?:"<>|]', "", filename_val)
                        
                        if is_pdf:
                            # Simpan sementara sebagai docx
                            temp_docx_path = os.path.join(temp_dir, f"temp_{idx}.docx")
                            doc_tpl.save(temp_docx_path)
                            
                            # Konversi docx ke pdf memakai LibreOffice
                            cmd = [
                                "libreoffice",
                                "--headless",
                                "--convert-to", "pdf",
                                temp_docx_path,
                                "--outdir", temp_dir
                            ]
                            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            
                            generated_pdf = os.path.join(temp_dir, f"temp_{idx}.pdf")
                            if os.path.exists(generated_pdf):
                                with open(generated_pdf, "rb") as pdf_file:
                                    pdf_data = pdf_file.read()
                                file_name = f"Surat_{clean_filename}.pdf"
                                zip_file.writestr(file_name, pdf_data)
                                os.remove(generated_pdf)
                            if os.path.exists(temp_docx_path):
                                os.remove(temp_docx_path)
                        else:
                            doc_io = io.BytesIO()
                            doc_tpl.save(doc_io)
                            file_name = f"Surat_{clean_filename}.docx"
                            zip_file.writestr(file_name, doc_io.getvalue())
                        
                        progress_bar.progress((idx + 1) / total_rows)

            status_text.empty()
            progress_bar.empty()
            
            st.success(f"🎉 Berhasil memproses {total_rows} dokumen surat ({output_format})!")
            
            st.download_button(
                label=f"⬇️ Unduh Semua Surat dalam File ZIP ({output_format})",
                data=zip_buffer.getvalue(),
                file_name=f"Hasil_Surat_{'PDF' if is_pdf else 'DOCX'}.zip",
                mime="application/zip",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {str(e)}")

else:
    st.info("💡 **Petunjuk:** Silakan unggah **File Excel** dan **Template Word** pada Langkah 1 untuk memulai.")