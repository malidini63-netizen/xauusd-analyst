# app.py — XAUUSD Analyst Dashboard
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timezone
from config import assert_config
from price_fetcher import get_all_timeframes, get_current_price
from bias_engine import analyze_timeframe, compute_htf_bias
from pe_generator import generate_pe
from alerts import send_telegram, format_pe_alert

st.set_page_config(
    page_title="XAUUSD Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #3a3a5e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #f0c040; }
    .metric-label { font-size: 0.85em; color: #aaa; margin-top: 5px; }
    .level-card {
    background: #ffffff;
    border-radius: 8px;
    padding: 12px 15px;
    margin: 5px 0;
    color: #111111;
    font-weight: 500;
}
.bull { 
    background: #e8f5e9;
    border-left: 5px solid #26a269;
    color: #1a5c2a;
}
.bear { 
    background: #fdecea;
    border-left: 5px solid #e01b24;
    color: #7a0c0c;
}
.neutral { 
    background: #fff8e1;
    border-left: 5px solid #f0c040;
    color: #7a5c00;
}
</style>
""", unsafe_allow_html=True)

assert_config()

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Paramètres")
    st.divider()
    bars = st.slider("📊 Nombre de bougies", 50, 200, 100, step=10)
    st.divider()
    st.caption(f"🕐 {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}")
    st.caption("📡 Source : Twelve Data")
    st.caption("🤖 IA : Groq LLaMA 3")

# ── HEADER ───────────────────────────────────────────────
st.markdown("# 📊 XAUUSD — Technical Analyst")
st.caption("Analyse ICT/SMC multi-timeframe • OB • FVG • CHoCH • BOS • PE automatique")
st.divider()

# ── SESSION STATE ─────────────────────────────────────────
for key in ["analyses", "htf_bias", "pe", "price"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── BOUTON ANALYSE ────────────────────────────────────────
if st.button("🔍 Lancer l'analyse technique", type="primary", use_container_width=True):

    with st.spinner("💰 Récupération du prix actuel..."):
        st.session_state.price = get_current_price()

    with st.spinner("📊 Récupération des données multi-timeframe..."):
        all_data = get_all_timeframes(bars=bars)

    with st.spinner("🧠 Analyse de la structure ICT/SMC..."):
        analyses = {
            tf: analyze_timeframe(df, tf)
            for tf, df in all_data.items()
        }
        st.session_state.analyses = analyses
        st.session_state.htf_bias = compute_htf_bias(analyses)

    with st.spinner("🤖 Génération du Plan d'Exécution IA..."):
        st.session_state.pe = generate_pe(
            st.session_state.price,
            analyses,
            st.session_state.htf_bias
        )

st.divider()

# ── AFFICHAGE ─────────────────────────────────────────────
if st.session_state.analyses and st.session_state.htf_bias and st.session_state.pe:

    price    = st.session_state.price
    analyses = st.session_state.analyses
    htf_bias = st.session_state.htf_bias
    pe       = st.session_state.pe
    sp       = pe.get("scenario_principal", {})

    # ── PRIX + BIAIS ─────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{price}</div>
            <div class="metric-label">Prix XAUUSD</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{htf_bias['emoji']} {htf_bias['bias']}</div>
            <div class="metric-label">Biais HTF</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{htf_bias['score']:+.1f}</div>
            <div class="metric-label">Score</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        risque = pe.get("risque", "N/A")
        color = "#e01b24" if risque == "Élevé" else "#f0c040" if risque == "Modéré" else "#26a269"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color}">{risque}</div>
            <div class="metric-label">Risque</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── JAUGE BIAIS ───────────────────────────────────────
    score = htf_bias["score"]
    gauge_color = "#26a269" if score > 0 else "#e01b24" if score < 0 else "#f0c040"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis": {"range": [-6.5, 6.5]},
            "bar":  {"color": gauge_color},
            "steps": [
                {"range": [-6.5, -3], "color": "#3b0a0a"},
                {"range": [-3, -1],   "color": "#5a1a1a"},
                {"range": [-1, 1],    "color": "#2a2a2a"},
                {"range": [1, 3],     "color": "#0a3b1a"},
                {"range": [3, 6.5],   "color": "#0a5a1a"},
            ]
        },
        title={"text": f"Score HTF — {htf_bias['bias']}", "font": {"size": 16}}
    ))
    fig_gauge.update_layout(
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # ── CONTENU PRINCIPAL ─────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:

        # Détail HTF
        st.subheader("🏗️ Structure Multi-Timeframe")
        for line in htf_bias["details"]:
            st.markdown(line)

        st.divider()

        # Niveaux par TF
        st.subheader("📐 Niveaux ICT/SMC")
        for tf, analysis in analyses.items():
            if analysis.get("error"):
                continue
            with st.expander(f"[{tf}] {analysis['trend']} @ {analysis['price']}"):
                if analysis.get("bos"):
                    bos = analysis["bos"]
                    st.markdown(f"🔵 **BOS {bos['type']}** @ `{bos['level']}`")
                if analysis.get("choch"):
                    choch = analysis["choch"]
                    st.markdown(f"🔄 **CHoCH {choch['type']}** @ `{choch['level']}`")
                if analysis.get("bullish_ob"):
                    ob = analysis["bullish_ob"]
                    st.markdown(f"🟢 **OB Bullish** : `{ob['bottom']}` — `{ob['top']}`")
                if analysis.get("bearish_ob"):
                    ob = analysis["bearish_ob"]
                    st.markdown(f"🔴 **OB Bearish** : `{ob['bottom']}` — `{ob['top']}`")
                if analysis.get("bullish_fvg"):
                    fvg = analysis["bullish_fvg"]
                    st.markdown(f"🟩 **FVG Bullish** : `{fvg['bottom']}` — `{fvg['top']}`")
                if analysis.get("bearish_fvg"):
                    fvg = analysis["bearish_fvg"]
                    st.markdown(f"🟥 **FVG Bearish** : `{fvg['bottom']}` — `{fvg['top']}`")
                if analysis.get("nearest_bsl"):
                    st.markdown(f"💧 **BSL** : `{analysis['nearest_bsl']['level']}`")
                if analysis.get("nearest_ssl"):
                    st.markdown(f"💧 **SSL** : `{analysis['nearest_ssl']['level']}`")

    with col_right:

        # Plan d'Exécution
        st.subheader("🎯 Plan d'Exécution (PE)")
        st.info(pe.get("resume_marche", ""))

        if sp:
            direction = sp.get("direction", "")
            css = "bull" if direction == "LONG" else "bear" if direction == "SHORT" else "neutral"
            emoji = "📈" if direction == "LONG" else "📉" if direction == "SHORT" else "⏳"

            st.markdown(f"""<div class="level-card {css}">
                <strong>{emoji} {direction}</strong><br>
                🎯 Entrée : <code>{sp.get('entree_zone', 'N/A')}</code>
                ({sp.get('entree_type', '')})<br>
                🛑 SL : <code>{sp.get('sl', 'N/A')}</code><br>
                ✅ TP1 : <code>{sp.get('tp1', 'N/A')}</code><br>
                ✅ TP2 : <code>{sp.get('tp2', 'N/A')}</code><br>
                📊 R/R : <strong>{sp.get('rr', 'N/A')}</strong><br>
                ⏰ Timing : {sp.get('timing', 'N/A')}
            </div>""", unsafe_allow_html=True)

        sa = pe.get("scenario_alternatif", {})
        if sa:
            st.markdown(f"""<div class="level-card neutral">
                🔄 <strong>Scénario Alternatif</strong><br>
                _{sa.get('condition', '')}_<br>
                Zone : <code>{sa.get('zone', 'N/A')}</code>
            </div>""", unsafe_allow_html=True)

        st.divider()

        st.markdown(f"🚫 **Invalidation :** `{pe.get('invalidation', 'N/A')}`")
        st.markdown(f"💬 _{pe.get('patience', '')}_")

        if pe.get("niveaux_cles"):
            st.markdown("**📌 Niveaux clés :**")
            for n in pe["niveaux_cles"]:
                st.markdown(f"- `{n}`")

        st.divider()

        # Telegram
        alert_msg = format_pe_alert(price, htf_bias, pe)
        if st.button("📱 Envoyer PE sur Telegram", type="secondary", use_container_width=True):
            with st.spinner("Envoi..."):
                success = send_telegram(alert_msg)
            if success:
                st.success("✅ PE envoyé sur Telegram !")
            else:
                st.error("❌ Échec envoi Telegram.")

        with st.expander("👁️ Aperçu message Telegram"):
            st.text(alert_msg)