import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st

try:
    from module_style import apply_module_style, kpi_card, render_hero_banner
except ImportError:

    def apply_module_style():
        pass

    def render_hero_banner(module_number, icon, title):
        st.title(f"{icon} Modul {module_number}: {title}")

    def kpi_card(icon, label, value, subtext):
        return f"""
        <div style="background-color:#1e293b; padding:15px; border-radius:10px; text-align:center;">
            <div style="font-size:24px;">{icon}</div>
            <div style="color:#94a3b8; font-size:12px;">{label}</div>
            <div style="color:#f8fafc; font-size:20px; font-weight:bold;">{value}</div>
            <div style="color:#64748b; font-size:11px;">{subtext}</div>
        </div>
        """


# =============================================================================
# HELPERS & PARSER FILE
# =============================================================================

COLUMN_ALIASES = {
    "Nomer Meter": [
        "nomer meter",
        "no meter",
        "nomor meter",
        "no. meter",
        "nokwh",
        "no kwh",
        "idpel",
    ],
    "Token": ["token"],
    "Pem kWh": ["pem kwh", "kwh", "jumlah kwh", "pembelian kwh", "pemkwh"],
    "Tarif": ["tarif", "tarip"],
    "Daya": ["daya"],
    "Tanggal Bayar": [
        "tanggal bayar",
        "tgl bayar",
        "tanggal transaksi",
        "tgl transaksi",
        "tglbayar",
    ],
}
REQUIRED_CANONICAL = ["Nomer Meter", "Pem kWh", "Tanggal Bayar"]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).replace("\xa0", "").strip() for c in df.columns]
    lower_map = {c.lower(): c for c in df.columns}

    rename_map = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in [canonical.lower()] + aliases:
            if alias in lower_map:
                rename_map[lower_map[alias]] = canonical
                break

    df = df.rename(columns=rename_map)

    missing = [c for c in REQUIRED_CANONICAL if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")
    return df


def load_token_history(uploaded_file) -> pd.DataFrame:
    uploaded_file.seek(0)

    if uploaded_file.name.lower().endswith(".csv"):
        raw = pd.read_csv(uploaded_file)
        df = standardize_columns(raw)
    else:
        excel_file = pd.ExcelFile(uploaded_file)
        frames = []
        for sheet_name in excel_file.sheet_names:
            sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
            try:
                std_df = standardize_columns(sheet_df)
                frames.append(std_df)
            except ValueError:
                continue

        if not frames:
            raise ValueError(
                "Tidak ada sheet dengan format riwayat token yang valid."
            )
        df = pd.concat(frames, ignore_index=True)

    df["Nomer Meter"] = (
        df["Nomer Meter"]
        .astype(str)
        .str.replace(",", "")
        .str.replace(".0", "", regex=False)
        .str.strip()
    )
    df["Pem kWh"] = pd.to_numeric(df["Pem kWh"], errors="coerce")
    df["Tanggal Bayar"] = pd.to_datetime(df["Tanggal Bayar"], errors="coerce")

    df = df.dropna(subset=["Nomer Meter", "Pem kWh", "Tanggal Bayar"])
    df = df.sort_values(["Nomer Meter", "Tanggal Bayar"]).reset_index(drop=True)
    return df


def compute_daily_rate_pln(
    meter_df: pd.DataFrame, window_days: int | None
) -> tuple[float, dt.datetime]:
    """Menghitung rata-rata harian berbasis standar PLN (Total kWh / Rentang Hari Real)."""
    last_date = meter_df["Tanggal Bayar"].max()

    if window_days is not None:
        start_window = last_date - pd.Timedelta(days=window_days)
        window_df = meter_df[meter_df["Tanggal Bayar"] >= start_window]
    else:
        window_df = meter_df

    if len(window_df) > 1:
        first_trx = window_df["Tanggal Bayar"].min()
        last_trx = window_df["Tanggal Bayar"].max()
        # Menggunakan selisih hari nyata antar transaksi awal dan akhir
        span_days = max((last_trx - first_trx).days, 1)
        # Pada metode transaksi interval, kWh transaksi pertama dianggap deposit awal
        total_kwh = window_df["Pem kWh"].iloc[1:].sum() if len(window_df) > 1 else window_df["Pem kWh"].sum()
    else:
        span_days = 30
        total_kwh = window_df["Pem kWh"].sum()

    rate = total_kwh / span_days if span_days > 0 else 0.0
    return round(rate, 3), last_date


def estimate_current_balance(
    meter_df: pd.DataFrame, daily_rate: float, as_of: dt.datetime
) -> float:
    last_row = meter_df.iloc[-1]
    days_since = max((as_of - last_row["Tanggal Bayar"]).days, 0)
    balance = last_row["Pem kWh"] - daily_rate * days_since
    return max(round(balance, 1), 0.0)


def build_projection(
    current_balance: float,
    daily_rate: float,
    start_date: dt.date,
    end_date: dt.date,
    ref_date: dt.date,
) -> pd.DataFrame:
    dates = pd.date_range(start_date, end_date, freq="D")
    days_from_ref = [(d.date() - ref_date).days for d in dates]
    balances = [
        max(current_balance - daily_rate * d, 0.0) for d in days_from_ref
    ]
    return pd.DataFrame(
        {"Tanggal": dates, "Perkiraan Sisa Token (kWh)": balances}
    )


def estimate_depletion_date(
    current_balance: float, daily_rate: float, ref_date: dt.date
):
    if daily_rate <= 0:
        return None
    days_left = current_balance / daily_rate
    return ref_date + dt.timedelta(days=int(days_left))


def build_projection_chart(proj_df: pd.DataFrame, depletion_date):
    line = (
        alt.Chart(proj_df)
        .mark_line(color="#38bdf8")
        .encode(
            x=alt.X("Tanggal:T", title="Tanggal"),
            y=alt.Y(
                "Perkiraan Sisa Token (kWh):Q", title="Sisa Token (kWh)"
            ),
        )
    )
    zero_rule = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(color="#ef4444", strokeDash=[4, 4])
        .encode(y="y:Q")
    )

    layers = [line, zero_rule]
    if depletion_date is not None:
        marker_df = pd.DataFrame(
            {"Tanggal": [pd.Timestamp(depletion_date)], "y": [0]}
        )
        point = (
            alt.Chart(marker_df)
            .mark_point(size=120, color="#ef4444", filled=True)
            .encode(x="Tanggal:T", y="y:Q")
        )
        layers.append(point)

    return alt.layer(*layers).properties(height=320)


# =============================================================================
# LAYOUT & INTERFACE
# =============================================================================

st.set_page_config(
    page_title="Prediksi Token Prabayar - PLN Platform",
    page_icon="⚡",
    layout="wide",
)

apply_module_style()
render_hero_banner(
    module_number=2, icon="🔋", title="Prediksi Sisa Token Prabayar"
)

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Upload riwayat pembelian token** (Excel/CSV) dari AP2T.
        2. Kolom wajib: `Nomer Meter`, `Pem kWh`, `Tanggal Bayar`.
        3. Rata-rata harian dihitung menggunakan rasio interval pembelian riil PLN.
        """
    )

uploaded_file = st.file_uploader(
    "Pilih file Excel/CSV riwayat token",
    type=["xlsx", "xls", "csv"],
    key="token_uploader",
)

if uploaded_file:
    try:
        df = load_token_history(uploaded_file)

        if df.empty:
            st.warning("Tidak ada data transaksi token yang valid di file ini.")
        else:
            meters = df["Nomer Meter"].unique().tolist()
            selected_meter = (
                meters[0]
                if len(meters) == 1
                else st.selectbox("Pilih Nomer Meter:", meters)
            )
            meter_df = df[df["Nomer Meter"] == selected_meter].sort_values(
                "Tanggal Bayar"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                window_option = st.selectbox(
                    "Hitung rata-rata pemakaian dari:",
                    [
                        "30 Hari Terakhir",
                        "60 Hari Terakhir",
                        "90 Hari Terakhir",
                        "180 Hari Terakhir",
                        "Seluruh Riwayat",
                    ],
                    index=2,
                )
            window_map = {
                "30 Hari Terakhir": 30,
                "60 Hari Terakhir": 60,
                "90 Hari Terakhir": 90,
                "180 Hari Terakhir": 180,
                "Seluruh Riwayat": None,
            }
            daily_rate, last_purchase_date = compute_daily_rate_pln(
                meter_df, window_map[window_option]
            )
            today = dt.date.today()

            est_balance = estimate_current_balance(
                meter_df, daily_rate, pd.Timestamp(today)
            )

            with c2:
                current_balance = st.number_input(
                    "Sisa Token Saat Ini (kWh):",
                    min_value=0.0,
                    value=float(est_balance),
                    step=1.0,
                )

            date_range = st.date_input(
                "Pilih rentang tanggal untuk proyeksi:",
                value=(today, today + dt.timedelta(days=30)),
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = today, today + dt.timedelta(days=30)

            depletion_date = estimate_depletion_date(
                current_balance, daily_rate, today
            )

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(
                    kpi_card(
                        "📈",
                        "Rata-rata Pemakaian/Hari",
                        f"{daily_rate:.2f} kWh",
                        window_option,
                    ),
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    kpi_card(
                        "🔋",
                        "Estimasi Sisa Token Hari Ini",
                        f"{current_balance:.1f} kWh",
                        f"per {today.strftime('%d %b %Y')}",
                    ),
                    unsafe_allow_html=True,
                )
            with k3:
                depletion_label = (
                    depletion_date.strftime("%d %b %Y")
                    if depletion_date
                    else "Tidak dapat diprediksi"
                )
                st.markdown(
                    kpi_card(
                        "⚠️",
                        "Perkiraan Token Habis",
                        depletion_label,
                        "Estimasi tanggal",
                    ),
                    unsafe_allow_html=True,
                )

            proj_df = build_projection(
                current_balance, daily_rate, start_date, end_date, today
            )
            st.altair_chart(
                build_projection_chart(proj_df, depletion_date),
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")