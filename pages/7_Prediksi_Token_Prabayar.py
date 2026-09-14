import datetime as dt

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
# LOGIKA PERHITUNGAN
# =============================================================================
# Alur: Sisa token saat ini - (rata-rata pemakaian/hari x lama periode yang dicek)
# Rata-rata/hari = total Pem kWh dibeli / jumlah hari antara pembelian pertama
# & terakhir yang dipakai sebagai acuan.


def hitung_manual_sisa_token(
    sisa_saat_ini: float,
    pem_kwh_historis: float,
    tgl_bayar_awal: dt.date,
    tgl_bayar_akhir: dt.date,
    tgl_diloss_awal: dt.date,
    tgl_diloss_akhir: dt.date,
) -> dict:
    lama_historis = max((tgl_bayar_akhir - tgl_bayar_awal).days, 0)
    rata2_per_hari = (pem_kwh_historis / lama_historis) if lama_historis > 0 else 0.0

    lama_diloss = max((tgl_diloss_akhir - tgl_diloss_awal).days, 0)
    total_pemakaian_diloss = rata2_per_hari * lama_diloss

    sisa_akhir = sisa_saat_ini - total_pemakaian_diloss

    # Margin error ±1% — estimasi ini linear (asumsi pemakaian rata harian konstan),
    # jadi hasil akhir realistiknya bisa meleset sedikit dari angka pasti.
    margin = abs(sisa_akhir) * 0.01
    batas_bawah = sisa_akhir - margin
    batas_atas = sisa_akhir + margin

    return {
        "lama_historis": lama_historis,
        "rata2_per_hari": rata2_per_hari,
        "lama_diloss": lama_diloss,
        "total_pemakaian_diloss": total_pemakaian_diloss,
        "sisa_akhir": sisa_akhir,
        "batas_bawah": batas_bawah,
        "batas_atas": batas_atas,
    }


# =============================================================================
# LAYOUT & INTERFACE
# =============================================================================

st.set_page_config(
    page_title="Prediksi Token Prabayar - PLN Platform",
    page_icon="⚡",
    layout="wide",
)

apply_module_style()
render_hero_banner(module_number=2, icon="🔋", title="Prediksi Sisa Token Prabayar")

with st.expander("❓ **Petunjuk Penggunaan Sistem**"):
    st.markdown(
        """
        1. **Sisa Token Saat Ini** — isi sisa saldo token pelanggan sekarang (kWh), dari hasil cek meter/AP2T.
        2. **Lama Diloss** — pilih rentang tanggal yang mau kamu cek (misalnya rentang perbaikan/pemadaman).
        3. **Pem kWh & Tgl Bayar** — isi total kWh yang dibeli pelanggan pada periode acuan, beserta rentang
           tanggal pembelian pertama & terakhir pada periode itu. Dari sini sistem menghitung rata-rata pemakaian per hari.
        4. Semua hasil (rata-rata/hari, total pemakaian selama diloss, sisa token akhir) **otomatis terhitung ulang**
           setiap kamu ubah angka atau tanggal — tidak perlu tombol submit.
        5. Hasil akhir ditampilkan dengan margin toleransi **±1%**, karena perhitungan ini memakai asumsi
           pemakaian rata-rata harian yang konstan (bukan pengukuran real-time).
        """
    )

st.markdown(
    """
    <div class="step-card">
        <div class="step-header">
            <div class="step-title"><span class="step-number">1</span> Data Perhitungan</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)

with c1:
    sisa_saat_ini = st.number_input(
        "1️⃣ Sisa Token Saat Ini (kWh)", min_value=0.0, value=0.0, step=1.0,
    )
    pem_kwh_historis = st.number_input(
        "3️⃣ Pem kWh — total kWh dibeli selama periode acuan", min_value=0.0, value=0.0, step=1.0,
    )
    st.markdown("**4️⃣ Tgl Bayar — rentang riwayat pembelian yang jadi acuan rata-rata**")
    cc1, cc2 = st.columns(2)
    with cc1:
        tgl_bayar_awal = st.date_input("Dari", value=dt.date.today() - dt.timedelta(days=160), key="tgl_bayar_awal_manual")
    with cc2:
        tgl_bayar_akhir = st.date_input("Sampai", value=dt.date.today(), key="tgl_bayar_akhir_manual")

with c2:
    st.markdown("**2️⃣ Lama Diloss — rentang tanggal yang mau dicek**")
    dd1, dd2 = st.columns(2)
    with dd1:
        tgl_diloss_awal = st.date_input("Dari", value=dt.date.today(), key="tgl_diloss_awal_manual")
    with dd2:
        tgl_diloss_akhir = st.date_input("Sampai", value=dt.date.today() + dt.timedelta(days=4), key="tgl_diloss_akhir_manual")

if tgl_bayar_akhir <= tgl_bayar_awal:
    st.warning("⚠️ Tanggal 'Sampai' pada Tgl Bayar harus lebih besar dari tanggal 'Dari'.")
elif tgl_diloss_akhir <= tgl_diloss_awal:
    st.warning("⚠️ Tanggal 'Sampai' pada Lama Diloss harus lebih besar dari tanggal 'Dari'.")
else:
    hasil = hitung_manual_sisa_token(
        sisa_saat_ini, pem_kwh_historis, tgl_bayar_awal, tgl_bayar_akhir, tgl_diloss_awal, tgl_diloss_akhir
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📊 Hasil Perhitungan")

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            kpi_card(
                "📅", "Lama Periode Acuan", f"{hasil['lama_historis']} hari",
                f"{tgl_bayar_awal.strftime('%d %b')} – {tgl_bayar_akhir.strftime('%d %b %Y')}",
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            kpi_card("📈", "Rata-rata / Hari", f"{hasil['rata2_per_hari']:.2f} kWh", "5️⃣ hasil bagi"),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            kpi_card(
                "🗓️", "Lama Diloss", f"{hasil['lama_diloss']} hari",
                f"{tgl_diloss_awal.strftime('%d %b')} – {tgl_diloss_akhir.strftime('%d %b %Y')}",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    k4, k5 = st.columns(2)
    with k4:
        st.markdown(
            kpi_card(
                "🔻", "6️⃣ Total Pemakaian Selama Diloss", f"{hasil['total_pemakaian_diloss']:.2f} kWh",
                "rata2/hari × lama diloss",
            ),
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            kpi_card(
                "🔋", "Estimasi Sisa Token", f"{hasil['sisa_akhir']:.2f} kWh",
                f"±1%: {hasil['batas_bawah']:.1f} – {hasil['batas_atas']:.1f} kWh",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if hasil["sisa_akhir"] <= 0:
        st.error(
            f"🔴 Berdasarkan perhitungan, token diperkirakan **sudah/akan habis** sebelum {tgl_diloss_akhir.strftime('%d %B %Y')}."
        )
    else:
        st.success(
            f"🟢 Token diperkirakan masih cukup hingga {tgl_diloss_akhir.strftime('%d %B %Y')} "
            f"(sisa ±{hasil['sisa_akhir']:.1f} kWh, margin toleransi 1%)."
        )