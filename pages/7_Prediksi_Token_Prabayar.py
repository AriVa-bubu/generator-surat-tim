import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st

# =============================================================================
# HELPERS
# =============================================================================



COLUMN_ALIASES = {
    "Nomer Meter": ["nomer meter", "no meter", "nomor meter", "no. meter"],
    "Token": ["token"],
    "Pem kWh": ["pem kwh", "kwh", "jumlah kwh", "pembelian kwh"],
    "Tarif": ["tarif"],
    "Daya": ["daya"],
    "Tanggal Bayar": ["tanggal bayar", "tgl bayar", "tanggal transaksi", "tgl transaksi"],
}
REQUIRED_CANONICAL = ["Nomer Meter", "Pem kWh", "Tanggal Bayar"]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).replace("\xa0", "").strip() for c in df.columns]
    lower_map = {c.lower().strip(): c for c in df.columns}

    rename_map = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in [canonical.lower()] + aliases:
            if alias in lower_map:
                rename_map[lower_map[alias]] = canonical
                break

    df = df.rename(columns=rename_map)

    missing = [c for c in REQUIRED_CANONICAL if c not in df.columns]
    if missing:
        raise ValueError(
            "Kolom wajib tidak ditemukan: " + ", ".join(missing)
            + ". Pastikan file punya kolom Nomer Meter, Pem kWh, dan Tanggal Bayar."
        )
    return df


def load_token_history(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        raw = pd.read_csv(uploaded_file)
        df = standardize_columns(raw)
    else:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)
        frames = []
        for _, sheet_df in sheets.items():
            try:
                frames.append(standardize_columns(sheet_df))
            except ValueError:
                continue
        if not frames:
            raise ValueError("Tidak ada sheet dengan format riwayat token yang valid.")
        df = pd.concat(frames, ignore_index=True)

    df["Nomer Meter"] = df["Nomer Meter"].astype(str).str.strip()
    df["Pem kWh"] = pd.to_numeric(df["Pem kWh"], errors="coerce")
    df["Tanggal Bayar"] = pd.to_datetime(df["Tanggal Bayar"], errors="coerce")

    df = df.dropna(subset=["Nomer Meter", "Pem kWh", "Tanggal Bayar"])
    df = df.sort_values(["Nomer Meter", "Tanggal Bayar"]).reset_index(drop=True)
    return df


def compute_daily_rate(meter_df: pd.DataFrame, window_days: int | None) -> tuple[float, dt.datetime]:
    """Rata-rata kWh terjual per hari = total kWh dibeli / lama rentang, dalam window tertentu."""
    last_date = meter_df["Tanggal Bayar"].max()

    if window_days is not None:
        start_window = last_date - pd.Timedelta(days=window_days)
        window_df = meter_df[meter_df["Tanggal Bayar"] >= start_window]
        span_days = window_days
    else:
        window_df = meter_df
        span_days = max((last_date - meter_df["Tanggal Bayar"].min()).days, 1)

    total_kwh = window_df["Pem kWh"].sum()
    rate = total_kwh / span_days if span_days > 0 else 0.0
    return round(rate, 3), last_date


def estimate_current_balance(meter_df: pd.DataFrame, daily_rate: float, as_of: dt.datetime) -> float:
    """Estimasi saldo sekarang = kWh pembelian terakhir dikurangi pemakaian sejak tanggal beli terakhir."""
    last_row = meter_df.iloc[-1]
    days_since = max((as_of - last_row["Tanggal Bayar"]).days, 0)
    balance = last_row["Pem kWh"] - daily_rate * days_since
    return max(round(balance, 1), 0.0)


def build_projection(current_balance: float, daily_rate: float, start_date: dt.date, end_date: dt.date, ref_date: dt.date) -> pd.DataFrame:
    dates = pd.date_range(start_date, end_date, freq="D")
    days_from_ref = [(d.date() - ref_date).days for d in dates]
    balances = [max(current_balance - daily_rate * d, 0.0) for d in days_from_ref]
    return pd.DataFrame({"Tanggal": dates, "Perkiraan Sisa Token (kWh)": balances})


def estimate_depletion_date(current_balance: float, daily_rate: float, ref_date: dt.date):
    if daily_rate <= 0:
        return None
    days_left = current_balance / daily_rate
    return ref_date + dt.timedelta(days=int(days_left))


def build_projection_chart(proj_df: pd.DataFrame, depletion_date):
    line = (
        alt.Chart(proj_df)
        .mark_line(color="#38bdf8")
        .encode(x=alt.X("Tanggal:T", title="Tanggal"), y=alt.Y("Perkiraan Sisa Token (kWh):Q", title="Sisa Token (kWh)"))
    )
    zero_rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#ef4444", strokeDash=[4, 4]).encode(y="y:Q")

    layers = [line, zero_rule]
    if depletion_date is not None:
        marker_df = pd.DataFrame({"Tanggal": [pd.Timestamp(depletion_date)], "y": [0]})
        point = (
            alt.Chart(marker_df)
            .mark_point(size=120, color="#ef4444", filled=True)
            .encode(x="Tanggal:T", y="y:Q")
        )
        layers.append(point)

    return alt.layer(*layers).properties(height=320)


from module_style import apply_module_style, render_hero_banner, kpi_card

# =============================================================================
# KONFIGURASI HALAMAN & STYLE
# =============================================================================

st.set_page_config(
    page_title="Prediksi Token Prabayar - PLN Platform",
    page_icon="⚡",
    layout="wide",
)

apply_module_style()
render_hero_banner(module_number=7, icon="🔋", title="Prediksi Sisa Token Prabayar")

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Upload riwayat pembelian token** (Excel/CSV) dari menu Info Prepaid → Transaksi Pembelian Token di AP2T.
        2. Kolom wajib: `Nomer Meter`, `Pem kWh`, `Tanggal Bayar`. Kolom `Token`, `Tarif`, `Daya` opsional.
        3. Sistem menghitung **rata-rata pemakaian per hari** dari total kWh yang dibeli dibagi jangka waktu (bukan dari pembacaan stand, karena meter prabayar tidak punya kolom pemakaian bulanan).
        4. Pilih rentang tanggal untuk melihat **proyeksi sisa token** ke depan, dan sistem akan memperkirakan kapan token diperkirakan habis.
        5. Kalau kamu tahu sisa saldo sebenarnya saat ini (dari cek meter langsung), masukkan manual di kolom "Sisa Token Saat Ini" supaya prediksi lebih akurat.
        """
    )

# =============================================================================
# UPLOAD & PROSES
# =============================================================================

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">1</span> Unggah Riwayat Pembelian Token</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Pilih file Excel/CSV riwayat token", type=["xlsx", "xls", "csv"], key="token_uploader")

if uploaded_file:
    try:
        df = load_token_history(uploaded_file)

        if df.empty:
            st.warning("Tidak ada data transaksi token yang valid di file ini.")
        else:
            meters = df["Nomer Meter"].unique().tolist()
            selected_meter = meters[0] if len(meters) == 1 else st.selectbox("Pilih Nomer Meter:", meters)
            meter_df = df[df["Nomer Meter"] == selected_meter].sort_values("Tanggal Bayar")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-title"><span class="step-number">2</span> Pengaturan Prediksi</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                window_option = st.selectbox(
                    "Hitung rata-rata pemakaian dari:",
                    ["30 Hari Terakhir", "60 Hari Terakhir", "90 Hari Terakhir", "180 Hari Terakhir", "Seluruh Riwayat"],
                    index=2,
                )
            window_map = {
                "30 Hari Terakhir": 30,
                "60 Hari Terakhir": 60,
                "90 Hari Terakhir": 90,
                "180 Hari Terakhir": 180,
                "Seluruh Riwayat": None,
            }
            daily_rate, last_purchase_date = compute_daily_rate(meter_df, window_map[window_option])
            today = dt.date.today()

            est_balance = estimate_current_balance(meter_df, daily_rate, pd.Timestamp(today))

            with c2:
                current_balance = st.number_input(
                    "Sisa Token Saat Ini (kWh) — kosongkan/pakai estimasi jika tidak tahu pastinya:",
                    min_value=0.0,
                    value=float(est_balance),
                    step=1.0,
                    help="Default dihitung otomatis dari pembelian terakhir dikurangi estimasi pemakaian sampai hari ini.",
                )

            date_range = st.date_input(
                "Pilih rentang tanggal untuk proyeksi:",
                value=(today, today + dt.timedelta(days=30)),
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = today, today + dt.timedelta(days=30)

            depletion_date = estimate_depletion_date(current_balance, daily_rate, today)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 📊 Hasil Prediksi")

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(
                    kpi_card("📈", "Rata-rata Pemakaian/Hari", f"{daily_rate:.2f} kWh", window_option),
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    kpi_card("🔋", "Estimasi Sisa Token Hari Ini", f"{current_balance:.1f} kWh", f"per {today.strftime('%d %b %Y')}"),
                    unsafe_allow_html=True,
                )
            with k3:
                depletion_label = depletion_date.strftime("%d %b %Y") if depletion_date else "Tidak dapat diprediksi"
                st.markdown(
                    kpi_card("⚠️", "Perkiraan Token Habis", depletion_label, "Estimasi tanggal"),
                    unsafe_allow_html=True,
                )

            if depletion_date and start_date <= depletion_date <= end_date:
                st.warning(
                    f"⚠️ Berdasarkan pola pemakaian saat ini, token diperkirakan **habis pada {depletion_date.strftime('%d %B %Y')}**, "
                    "yaitu dalam rentang tanggal yang kamu pilih."
                )
            elif depletion_date and depletion_date < start_date:
                st.error(
                    f"🔴 Token diperkirakan **sudah habis sejak {depletion_date.strftime('%d %B %Y')}** — sebelum rentang tanggal yang dipilih. "
                    "Kemungkinan pelanggan sudah membeli token baru yang belum tercatat di data ini."
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-title"><span class="step-number">3</span> Grafik Proyeksi Sisa Token</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            proj_df = build_projection(current_balance, daily_rate, start_date, end_date, today)
            st.altair_chart(build_projection_chart(proj_df, depletion_date), use_container_width=True)
            st.caption("Garis putus merah menandai titik saldo nol. Titik merah = perkiraan tanggal token habis (jika masuk rentang chart).")

            with st.expander("📋 Lihat tabel proyeksi harian"):
                st.dataframe(proj_df, use_container_width=True, hide_index=True)

            with st.expander("🧾 Lihat riwayat pembelian token meter ini"):
                st.dataframe(
                    meter_df[[c for c in ["Tanggal Bayar", "Token", "Pem kWh", "Tarif", "Daya"] if c in meter_df.columns]],
                    use_container_width=True,
                    hide_index=True,
                )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")

else:
    st.info("💡 **Petunjuk:** Silakan unggah file riwayat pembelian token di atas untuk memulai prediksi.")