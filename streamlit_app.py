import streamlit as st
import sys
import os
import requests as http_requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Emergency Response System",
    page_icon="🚑",
    layout="wide"
)

# ─── Backend URL ───────────────────────────────────────────
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def call_backend(report: str, location: str, radius: int):
    try:
        response = http_requests.post(
            f"{BACKEND_URL}/analyze",
            json={"report": report, "location": location, "radius_km": radius},
            timeout=60
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("detail", "Backend error")
    except http_requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to backend. Open a new terminal and run: uvicorn app.main:app --reload --port 8000"
    except Exception as e:
        return None, str(e)


# ─── Cookie Manager ─────────────────────────────────────────
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="ers_",
    password="emergency_response_secret_key_2024"
)

if not cookies.ready():
    st.stop()

# ─── Session State Init ─────────────────────────────────────
if "connected" not in st.session_state:
    saved = cookies.get("user_info")
    if saved:
        try:
            st.session_state.user_info = json.loads(saved)
            st.session_state.connected = True
        except:
            st.session_state.connected = False
            st.session_state.user_info = {}
    else:
        st.session_state.connected = False
        st.session_state.user_info = {}


# ─── Theme ─────────────────────────────────────────────────
BG = "linear-gradient(135deg, #1a0a0a 0%, #0a0a1a 50%, #1a0a0a 100%)"
CARD = "#1e1e1e"
CARD_BORDER = "#2a2a2a"
HOSP_BG = "#1a1a2e"
HOSP_BORDER = "#2a2a4a"
PLAN_BG = "#0d1f0d"
PLAN_BORDER = "#1a4a1a"
PLAN_COLOR = "#ccffcc"
TEXT = "#ffffff"
TEXT2 = "#aaaaaa"
MUTED = "#888888"
INPUT_BG = "#111111"
INPUT_BORDER = "#444444"
BAR_TRACK = "#2a2a2a"
SEV_BG = "#1a1a1a"
SEV_BORDER = "#2a2a2a"
DIVIDER = "#333333"
LOGIN_BG = "#1a1a1a"
LOGIN_BORDER = "#333333"
DEMO_BG = "#2a2a2a"
DESC_BG = "#222222"


# ─── Login Page ─────────────────────────────────────────────
def show_login():
    st.markdown(f"""
    <style>
        .stApp {{ background: {BG}; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
            max-width: 100% !important;
        }}
        .login-wrapper {{ max-width: 520px; margin: 0 auto; padding: 0 1rem; }}
        .login-box {{
            background: {LOGIN_BG};
            border: 1px solid {LOGIN_BORDER};
            border-radius: 24px;
            padding: 2.5rem 2rem;
            text-align: center;
        }}
        .login-title {{
            font-size: 2.4rem; font-weight: 800;
            background: linear-gradient(90deg, #ff4444, #ff8800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem; line-height: 1.2;
        }}
        .login-subtitle {{
            color: {MUTED}; font-size: 1rem; margin-bottom: 1.2rem;
        }}
        .footer-note {{
            color: {MUTED}; font-size: 0.75rem;
            margin-top: 1.5rem; line-height: 1.6;
        }}
        .divider-line {{
            display: flex; align-items: center;
            gap: 10px; margin: 1.2rem 0;
            color: {MUTED}; font-size: 0.8rem;
        }}
        .divider-line::before, .divider-line::after {{
            content: ""; flex: 1;
            border-top: 1px solid {DIVIDER};
        }}
        .stTextInput input {{
            background: #111111 !important;
            color: white !important;
            border: 1px solid #444444 !important;
            border-radius: 10px !important;
        }}
        .stButton > button {{
            background: linear-gradient(90deg, #cc0000, #ff4444) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.6rem 2rem !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            width: 100% !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div style="text-align:center; margin-bottom: 1rem;">
        <div style="
            font-size: 2.5rem; font-weight: 900;
            background: linear-gradient(90deg, #ff4444, #ff8800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
        ">EROS</div>
        <div style="font-size: 0.7rem; color: {MUTED}; letter-spacing: 2px;">
            EMERGENCY RESPONSE OS
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-wrapper"><div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🚑 Emergency Response System</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">AI-Powered Emergency Analysis Platform</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-bottom:1.5rem;">
        <div style="background:#1a1a2e; border-radius:20px; padding:6px 14px; font-size:0.82rem; color:#8888ff;">🧠 AI Analysis</div>
        <div style="background:#1a2e1a; border-radius:20px; padding:6px 14px; font-size:0.82rem; color:#44cc88;">🏥 Real Hospitals</div>
        <div style="background:#2e1a1a; border-radius:20px; padding:6px 14px; font-size:0.82rem; color:#ff8844;">📊 Severity Detection</div>
        <div style="background:#1a2a2e; border-radius:20px; padding:6px 14px; font-size:0.82rem; color:#44aaff;">🎙️ Voice Input</div>
        <div style="background:#2a1a2e; border-radius:20px; padding:6px 14px; font-size:0.82rem; color:#aa66ff;">🗺️ Live Maps</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider-line">Login to continue</div>', unsafe_allow_html=True)

    # Simple login form
    username = st.text_input("Username", placeholder="Enter username", key="login_username")
    password = st.text_input("Password", placeholder="Enter password", type="password", key="login_password")

    if st.button("🚑 Login", key="login_btn"):
        # Valid credentials - you can change these
        valid_users = {
            "admin": "eros2024",
            "demo": "demo123",
            "eros": "emergency",
        }
        if username in valid_users and valid_users[username] == password:
            st.session_state.connected = True
            st.session_state.user_info = {"name": username, "picture": ""}
            cookies["user_info"] = json.dumps({"name": username, "picture": ""})
            cookies.save()
            st.rerun()
        else:
            st.error("❌ Invalid username or password!")

    st.markdown("""
    <div class="footer-note">
        🔒 This is a simulation system for educational purposes.<br>
        No real emergency services are notified.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)


# ─── Main App ───────────────────────────────────────────────

def show_app():
    st.markdown(f"""
    <style>
        .stApp {{ background: {BG}; color: {TEXT}; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        @media (max-width: 768px) {{
            .hero-title {{ font-size: 1.8rem !important; padding-top: 1rem !important; }}
            .hero-subtitle {{ font-size: 0.9rem !important; }}
            .info-card {{ padding: 0.8rem !important; }}
            .plan-box {{ font-size: 0.85rem !important; padding: 1rem !important; }}
            .section-header {{ font-size: 1.1rem !important; }}
        }}
        @media (max-width: 640px) {{
            [data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
        }}
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }}
        .hero-title {{
            text-align: center; font-size: 3rem; font-weight: 800;
            background: linear-gradient(90deg, #ff4444, #ff8800, #ff4444);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem; padding-top: 1rem;
        }}
        .hero-subtitle {{
            text-align: center; font-size: 1.1rem;
            color: {MUTED}; margin-bottom: 1rem;
        }}
        .badge-critical {{ background:#ff0000; color:white; padding:6px 18px; border-radius:20px; font-weight:700; font-size:1rem; display:inline-block; }}
        .badge-high {{ background:#ff6600; color:white; padding:6px 18px; border-radius:20px; font-weight:700; font-size:1rem; display:inline-block; }}
        .badge-medium {{ background:#ffaa00; color:black; padding:6px 18px; border-radius:20px; font-weight:700; font-size:1rem; display:inline-block; }}
        .badge-low {{ background:#00aa44; color:white; padding:6px 18px; border-radius:20px; font-weight:700; font-size:1rem; display:inline-block; }}
        .info-card {{
            background:{CARD}; border:1px solid {CARD_BORDER};
            border-radius:12px; padding:1.2rem; margin-bottom:1rem;
            border-left:4px solid #ff4444;
        }}
        .info-card-label {{ color:{MUTED}; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
        .info-card-value {{ color:{TEXT}; font-size:1.1rem; font-weight:600; }}
        .hospital-card {{
            background:{HOSP_BG}; border:1px solid {HOSP_BORDER};
            border-radius:12px; padding:1.2rem; margin-bottom:0.8rem;
            border-left:4px solid #4444ff;
        }}
        .hospital-name {{ color:{TEXT}; font-size:1rem; font-weight:700; margin-bottom:4px; }}
        .hospital-detail {{ color:{TEXT2}; font-size:0.85rem; margin:2px 0; }}
        .hospital-distance {{ color:#4488ff; font-weight:700; font-size:1rem; }}
        .plan-box {{
            background:{PLAN_BG}; border:1px solid {PLAN_BORDER};
            border-radius:12px; padding:1.5rem; border-left:4px solid #00cc44;
            white-space:pre-wrap; color:{PLAN_COLOR};
            font-size:0.95rem; line-height:1.7;
        }}
        .section-header {{
            font-size:1.3rem; font-weight:700; color:{TEXT};
            margin:1.5rem 0 1rem 0; padding-bottom:0.5rem;
            border-bottom:2px solid {DIVIDER};
        }}
        .stButton > button {{
            background: linear-gradient(90deg, #cc0000, #ff4444);
            color:white; border:none; border-radius:10px;
            padding:0.8rem 2rem; font-size:1.1rem; font-weight:700; width:100%;
        }}
        .stTextArea textarea {{
            background:{INPUT_BG} !important; color:{TEXT} !important;
            caret-color: {TEXT} !important;
            border:1px solid {INPUT_BORDER} !important; border-radius:10px !important;
        }}
        .stTextInput input {{
            background:{INPUT_BG} !important; color:{TEXT} !important;
            caret-color: {TEXT} !important;
            border:1px solid {INPUT_BORDER} !important; border-radius:10px !important;
        }}
        .severity-bar-container {{
            background:{SEV_BG}; border-radius:12px; padding:1.2rem;
            margin:1rem 0; border:1px solid {SEV_BORDER};
        }}
        .severity-label {{ color:{MUTED}; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
        .bar-track {{ background:{BAR_TRACK}; border-radius:8px; height:18px; width:100%; overflow:hidden; }}
        .bar-fill-low {{ background:linear-gradient(90deg,#00aa44,#00cc55); height:100%; border-radius:8px; width:25%; }}
        .bar-fill-medium {{ background:linear-gradient(90deg,#ffaa00,#ffcc00); height:100%; border-radius:8px; width:50%; }}
        .bar-fill-high {{ background:linear-gradient(90deg,#ff6600,#ff8800); height:100%; border-radius:8px; width:75%; }}
        .bar-fill-critical {{ background:linear-gradient(90deg,#cc0000,#ff0000); height:100%; border-radius:8px; width:100%; }}
        .severity-markers {{ display:flex; justify-content:space-between; margin-top:6px; }}
        .severity-marker {{ font-size:0.7rem; color:{MUTED}; }}
        .user-badge {{
            background:{DEMO_BG}; border-radius:20px; padding:4px 14px;
            font-size:0.85rem; color:{TEXT2}; display:inline-block;
        }}
        .api-status {{
            background:#0d1a0d; border:1px solid #1a4a1a;
            border-radius:8px; padding:6px 14px; font-size:0.8rem;
            color:#44cc88; display:inline-block;
        }}
    </style>
    """, unsafe_allow_html=True)

    # ─── Top Bar ─────────────────────────────────────────────
    tb1, tb2, tb3 = st.columns([4, 2, 1])

    user_info = st.session_state.get("user_info", {})
    user_name = user_info.get("name", "User")
    user_picture = user_info.get("picture", "")

    with tb1:
        st.markdown('<span class="api-status">⚡ FastAPI Backend Connected</span>',
                    unsafe_allow_html=True)
    with tb2:
        if user_picture:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-top:6px;">
                <img src="{user_picture}" style="width:30px; height:30px; border-radius:50%;"/>
                <span style="font-size:0.85rem; color:{TEXT2};">{user_name}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-badge">👤 {user_name}</div>',
                        unsafe_allow_html=True)
    with tb3:
        if st.button("🚪 Logout", key="logout"):
            st.session_state.connected = False
            st.session_state.user_info = {}
            cookies["user_info"] = ""
            cookies.save()
            st.rerun()

    # ─── Hero ────────────────────────────────────────────────
    st.markdown('<div class="hero-title">🚑 Emergency Response System</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-Powered • Real Hospitals • Instant Analysis</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # ─── Input Section ───────────────────────────────────────
    col1, col2 = st.columns([2, 1], gap="medium")

    with col1:
        st.markdown("### 📝 Accident Report")

        # ── Voice Input ──────────────────────────────────────
        # Initialize session state for voice
        if "voice_text" not in st.session_state:
            st.session_state.voice_text = ""
        if "voice_recording_key" not in st.session_state:
            st.session_state.voice_recording_key = 0
        if "transcribed_audio_key" not in st.session_state:
            st.session_state.transcribed_audio_key = -1

        st.markdown("🎙️ **Voice Input** — record your accident report:")

        audio_file = st.audio_input(
            "Record accident report",
            key=f"voice_input_{st.session_state.voice_recording_key}"
        )

        # Action buttons row
        btn_col1, btn_col2 = st.columns([1, 1])

        with btn_col1:
            if st.button("🗑️ Cancel & Re-record", use_container_width=True, key="cancel_audio"):
                st.session_state.voice_text = ""
                st.session_state.voice_recording_key += 1
                st.rerun()
        # Auto-transcribe when audio is recorded
        current_audio_key = st.session_state.voice_recording_key
        if audio_file is not None and st.session_state.transcribed_audio_key != current_audio_key:
            with st.spinner("🔊 Transcribing your voice..."):
                try:
                    from groq import Groq
                    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                    transcription = groq_client.audio.transcriptions.create(
                        file=("audio.wav", audio_file.read(), "audio/wav"),
                        model="whisper-large-v3",
                        language="en"
                    )
                    st.session_state.voice_text = transcription.text
                    st.session_state.transcribed_audio_key = current_audio_key
                    st.success(f"✅ Transcribed: {st.session_state.voice_text}")
                except Exception as e:
                    st.warning(f"Voice transcription failed: {str(e)}")

        voice_text = st.session_state.voice_text

        report = st.text_area(
            label="Describe the accident",
            value=voice_text if voice_text else "",
            placeholder="Example: Two vehicles collided near the main market. One person is unconscious and bleeding heavily.",
            height=130,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### 📍 Accident Location")
        location = st.text_input(
            label="Location",
            placeholder="Example: MG Road, Bangalore",
            label_visibility="collapsed"
        )
        st.markdown("### 🔍 Search Radius")
        radius = st.slider(
            "Radius (km)",
            min_value=1,
            max_value=100,
            value=5,
            label_visibility="collapsed"
        )
        st.caption(f"Searching hospitals within {radius} km")

    st.markdown("")
    analyze_btn = st.button("🚨 ANALYZE EMERGENCY", use_container_width=True)
    st.markdown("---")

    # ─── Results ─────────────────────────────────────────────
    if analyze_btn:

        if not report.strip():
            st.error("⚠️ Please describe the accident first.")
            st.stop()
        if not location.strip():
            st.error("⚠️ Please enter the accident location.")
            st.stop()

        with st.spinner("🚨 Sending to Emergency Response API..."):
            result, error = call_backend(report, location, radius)

        if error:
            st.error(f"❌ Error: {error}")
            if "Could not find location" in str(error) or "location" in str(error).lower():
                st.info("💡 **Tip:** Use a more specific location name. Examples:\n- ✅ 'Tumkur, Karnataka'\n- ✅ 'MG Road, Bangalore'\n- ✅ 'Mysore, India'\n- ❌ 'SIT main road, tumkur' (too specific, not on map)")
            st.stop()

        analysis = result["analysis"]
        hospitals = result["hospitals"]
        plan = result["emergency_plan"]
        coords = result.get("location_coords", {})
        lat = coords.get("lat")
        lon = coords.get("lon")
        radius_used = result.get("radius_used", radius)
        radius_expanded = result.get("radius_expanded", False)

        # Severity Badge
        severity = analysis.get("severity", "UNKNOWN")
        badge_class = {
            "CRITICAL": "badge-critical",
            "HIGH":     "badge-high",
            "MEDIUM":   "badge-medium",
            "LOW":      "badge-low"
        }.get(severity, "badge-medium")

        st.markdown(f"""
            <div style="text-align:center; margin:1rem 0 2rem 0;">
                <div style="color:{MUTED}; font-size:0.85rem; margin-bottom:6px;">SEVERITY LEVEL</div>
                <span class="{badge_class}">⚠️ {severity}</span>
            </div>
        """, unsafe_allow_html=True)

        # Severity Bar
        bar_class = {
            "LOW":      "bar-fill-low",
            "MEDIUM":   "bar-fill-medium",
            "HIGH":     "bar-fill-high",
            "CRITICAL": "bar-fill-critical"
        }.get(severity, "bar-fill-medium")

        st.markdown(f"""
        <div class="severity-bar-container">
            <div class="severity-label">⚡ Severity Meter</div>
            <div class="bar-track"><div class="{bar_class}"></div></div>
            <div class="severity-markers">
                <span class="severity-marker">LOW</span>
                <span class="severity-marker">MEDIUM</span>
                <span class="severity-marker">HIGH</span>
                <span class="severity-marker">CRITICAL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Analysis Cards
        st.markdown('<div class="section-header">🔍 Accident Analysis</div>',
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Accident Type</div>
                <div class="info-card-value">{analysis.get('accident_type', 'N/A')}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Victims</div>
                <div class="info-card-value">{analysis.get('victims', 'N/A')} people</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Ambulances Needed</div>
                <div class="info-card-value">{analysis.get('ambulances_needed', 'N/A')} units</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            services = analysis.get('services_needed', [])
            services_text = ", ".join(services) if services else "N/A"
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-label">Services Needed</div>
                <div class="info-card-value">{services_text}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="border-left-color:#ff8800;">
            <div class="info-card-label">⚡ Immediate Action Required</div>
            <div class="info-card-value">{analysis.get('immediate_actions', 'N/A')}</div>
        </div>""", unsafe_allow_html=True)

        # Accident Location Map
        if lat and lon:
            st.markdown('<div class="section-header">🌐 Accident Location</div>',
                        unsafe_allow_html=True)
            import pandas as pd
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=15)
            st.caption(f"📍 Coordinates: {round(lat, 5)}, {round(lon, 5)}")

        # Hospitals
        st.markdown('<div class="section-header">🏥 Nearby Hospitals</div>', unsafe_allow_html=True)

        if not hospitals:
            st.error(f"❌ No hospitals found even within 100 km of {location}. Please check the location name and try again.")
        else:
            if radius_expanded:
                st.warning(f"⚠️ No hospitals found within {radius} km. Automatically expanded search to **{radius_used} km** and found **{len(hospitals)} hospitals** (Top AI Matches highlighted).")
            else:
                st.success(f"✅ Found {len(hospitals)} hospitals within {radius_used} km of {location} (Top AI Matches highlighted).")
            import pandas as pd
            st.map(pd.DataFrame({
                "lat": [h["lat"] for h in hospitals],
                "lon": [h["lon"] for h in hospitals],
            }), zoom=13)

            for i, hospital in enumerate(hospitals):
                phone = hospital.get("phone")
                if phone:
                    phone_html = f'<div class="hospital-detail">📞 <a href="tel:{phone}" style="color:#4488ff; text-decoration:none;">{phone}</a></div>'
                else:
                    search_url = f"https://www.google.com/search?q={hospital['name'].replace(' ', '+')}+hospital+phone+number"
                    phone_html = f'<div class="hospital-detail">📞 <a href="{search_url}" target="_blank" style="color:#ff8800; text-decoration:none;">🔍 Find phone number</a></div>'

                maps_url = f"https://www.google.com/maps/search/{hospital['name'].replace(' ', '+')}"

                if hospital.get("best_match"):
                    highlight_style = "border-left: 4px solid #ffaa00; background: #221c08; box-shadow: 0 0 15px rgba(255, 170, 0, 0.25);"
                    badge_html = '<span style="background:#ffaa00; color:black; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:bold; margin-left:8px; vertical-align:middle;">🥇 BEST MATCH</span>'
                elif hospital.get("top_10"):
                    highlight_style = "border-left: 4px solid #44aaff; background: #1a202a; box-shadow: 0 0 10px rgba(68, 170, 255, 0.15);"
                    badge_html = '<span style="background:#44aaff; color:black; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:bold; margin-left:8px; vertical-align:middle;">🌟 TOP 10 MATCH</span>'
                else:
                    highlight_style = ""
                    badge_html = ""

                st.markdown(f"""
                <div class="hospital-card" style="{highlight_style}">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div style="flex:1;">
                            <div class="hospital-name">{i+1}. {hospital['name']}{badge_html}</div>
                            <div class="hospital-detail" style="margin:3px 0;">🏷️ {hospital['type']}</div>
                            {phone_html}
                            <div style="margin-top:8px;">
                                <a href="{maps_url}" target="_blank"
                                   style="color:#44cc88; font-size:0.8rem; text-decoration:none;">
                                    📍 View on Google Maps
                                </a>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div class="hospital-distance">{hospital['distance_km']} km</div>
                            <div class="hospital-detail">away</div>
                            <div class="hospital-detail" style="margin-top:8px; color:#ff8844; font-weight:600;">
                                ⏱️ ~{hospital.get('estimated_time_min', '?')} min
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Emergency Plan
        st.markdown('<div class="section-header">📋 Emergency Response Plan</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="plan-box">{plan}</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center; color:{MUTED}; font-size:0.8rem;">
            ⚠️ This is a simulation system for educational purposes only.<br>
            No real emergency services are notified. In a real emergency,
            call 112 (India) or your local emergency number.
        </div>
        """, unsafe_allow_html=True)


# ─── App Router ─────────────────────────────────────────────
if not st.session_state.get("connected"):
    show_login()
else:
    show_app()