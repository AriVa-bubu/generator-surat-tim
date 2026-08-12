import base64
import io
import os

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# =============================================================================
# HELPERS
# =============================================================================

def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Bersihkan nama kolom dari spasi/non-breaking-space bawaan export AP2T."""
    df.columns = [str(c).replace("\xa0", "").strip() for c in df.columns]
    return df


def normalize_idpel(value) -> str:
    if pd.isna(value):
        return None
    s = str(value).strip().lstrip("'\"")
    if s.endswith(".0"):
        s = s[:-2]
    return s


REQUIRED_COLUMNS = ["IDPEL", "BLTH REK", "SLALWBP", "SAHLWBP", "PEMKWH"]


def load_and_prepare(uploaded_file) -> pd.DataFrame:
    """Baca semua sheet (bisa multi-pelanggan), gabungkan, dan siapkan kolom analisis."""
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    frames = []
    for sheet_name, sheet_df in sheets.items():
        sheet_df = clean_columns(sheet_df.copy())
        if not all(col in sheet_df.columns for col in REQUIRED_COLUMNS):
            continue  # lewati sheet yang bukan format DPP
        frames.append(sheet_df)

    if not frames:
        raise ValueError(
            "Tidak ada sheet dengan format DPP yang valid. Pastikan ada kolom: "
            + ", ".join(REQUIRED_COLUMNS)
        )

    df = pd.concat(frames, ignore_index=True)
    df["IDPEL"] = df["IDPEL"].apply(normalize_idpel)
    df = df[df["IDPEL"].notna()].copy()

    df["BLTH REK"] = pd.to_datetime(df["BLTH REK"], errors="coerce")
    df = df[df["BLTH REK"].notna()].copy()

    for col in ["SLALWBP", "SAHLWBP", "PEMKWH"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["IDPEL", "BLTH REK"]).reset_index(drop=True)

    # Deteksi utama: stand sekarang == stand bulan lalu -> meter tidak bergerak
    df["MACET"] = (
        df["SLALWBP"].notna()
        & df["SAHLWBP"].notna()
        & np.isclose(df["SLALWBP"], df["SAHLWBP"])
    )

    # Hitung streak (durasi berturut-turut) per IDPEL
    df["streak_id"] = (
        df["MACET"] != df.groupby("IDPEL")["MACET"].shift()
    ).groupby(df["IDPEL"]).cumsum()
    df["streak_len"] = df.groupby(["IDPEL", "streak_id"])["MACET"].transform("size")

    return df


def summarize_per_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Rekap status kWh macet per IDPEL, fokus ke jendela 6 bulan terakhir."""
    rows = []

    for idpel, g in df.groupby("IDPEL"):
        g = g.sort_values("BLTH REK")
        last_row = g.iloc[-1]
        last_date = last_row["BLTH REK"]
        window_start = last_date - pd.DateOffset(months=5)
        window = g[g["BLTH REK"] >= window_start]

        is_macet_now = bool(last_row["MACET"])
        current_streak = int(last_row["streak_len"]) if is_macet_now else 0
        longest_streak = int(g.loc[g["MACET"], "streak_len"].max()) if g["MACET"].any() else 0

        normal_usage = g.loc[~g["MACET"], "PEMKWH"].mean()
        normal_usage = 0 if pd.isna(normal_usage) else normal_usage

        macet_window = window[window["MACET"]]
        bulan_macet_6bln = len(macet_window)
        estimasi_hilang = float(
            (normal_usage - macet_window["PEMKWH"].fillna(0)).clip(lower=0).sum()
        )

        if is_macet_now and current_streak >= 1:
            status = "🔴 Macet (berlanjut)"
        elif bulan_macet_6bln > 0:
            status = "🟠 Pernah macet, sudah normal"
        else:
            status = "🟢 Normal"

        rows.append(
            {
                "IDPEL": idpel,
                "Bulan Terakhir": last_date.strftime("%b %Y"),
                "Status Sekarang": status,
                "Bulan Macet (6 Bln Terakhir)": bulan_macet_6bln,
                "Durasi Macet Terpanjang (Riwayat)": longest_streak,
                "Rata-rata Pemakaian Normal (kWh)": round(normal_usage, 1),
                "Estimasi kWh Hilang (6 Bln)": round(estimasi_hilang, 1),
            }
        )

    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values(
            ["Bulan Macet (6 Bln Terakhir)", "Estimasi kWh Hilang (6 Bln)"],
            ascending=False,
        ).reset_index(drop=True)
    return summary


def style_summary(summary: pd.DataFrame):
    def highlight_status(val):
        if "🔴" in str(val):
            return "background-color: rgba(239, 68, 68, 0.18); color: #fecaca; font-weight: 700;"
        if "🟠" in str(val):
            return "background-color: rgba(251, 191, 36, 0.15); color: #fde68a; font-weight: 700;"
        return "color: #86efac;"

    styler = summary.style
    style_fn = getattr(styler, "map", None) or styler.applymap
    return style_fn(highlight_status, subset=["Status Sekarang"])


def build_customer_chart(g: pd.DataFrame):
    chart_df = g[["BLTH REK", "PEMKWH", "MACET"]].copy()
    chart_df["Kondisi"] = chart_df["MACET"].map({True: "Macet", False: "Normal"})

    line = (
        alt.Chart(chart_df)
        .mark_line(color="#38bdf8")
        .encode(x=alt.X("BLTH REK:T", title="Bulan"), y=alt.Y("PEMKWH:Q", title="Pemakaian (kWh)"))
    )
    points = (
        alt.Chart(chart_df)
        .mark_circle(size=90)
        .encode(
            x="BLTH REK:T",
            y="PEMKWH:Q",
            color=alt.Color(
                "Kondisi:N",
                scale=alt.Scale(domain=["Normal", "Macet"], range=["#38bdf8", "#ef4444"]),
                legend=alt.Legend(title=None),
            ),
            tooltip=["BLTH REK:T", "PEMKWH:Q", "Kondisi:N"],
        )
    )
    return (line + points).properties(height=320)


def build_excel_bytes(summary: pd.DataFrame, detail: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Rekap Status", index=False)
        detail.to_excel(writer, sheet_name="Detail Per Bulan", index=False)
    return buffer.getvalue()


def kpi_card(icon: str, label: str, value: str, delta: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <span class="kpi-delta">{delta}</span>
    </div>
    """


# =============================================================================
# KONFIGURASI HALAMAN & STYLE
# =============================================================================

logo_path = "logo_pln.png"
logo_base64 = get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""

st.set_page_config(
    page_title="Deteksi kWh Macet - PLN Platform",
    page_icon=logo_path if os.path.exists(logo_path) else "⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }

        .hero-banner {
            background: linear-gradient(135deg, #0b2545 0%, #134074 60%, #00a8e8 100%);
            border-radius: 16px; padding: 24px 28px; color: white; margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 168, 232, 0.2);
            display: flex; align-items: center; gap: 20px;
        }
        .hero-logo-img { width: 70px; height: auto; border-radius: 8px; background: white; padding: 4px; }
        .hero-badge {
            background-color: #ffb703; color: #000; font-weight: 800; font-size: 0.75rem;
            padding: 4px 12px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 6px;
        }
        .hero-title { font-size: 1.8rem; font-weight: 800; margin: 0; }

        .step-card {
            background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 22px; margin-bottom: 20px;
        }
        .step-header {
            display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
            border-bottom: 1px solid #334155; padding-bottom: 10px;
        }
        .step-title { font-size: 1.15rem; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 10px; }
        .step-number {
            background: linear-gradient(135deg, #0284c7, #0369a1); color: white; font-size: 0.85rem; font-weight: 700;
            width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
        }

        .kpi-card {
            background: linear-gradient(160deg, #1e293b 0%, #172033 100%); border: 1px solid #2b3a52;
            border-radius: 16px; padding: 18px 20px; height: 100%;
        }
        .kpi-icon { font-size: 1.4rem; margin-bottom: 8px; display: inline-block; }
        .kpi-label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em; }
        .kpi-value { font-size: 1.55rem; font-weight: 800; color: #f8fafc; margin: 4px 0 8px 0; }
        .kpi-delta {
            display: inline-flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 700;
            color: #94a3b8; background: rgba(148, 163, 184, 0.12); padding: 3px 9px; border-radius: 999px;
        }

        div[data-testid="stFileUploader"] {
            background-color: #1e293b; border: 1px dashed #475569; border-radius: 12px; padding: 8px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; border: none !important;
            border-radius: 10px !important; font-weight: 700 !important; padding: 0.75rem 1.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

logo_html = (
    f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">' if logo_base64 else "⚡"
)

st.markdown(
    f"""
    <div class="hero-banner">
        <div>{logo_html}</div>
        <div>
            <span class="hero-badge">MODUL 6</span>
            <div class="hero-title">🔎 Deteksi kWh Macet</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Upload File Excel DPP** dari AP2T — boleh berisi 1 sheet (1 pelanggan) atau banyak sheet (banyak pelanggan sekaligus).
        2. Kolom wajib ada: `IDPEL`, `BLTH REK`, `SLALWBP`, `SAHLWBP`, `PEMKWH`.
        3. Sistem membandingkan **stand meter bulan ini vs bulan lalu** (bukan cuma cek pemakaian 0 kWh),
           karena kadang sistem tetap menagih pakai rata-rata walau meternya macet.
        4. Hasil ditampilkan sebagai rekap status per pelanggan (fokus 6 bulan terakhir), grafik tren, dan bisa diunduh sebagai Excel.
        """
    )

# =============================================================================
# UPLOAD & PROSES
# =============================================================================

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">1</span> Unggah Data DPP</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Pilih file Excel DPP (.xlsx)", type=["xlsx", "xls"], key="dpp_uploader")

if uploaded_file:
    try:
        df = load_and_prepare(uploaded_file)
        summary = summarize_per_customer(df)

        if summary.empty:
            st.warning("Tidak ada data pelanggan yang bisa dianalisis dari file ini.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📊 Ringkasan Keseluruhan")

            total_pelanggan = len(summary)
            macet_berlanjut = (summary["Status Sekarang"] == "🔴 Macet (berlanjut)").sum()
            total_estimasi = summary["Estimasi kWh Hilang (6 Bln)"].sum()

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(kpi_card("👥", "Total Pelanggan Dianalisis", f"{total_pelanggan}", "IDPEL"), unsafe_allow_html=True)
            with k2:
                st.markdown(
                    kpi_card("🔴", "Sedang Macet Berlanjut", f"{macet_berlanjut}", "Perlu ditindaklanjuti"),
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    kpi_card("⚡", "Estimasi kWh Hilang (6 Bln)", f"{total_estimasi:,.0f} kWh", "Seluruh pelanggan"),
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-title"><span class="step-number">2</span> Rekap Status Per Pelanggan</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.dataframe(style_summary(summary), use_container_width=True, hide_index=True)

            excel_bytes = build_excel_bytes(summary, df.drop(columns=["streak_id"]))
            st.download_button(
                "⬇️ UNDUH REKAP (.XLSX)",
                data=excel_bytes,
                file_name="Rekap_Deteksi_KWH_Macet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-title"><span class="step-number">3</span> Detail Tren Per Pelanggan</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            selected_idpel = st.selectbox("Pilih IDPEL untuk lihat detail:", summary["IDPEL"].tolist())
            customer_df = df[df["IDPEL"] == selected_idpel].sort_values("BLTH REK")

            st.altair_chart(build_customer_chart(customer_df), use_container_width=True)
            st.caption("🔴 Titik merah = bulan terdeteksi macet (stand meter tidak bergerak).")

            with st.expander("📋 Lihat data mentah bulan-per-bulan pelanggan ini"):
                st.dataframe(
                    customer_df[["BLTH REK", "SLALWBP", "SAHLWBP", "PEMKWH", "MACET"]],
                    use_container_width=True,
                    hide_index=True,
                )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")

else:
    st.info("💡 **Petunjuk:** Silakan unggah file Excel DPP di atas untuk memulai analisis.")