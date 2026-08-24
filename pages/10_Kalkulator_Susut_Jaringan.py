import io

import altair as alt
import pandas as pd
import streamlit as st

from module_style import apply_module_style, render_hero_banner, kpi_card

# =============================================================================
# HELPERS
# =============================================================================

REQUIRED_COLUMNS = ["Nama Feeder", "Periode", "Energi Kirim (kWh)", "Energi Terjual (kWh)"]


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).replace("\xa0", "").strip() for c in df.columns]
    return df


def hitung_susut(energi_kirim: float, energi_terjual: float, target_persen: float) -> dict:
    susut_kwh = energi_kirim - energi_terjual
    susut_persen = (susut_kwh / energi_kirim * 100) if energi_kirim > 0 else 0.0

    susut_teknis_estimasi = (target_persen / 100) * energi_kirim
    susut_non_teknis = max(susut_kwh - susut_teknis_estimasi, 0.0)

    status = "🟢 Dalam Batas Target" if susut_persen <= target_persen else "🔴 Di Atas Target — Perlu Investigasi"

    return {
        "susut_kwh": susut_kwh,
        "susut_persen": susut_persen,
        "susut_teknis_estimasi": susut_teknis_estimasi,
        "susut_non_teknis": susut_non_teknis,
        "status": status,
    }


def process_bulk(df: pd.DataFrame, target_persen: float) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        hasil = hitung_susut(row["Energi Kirim (kWh)"], row["Energi Terjual (kWh)"], target_persen)
        rows.append(
            {
                "Nama Feeder": row["Nama Feeder"],
                "Periode": row["Periode"],
                "Energi Kirim (kWh)": row["Energi Kirim (kWh)"],
                "Energi Terjual (kWh)": row["Energi Terjual (kWh)"],
                "Susut (kWh)": round(hasil["susut_kwh"], 1),
                "Susut (%)": round(hasil["susut_persen"], 2),
                "Estimasi Non-Teknis (kWh)": round(hasil["susut_non_teknis"], 1),
                "Status": hasil["status"],
            }
        )
    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        result_df = result_df.sort_values("Susut (%)", ascending=False).reset_index(drop=True)
    return result_df


def style_result(df: pd.DataFrame):
    def highlight(val):
        if "🔴" in str(val):
            return "background-color: rgba(239, 68, 68, 0.18); color: #fecaca; font-weight: 700;"
        return "color: #86efac;"

    styler = df.style
    style_fn = getattr(styler, "map", None) or styler.applymap
    return style_fn(highlight, subset=["Status"])


def build_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Rekap Susut Jaringan", index=False)
    return buffer.getvalue()


def build_bar_chart(df: pd.DataFrame, target_persen: float):
    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Nama Feeder:N", sort="-y", title=None),
            y=alt.Y("Susut (%):Q", title="Susut (%)"),
            color=alt.condition(
                alt.datum["Susut (%)"] > target_persen,
                alt.value("#ef4444"),
                alt.value("#38bdf8"),
            ),
            tooltip=["Nama Feeder", "Periode", "Susut (%)", "Status"],
        )
    )
    target_rule = (
        alt.Chart(pd.DataFrame({"y": [target_persen]}))
        .mark_rule(color="#facc15", strokeDash=[4, 4])
        .encode(y="y:Q")
    )
    return (bars + target_rule).properties(height=340)


# =============================================================================
# KONFIGURASI HALAMAN & STYLE
# =============================================================================

st.set_page_config(
    page_title="Kalkulator Susut Jaringan - PLN Platform",
    page_icon="⚡",
    layout="wide",
)

try:
    from auth import check_login, render_logout_button

    check_login()
    render_logout_button()
except ImportError:
    pass

apply_module_style()
render_hero_banner(module_number=10, icon="🕸️", title="Kalkulator Susut Jaringan")

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Susut Jaringan** = selisih antara energi yang dikirim (dari GI/Gardu/Penyulang) dengan energi yang terjual ke pelanggan.
        2. Rumus: `Susut (%) = (Energi Kirim - Energi Terjual) / Energi Kirim × 100%`.
        3. **Target Susut (%)** biasanya mengacu pada standar/benchmark unit kamu (umumnya susut teknis wajar berkisar 8-12%,
           tapi sebaiknya sesuaikan dengan target resmi dari manajemen unit).
        4. Selisih di atas target dianggap **indikasi susut non-teknis** (potensi pencurian, kesalahan catat meter, atau sambungan tidak resmi) —
           bukan kepastian, tapi sinyal untuk diselidiki lebih lanjut.
        5. Gunakan **Input Manual** untuk cek cepat 1 feeder, atau **Upload Excel** untuk analisis banyak feeder/periode sekaligus dan melihat mana yang paling perlu diprioritaskan.
        """
    )

# =============================================================================
# PILIH MODE
# =============================================================================

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">1</span> Pilih Mode Perhitungan</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

mode = st.radio("Mode:", ["✍️ Input Manual (1 Feeder)", "📁 Upload Excel (Banyak Feeder)"], horizontal=True)

st.markdown("<br>", unsafe_allow_html=True)

if mode.startswith("✍️"):
    st.markdown(
        """
        <div class="step-card">
            <div class="step-header">
                <div class="step-title"><span class="step-number">2</span> Data Energi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        nama_feeder = st.text_input("Nama Feeder/Gardu/Unit", value="Feeder A")
        energi_kirim = st.number_input("Energi Kirim (kWh)", min_value=0.0, value=0.0, step=100.0)
    with c2:
        energi_terjual = st.number_input("Energi Terjual (kWh)", min_value=0.0, value=0.0, step=100.0)
    with c3:
        target_persen = st.number_input("Target Susut (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

    if energi_kirim > 0:
        hasil = hitung_susut(energi_kirim, energi_terjual, target_persen)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📊 Hasil Perhitungan")

        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(kpi_card("📉", "Susut Total", f"{hasil['susut_kwh']:,.1f} kWh", f"{hasil['susut_persen']:.2f}%"), unsafe_allow_html=True)
        with k2:
            st.markdown(kpi_card("🔧", "Estimasi Susut Teknis", f"{hasil['susut_teknis_estimasi']:,.1f} kWh", f"berdasar target {target_persen:.1f}%"), unsafe_allow_html=True)
        with k3:
            tone_label = "Perlu Investigasi" if hasil["susut_non_teknis"] > 0 else "Tidak Terindikasi"
            st.markdown(kpi_card("🚨", "Estimasi Non-Teknis", f"{hasil['susut_non_teknis']:,.1f} kWh", tone_label), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if "🔴" in hasil["status"]:
            st.error(f"**{nama_feeder}** — {hasil['status']} (Susut {hasil['susut_persen']:.2f}% vs target {target_persen:.1f}%)")
        else:
            st.success(f"**{nama_feeder}** — {hasil['status']} (Susut {hasil['susut_persen']:.2f}% vs target {target_persen:.1f}%)")
    else:
        st.info("💡 Masukkan nilai Energi Kirim lebih dari 0 untuk melihat hasil perhitungan.")

else:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-header">
                <div class="step-title"><span class="step-number">2</span> Unggah Data & Target</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        uploaded_file = st.file_uploader(
            "Upload Excel/CSV (kolom: Nama Feeder, Periode, Energi Kirim (kWh), Energi Terjual (kWh))",
            type=["xlsx", "xls", "csv"],
        )
    with c2:
        target_persen_bulk = st.number_input("Target Susut (%) untuk semua feeder", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            df = clean_columns(df)

            missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
            if missing:
                st.error("Kolom wajib tidak ditemukan: " + ", ".join(missing))
            else:
                df["Energi Kirim (kWh)"] = pd.to_numeric(df["Energi Kirim (kWh)"], errors="coerce")
                df["Energi Terjual (kWh)"] = pd.to_numeric(df["Energi Terjual (kWh)"], errors="coerce")
                df = df.dropna(subset=["Energi Kirim (kWh)", "Energi Terjual (kWh)"])

                result_df = process_bulk(df, target_persen_bulk)

                if result_df.empty:
                    st.warning("Tidak ada data valid untuk dianalisis.")
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("##### 📊 Ringkasan Keseluruhan")

                    total_feeder = len(result_df)
                    over_target = (result_df["Status"].str.contains("🔴")).sum()
                    total_non_teknis = result_df["Estimasi Non-Teknis (kWh)"].sum()

                    k1, k2, k3 = st.columns(3)
                    with k1:
                        st.markdown(kpi_card("🗂️", "Total Feeder Dianalisis", f"{total_feeder}", "entri"), unsafe_allow_html=True)
                    with k2:
                        st.markdown(kpi_card("🔴", "Di Atas Target", f"{over_target}", "perlu investigasi"), unsafe_allow_html=True)
                    with k3:
                        st.markdown(kpi_card("🚨", "Total Estimasi Non-Teknis", f"{total_non_teknis:,.0f} kWh", "seluruh feeder"), unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        """
                        <div class="step-card">
                            <div class="step-header">
                                <div class="step-title"><span class="step-number">3</span> Rekap & Ranking Feeder</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.dataframe(style_result(result_df), use_container_width=True, hide_index=True)

                    excel_bytes = build_excel_bytes(result_df)
                    st.download_button(
                        "⬇️ UNDUH REKAP (.XLSX)",
                        data=excel_bytes,
                        file_name="Rekap_Susut_Jaringan.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-heading">📈 Grafik Perbandingan Susut per Feeder</div>' if False else "##### 📈 Grafik Perbandingan Susut per Feeder")
                    st.altair_chart(build_bar_chart(result_df, target_persen_bulk), use_container_width=True)
                    st.caption("Garis putus kuning = target susut. Batang merah = di atas target, biru = masih wajar.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")
    else:
        st.info("💡 **Petunjuk:** Unggah file berisi data energi kirim & terjual per feeder untuk memulai analisis.")
