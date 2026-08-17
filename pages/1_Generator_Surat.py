import base64
import io
import os
import re
import shutil
import subprocess
import tempfile
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from docxtpl import DocxTemplate

# =============================================================================
# HELPERS
# =============================================================================

ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|]')
NO_FOLDER_OPTION = "Tanpa Folder (1 Folder Utama)"


def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def sanitize_filename(value: str) -> str:
    """Bersihkan string dari karakter yang tidak boleh ada di nama file/folder."""
    return ILLEGAL_FILENAME_CHARS.sub("", str(value).strip())


def cell_to_text(value) -> str:
    """Konversi nilai sel Excel ke teks yang aman dipakai di surat/nama file."""
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%d-%m-%Y")
    return str(value)


def build_unique_name(base_name: str, folder_path: str, used_names: dict) -> str:
    """Pastikan nama file unik di dalam folder yang sama (hindari saling menimpa)."""
    key = f"{folder_path}{base_name}".lower()
    count = used_names.get(key, 0)
    used_names[key] = count + 1
    return base_name if count == 0 else f"{base_name}_{count + 1}"


def check_libreoffice_available() -> bool:
    return shutil.which("libreoffice") is not None


# =============================================================================
# KONFIGURASI HALAMAN & STYLE
# =============================================================================

logo_path = "logo_pln.png"
logo_base64 = get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""

st.set_page_config(
    page_title="Generator Surat - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide",
)

try:
    from auth import check_login, render_logout_button
    check_login()
    render_logout_button()
except ImportError:
    pass

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

logo_html = (
    f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">'
    if logo_base64
    else "⚡"
)

st.markdown(
    f"""
    <div class="hero-banner">
        <div>{logo_html}</div>
        <div>
            <span class="hero-badge">MODUL 1</span>
            <div class="hero-title">✉️ Generator Surat & Arsip Otomatis</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Upload File Excel**: Pastikan kolom header berada di baris paling atas.
        2. **Upload Template Word**: Gunakan tag `{{ NAMA_KOLOM }}` di dalam file `.docx`.
        3. **Pilihan Folder**: Pilih kolom `TANGGAL` atau `ULP` untuk mengelompokkan hasil ke sub-folder digital di dalam ZIP.
        4. **Output PDF & Cetak**: Cetak dokumen atau unduh hasil pengarsipan ZIP.
        """
    )

# =============================================================================
# STEP 1 — UPLOAD
# =============================================================================

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title">
                <span class="step-number">1</span> Unggah Sumber Data & Template
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 Data Excel Target (`.xlsx`)**")
    excel_file = st.file_uploader("Pilih file excel", type=["xlsx", "xls"], key="excel_uploader")

with col2:
    st.markdown("**📝 Template Surat (`.docx`)**")
    word_file = st.file_uploader("Pilih template word", type=["docx"], key="word_uploader")


def render_summary_cards(df: pd.DataFrame) -> None:
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Surat Dicetak</div>
                <div class="stat-value">{len(df)} Dokumen</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Variabel Kolom Excel</div>
                <div class="stat-value">{len(df.columns)} Kolom</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-label">Status File Template</div>
                <div class="stat-value" style="color:#4ade80;">Ready ✓</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_options(df: pd.DataFrame):
    st.markdown(
        """
        <div class="step-card">
            <div class="step-header">
                <div class="step-title">
                    <span class="step-number">2</span> Pengaturan File & Pengarsipan
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    c_opt1, c_opt2, c_opt3 = st.columns(3)

    with c_opt1:
        naming_column = st.selectbox(
            "Penamaan File Berdasarkan:",
            options=df.columns.tolist(),
            index=0,
        )

    with c_opt2:
        options_folder = [NO_FOLDER_OPTION] + df.columns.tolist()
        folder_column = st.selectbox(
            "Pengelompokan Sub-Folder (ZIP):",
            options=options_folder,
            index=0,
            help="Pilih kolom TANGGAL atau ULP untuk membagi file ke sub-folder otomatis.",
        )

    with c_opt3:
        output_format = st.radio(
            "Format File Keluaran:",
            options=["DOCX (Word)", "PDF Format"],
            horizontal=True,
        )

    return naming_column, folder_column, output_format


def render_docx_batch(df: pd.DataFrame, template_bytes: bytes, naming_column: str, folder_column: str, temp_dir: str):
    documents = []
    used_names: dict = {}
    total_rows = len(df)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, row in df.iterrows():
        status_text.text(f"⏳ Merender surat {idx + 1} dari {total_rows}...")

        context = {str(col): cell_to_text(row[col]) for col in df.columns}

        doc_tpl = DocxTemplate(io.BytesIO(template_bytes))
        doc_tpl.render(context)

        raw_name = cell_to_text(row[naming_column])
        clean_filename = sanitize_filename(raw_name) or f"Baris_{idx + 1}"

        folder_path = ""
        if folder_column != NO_FOLDER_OPTION:
            raw_folder_val = cell_to_text(row[folder_column])
            clean_folder_name = sanitize_filename(raw_folder_val)
            if clean_folder_name:
                folder_path = f"{clean_folder_name}/"

        final_name = build_unique_name(clean_filename, folder_path, used_names)

        temp_docx_path = os.path.join(temp_dir, f"doc_{idx:04d}.docx")
        doc_tpl.save(temp_docx_path)

        documents.append(
            {
                "temp_docx_path": temp_docx_path,
                "folder_path": folder_path,
                "final_name": final_name,
            }
        )
        progress_bar.progress((idx + 1) / total_rows * 0.6)

    status_text.empty()
    progress_bar.empty()
    return documents


def convert_batch_to_pdf(documents: list, temp_dir: str) -> None:
    docx_paths = [doc["temp_docx_path"] for doc in documents]
    if not docx_paths:
        return

    cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", temp_dir] + docx_paths
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise RuntimeError(
            "Konversi PDF gagal. Detail: " + result.stderr.decode(errors="ignore")[:500]
        )


def build_zip_archive(documents: list, is_pdf: bool) -> bytes:
    zip_buffer = io.BytesIO()
    ext = "pdf" if is_pdf else "docx"

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for doc in documents:
            source_path = doc["temp_docx_path"]
            if is_pdf:
                source_path = os.path.splitext(source_path)[0] + ".pdf"
                if not os.path.exists(source_path):
                    continue

            with open(source_path, "rb") as f:
                data = f.read()
            zip_file.writestr(f"{doc['folder_path']}Surat_{doc['final_name']}.{ext}", data)

    return zip_buffer.getvalue()


# =============================================================================
# ALUR UTAMA
# =============================================================================

if excel_file and word_file:
    try:
        df = pd.read_excel(excel_file)
        df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x) if col.dtype == "object" else col)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📈 Ringkasan Data Rencana Cetak")
        render_summary_cards(df)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📋 Pratinjau Data Excel:")
        st.dataframe(df.head(5), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        naming_column, folder_column, output_format = render_options(df)
        is_pdf = "PDF" in output_format

        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("⚡ MULAI PROSES GENERATE SURAT", type="primary", use_container_width=True)

        if generate_btn:
            template_bytes = word_file.getvalue()

            with tempfile.TemporaryDirectory() as temp_dir:
                documents = render_docx_batch(df, template_bytes, naming_column, folder_column, temp_dir)

                has_pdf = False
                if is_pdf and check_libreoffice_available():
                    try:
                        status_text = st.empty()
                        status_text.text("⏳ Mengonversi seluruh dokumen ke PDF...")
                        convert_batch_to_pdf(documents, temp_dir)
                        status_text.empty()
                        has_pdf = True
                    except Exception as e:
                        st.warning(f"Gagal mengonversi PDF: {str(e)}")

                zip_bytes = build_zip_archive(documents, is_pdf and has_pdf)

                first_pdf_b64 = None
                first_pdf_bytes = None
                first_pdf_name = "Sampel_Surat_1.pdf"
                if has_pdf and len(documents) > 0:
                    pdf_path = os.path.splitext(documents[0]["temp_docx_path"])[0] + ".pdf"
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            first_pdf_bytes = f.read()
                            first_pdf_b64 = base64.b64encode(first_pdf_bytes).decode("utf-8")
                        first_pdf_name = f"Surat_{documents[0]['final_name']}.pdf"

            st.toast("🎉 Semua surat berhasil dibuat!", icon="⚡")
            st.success(f"🎉 Selesai! Berhasil memproses **{len(documents)} surat** secara otomatis.")

            if first_pdf_b64:
                col_dl1, col_dl2, col_print = st.columns(3)
            else:
                col_dl1, col_dl2 = st.columns(2)
                col_print = None

            with col_dl1:
                st.download_button(
                    label="⬇️ UNDUH SEMUA SURAT (.ZIP)",
                    data=zip_bytes,
                    file_name=f"Arsip_Surat_PLN_{'PDF' if is_pdf and has_pdf else 'DOCX'}.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

            with col_dl2:
                if first_pdf_bytes:
                    st.download_button(
                        label="📄 UNDUH SAMPEL PDF",
                        data=first_pdf_bytes,
                        file_name=first_pdf_name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.info("💡 Pilih **PDF Format** untuk mengaktifkan cetak.")

            if col_print and first_pdf_b64:
                with col_print:
                    print_component = f"""
                    <div style="width: 100%;">
                        <button onclick="cetakPDF()" style="
                            width: 100%;
                            background: linear-gradient(135deg, #059669 0%, #047857 100%);
                            color: white;
                            font-weight: 700;
                            border: none;
                            border-radius: 10px;
                            padding: 0.75rem 1rem;
                            cursor: pointer;
                            font-family: 'Plus Jakarta Sans', sans-serif;
                            font-size: 14px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: 8px;
                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        ">
                            🖨️ CETAK SEKARANG (CTRL + P)
                        </button>
                    </div>

                    <script>
                    function cetakPDF() {{
                        const base64Data = '{first_pdf_b64}';
                        const byteCharacters = atob(base64Data);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {{
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }}
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], {{type: 'application/pdf'}});
                        const fileURL = URL.createObjectURL(blob);
                        
                        // Buka PDF di jendela baru lalu buka dialog cetak
                        const printWindow = window.open(fileURL, '_blank');
                        if (printWindow) {{
                            printWindow.focus();
                        }} else {{
                            alert('Mohon izinkan pop-up di browser kamu untuk membuka jendela cetak!');
                        }}
                    }}
                    </script>
                    """
                    components.html(print_component, height=55)

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan sistem: {str(e)}")

else:
    st.info("💡 **Petunjuk:** Silakan unggah **File Excel** dan **Template Word** di atas untuk membuka panel pengaturan.")