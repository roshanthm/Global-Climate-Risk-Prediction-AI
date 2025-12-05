import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Climate Risk Radar",
    page_icon="🌍",
    layout="wide"
)

# ---------- STYLES ----------
st.markdown(
    """
    <style>
        .main {
            background: radial-gradient(circle at top, #0f172a 0, #020617 55%, #000 100%);
            color: #e5e7eb;
        }
        .big-title {
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(90deg, #38bdf8, #a855f7, #22c55e);
            -webkit-background-clip: text;
            color: transparent;
        }
        .subtitle {
            font-size: 0.95rem;
            color: #9ca3af;
        }
        .metric-card {
            padding: 1rem 1.25rem;
            border-radius: 1rem;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.3);
        }
        .risk-low { color: #22c55e; font-weight: 600; }
        .risk-medium { color: #eab308; font-weight: 600; }
        .risk-high { color: #ef4444; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-title">🌍 Climate Risk Radar</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered climate risk prediction with ML, satellite, and disaster alerts.</div>',
    unsafe_allow_html=True
)

st.write("")
col_left, col_right = st.columns([2, 1])

with col_left:
    place = st.text_input("📍 Search any city or country", value="Kottayam")

with col_right:
    st.write("")
    analyze = st.button("Analyze Climate Risk", type="primary")

st.write("")

# ---------- CALL BACKEND ----------
if analyze and place.strip():
    try:
        with st.spinner(f"Fetching climate intelligence for **{place}**..."):
            resp = requests.post(
                f"{BACKEND_URL}/risk",
                json={"location": place.strip()},
                timeout=25,
            )
        
        if resp.status_code != 200:
            st.error(f"Backend error: {resp.status_code} - {resp.text}")
        else:
            data = resp.json()
            loc = data["location"]
            wx = data["weather"]
            risks = data["risks"]

            st.markdown(f"### 📌 Location: **{loc['name']}**, {loc['country']}")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**🌡 Temperature**")
                st.metric("", f"{wx['temp_c']} °C")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**💨 Wind Speed**")
                st.metric("", f"{wx['wind_kmh']} km/h")
                st.markdown("</div>", unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**🌧 Rain (Last Hours)**")
                st.metric("", f"{wx['recent_rain_mm']} mm")
                st.markdown("</div>", unsafe_allow_html=True)

            with c4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**⏱ Last Update**")
                st.metric("", wx.get("last_update", "N/A"))
                st.markdown("</div>", unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🔍 Climate Risk Snapshot")

            # ------------ RISK CARDS ------------
            r1, r2, r3 = st.columns(3)

            def risk_class(level):
                if level == "High": return "risk-high"
                if level == "Medium": return "risk-medium"
                return "risk-low"

            # -------- FLOOD CARD --------
            with r1:
                flood = risks["flood"]
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**🌊 Flood Risk**")
                st.markdown(f'<span class="{risk_class(flood["level"])}">{flood["level"]}</span>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if flood["level"] == "High":
                    st.markdown(
                        """
                        <div style="
                            background:#b91c1c;
                            color:white;
                            padding:6px 10px;
                            border-radius:8px;
                            font-weight:700;
                            margin-top:6px;
                            text-align:center;
                            ">
                            🚨 EMERGENCY – FLOOD ALERT ACTIVE
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # -------- HEAT CARD --------
            with r2:
                heat = risks["heat"]
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**🔥 Heat Risk**")
                st.markdown(f'<span class="{risk_class(heat["level"])}">{heat["level"]}</span>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # -------- STORM CARD --------
            with r3:
                storm = risks["storm"]
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**🌪 Storm Risk**")
                st.markdown(f'<span class="{risk_class(storm["level"])}">{storm["level"]}</span>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.write("")
            st.info(data.get("ai_insight", ""))

    except Exception as e:
        st.error(f"Frontend Error: {e}")

else:
    st.caption("👆 Enter a location and click Analyze.")
