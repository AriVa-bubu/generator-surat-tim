"""
Modul styling bersama untuk semua halaman PLN Multitools.

Sebelumnya tiap file di pages/ punya salinan CSS + hero-banner sendiri (~150 baris
terduplikasi identik di tiap file). Sekarang cukup:

    from module_style import apply_module_style, render_hero_banner, kpi_card

    apply_module_style()
    render_hero_banner(module_number=1, icon="✉️", title="Generator Surat & Arsip Otomatis")

Manfaatnya:
- Tiap file modul jadi jauh lebih pendek & fokus ke logika bisnisnya saja (lebih "enteng").
- Tampilan otomatis konsisten di semua modul.
- Ganti warna/tema cukup di satu tempat ini, tidak perlu edit satu-satu.
"""

import base64
import os

import streamlit as st

MODULE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }

    /* ---------- HERO BANNER (gradient animasi + tekstur, konsisten dgn halaman utama) ---------- */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-banner {
        position: relative;
        overflow: hidden;
        background: linear-gradient(-45deg, #0b2545, #134074, #00a8e8, #0b2545);
        background-size: 300% 300%;
        animation: gradientBG 10s ease infinite;
        border-radius: 16px; padding: 24px 28px; color: white; margin-bottom: 24px;
        box-shadow: 0 15px 30px -8px rgba(0, 168, 232, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex; align-items: center; gap: 20px;
    }
    .hero-banner::before {
        content: "";
        position: absolute; inset: 0;
        background-image:
            radial-gradient(circle at 88% 8%, rgba(56, 189, 248, 0.30) 0%, transparent 42%),
            radial-gradient(circle at 4% 108%, rgba(255, 183, 3, 0.18) 0%, transparent 45%),
            radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px);
        background-size: auto, auto, 20px 20px;
        pointer-events: none;
    }
    .hero-banner::after {
        content: "⚡";
        position: absolute;
        right: -18px; bottom: -38px;
        font-size: 170px;
        line-height: 1;
        opacity: 0.08;
        transform: rotate(-12deg);
        pointer-events: none;
    }
    .hero-logo-img { width: 70px; height: auto; border-radius: 8px; background: white; padding: 4px; position: relative; z-index: 1; }
    .hero-badge {
        background-color: #ffb703; color: #000; font-weight: 800; font-size: 0.75rem;
        padding: 4px 12px; border-radius: 20px; text-transform: uppercase; display: inline-block; margin-bottom: 6px;
        position: relative; z-index: 1;
    }
    .hero-title { font-size: 1.8rem; font-weight: 800; margin: 0; position: relative; z-index: 1; }

    /* ---------- STEP CARD (aksen kiri + hover halus + animasi masuk) ---------- */
    .step-card {
        background-color: #0f172a; border: 1px solid #1e293b; border-left: 3px solid #0284c7;
        border-radius: 16px; padding: 22px; margin-bottom: 20px;
        animation: fadeInUp 0.4s ease-out;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .step-card:hover { border-left-color: #38bdf8; box-shadow: 0 8px 20px -10px rgba(56, 189, 248, 0.25); }
    .step-header {
        display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
        border-bottom: 1px solid #334155; padding-bottom: 10px;
    }
    .step-title { font-size: 1.15rem; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 10px; }
    .step-number {
        background: linear-gradient(135deg, #0284c7, #0369a1); color: white; font-size: 0.85rem; font-weight: 700;
        width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
        box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15);
    }

    /* ---------- STAT / KPI CARD (hover lift, lebih hidup) ---------- */
    .stat-card, .kpi-card {
        background: linear-gradient(160deg, #1e293b 0%, #172033 100%);
        border: 1px solid #2b3a52; border-radius: 16px; padding: 18px 20px; height: 100%;
        transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    }
    .stat-card:hover, .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #38bdf8;
        box-shadow: 0 10px 22px -8px rgba(56, 189, 248, 0.3);
    }
    .stat-card { border-left: 4px solid #38bdf8; border-radius: 10px; padding: 14px 18px; }
    .stat-label, .kpi-label {
        font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.03em;
    }
    .stat-value, .kpi-value { font-size: 1.4rem; font-weight: 800; color: #f8fafc; margin-top: 2px; }
    .kpi-icon { font-size: 1.4rem; margin-bottom: 8px; display: inline-block; }
    .kpi-value { font-size: 1.55rem; margin: 4px 0 8px 0; }
    .kpi-delta {
        display: inline-flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 700;
        color: #94a3b8; background: rgba(148, 163, 184, 0.12); padding: 3px 9px; border-radius: 999px;
    }

    /* ---------- RESULT BANNERS (tagihan / pengembalian) ---------- */
    .result-banner-tagih {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); border: 1px solid #ef4444;
        border-radius: 16px; padding: 24px 28px; margin: 12px 0;
        animation: fadeInUp 0.35s ease-out;
    }
    .result-banner-kembali {
        background: linear-gradient(135deg, #14532d 0%, #052e16 100%); border: 1px solid #22c55e;
        border-radius: 16px; padding: 24px 28px; margin: 12px 0;
        animation: fadeInUp 0.35s ease-out;
    }
    .result-label { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #e2e8f0; margin-bottom: 6px; }
    .result-value { font-size: 2rem; font-weight: 800; color: #ffffff; }

    /* ---------- MISC ---------- */
    div[data-testid="stFileUploader"] {
        background-color: #1e293b; border: 1px dashed #475569; border-radius: 12px; padding: 8px;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stFileUploader"]:hover { border-color: #38bdf8; }
    div[data-testid="stExpander"] { border: 1px solid #2b3a52 !important; border-radius: 12px !important; }
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important; padding: 0.75rem 1.5rem !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px -6px rgba(2, 132, 199, 0.45) !important;
    }

    /* ---------- RESPONSIVE (HP / tablet) ---------- */
    @media (max-width: 640px) {
        .hero-banner { flex-direction: column; align-items: flex-start; padding: 18px 20px; }
        .hero-title { font-size: 1.35rem !important; }
        .step-card, .kpi-card, .stat-card { padding: 16px !important; }
        .result-value { font-size: 1.5rem !important; }
    }
</style>
"""


def _get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_module_style() -> None:
    """Suntikkan CSS bersama. Panggil sekali di paling atas tiap halaman modul."""
    st.markdown(MODULE_CSS, unsafe_allow_html=True)


def render_hero_banner(module_number: int, icon: str, title: str, logo_path: str = "logo_pln.png") -> None:
    """Render banner judul modul yang konsisten di semua halaman."""
    logo_base64 = _get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""
    logo_html = (
        f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo-img" alt="PLN Logo">'
        if logo_base64
        else icon
    )
    st.markdown(
        f"""
        <div class="hero-banner">
            <div>{logo_html}</div>
            <div>
                <span class="hero-badge">MODUL {module_number}</span>
                <div class="hero-title">{icon} {title}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str, delta: str, tone: str = "neutral") -> str:
    """Kembalikan HTML kartu KPI. Dipakai dengan st.markdown(kpi_card(...), unsafe_allow_html=True)."""
    tone_colors = {
        "neutral": ("#94a3b8", "rgba(148, 163, 184, 0.12)"),
        "danger": ("#fca5a5", "rgba(239, 68, 68, 0.15)"),
        "success": ("#86efac", "rgba(34, 197, 94, 0.15)"),
    }
    color, bg = tone_colors.get(tone, tone_colors["neutral"])
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <span class="kpi-delta" style="color:{color}; background:{bg};">{delta}</span>
    </div>
    """


def step_card_header(number: int, title: str) -> None:
    """Render header 'Langkah N: ...' bergaya konsisten, tanpa perlu tulis HTML manual tiap kali."""
    st.markdown(
        f"""
        <div class="step-card">
            <div class="step-header">
                <div class="step-title"><span class="step-number">{number}</span> {title}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )