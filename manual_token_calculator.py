import datetime as dt

import streamlit as st

# =============================================================================
# KALKULATOR MANUAL SISA TOKEN (sesuai alur baru)
# =============================================================================
# Alur: Sisa token saat ini - (rata-rata pemakaian/hari x lama periode yang dicek)
# Rata-rata/hari dihitung dari: total Pem kWh dibeli / jumlah hari antara
# pembelian pertama & terakhir yang dipakai sebagai acuan.


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


def render_manual_token_calculator() -> None:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-header">
                <div class="step-title"><span class="step-number">M</span> Hitung Manual Sisa Token (Alur Cepat)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Isi 6 data di bawah — hasilnya otomatis terhitung ulang tiap kamu ubah angka/tanggal, tidak perlu tombol submit."
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
        return
    if tgl_diloss_akhir <= tgl_diloss_awal:
        st.warning("⚠️ Tanggal 'Sampai' pada Lama Diloss harus lebih besar dari tanggal 'Dari'.")
        return

    hasil = hitung_manual_sisa_token(
        sisa_saat_ini, pem_kwh_historis, tgl_bayar_awal, tgl_bayar_akhir, tgl_diloss_awal, tgl_diloss_akhir
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📊 Hasil Perhitungan")

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-icon">📅</div>
            <div class="kpi-label">Lama Periode Acuan</div>
            <div class="kpi-value">{hasil['lama_historis']} hari</div>
            <span class="kpi-delta">{tgl_bayar_awal.strftime('%d %b')} – {tgl_bayar_akhir.strftime('%d %b %Y')}</span></div>""",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-icon">📈</div>
            <div class="kpi-label">Rata-rata / Hari</div>
            <div class="kpi-value">{hasil['rata2_per_hari']:.2f} kWh</div>
            <span class="kpi-delta">5️⃣ hasil bagi</span></div>""",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-icon">🗓️</div>
            <div class="kpi-label">Lama Diloss</div>
            <div class="kpi-value">{hasil['lama_diloss']} hari</div>
            <span class="kpi-delta">{tgl_diloss_awal.strftime('%d %b')} – {tgl_diloss_akhir.strftime('%d %b %Y')}</span></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    k4, k5 = st.columns(2)
    with k4:
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-icon">🔻</div>
            <div class="kpi-label">6️⃣ Total Pemakaian Selama Diloss</div>
            <div class="kpi-value">{hasil['total_pemakaian_diloss']:.2f} kWh</div>
            <span class="kpi-delta">rata2/hari × lama diloss</span></div>""",
            unsafe_allow_html=True,
        )
    with k5:
        tone = "danger" if hasil["sisa_akhir"] <= 0 else "success"
        color, bg = ("#fca5a5", "rgba(239, 68, 68, 0.15)") if tone == "danger" else ("#86efac", "rgba(34, 197, 94, 0.15)")
        st.markdown(
            f"""<div class="kpi-card"><div class="kpi-icon">🔋</div>
            <div class="kpi-label">Estimasi Sisa Token</div>
            <div class="kpi-value">{hasil['sisa_akhir']:.2f} kWh</div>
            <span class="kpi-delta" style="color:{color}; background:{bg};">
                ±1%: {hasil['batas_bawah']:.1f} – {hasil['batas_atas']:.1f} kWh
            </span></div>""",
            unsafe_allow_html=True,
        )

    if hasil["sisa_akhir"] <= 0:
        st.error(
            f"🔴 Berdasarkan perhitungan, token diperkirakan **sudah/akan habis** sebelum {tgl_diloss_akhir.strftime('%d %B %Y')}."
        )
    else:
        st.success(
            f"🟢 Token diperkirakan masih cukup hingga {tgl_diloss_akhir.strftime('%d %B %Y')} "
            f"(sisa ±{hasil['sisa_akhir']:.1f} kWh, margin toleransi 1%)."
        )
