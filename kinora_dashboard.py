import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from collections import deque

# --- CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Kinora Dashboard: Ambient Care Monitoring",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme aesthetics & UX polish
st.markdown("""
    <style>
    /* Hide Streamlit elements for a clean, app-like feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the Streamlit 'running' animation in the top right */
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }

    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 3.5rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-baseline {
        font-size: 0.9rem;
        color: #888888;
        margin-top: 5px;
        font-style: italic;
    }
    
    /* Hero Banner Styles */
    .hero-banner-normal {
        background-color: rgba(0, 230, 118, 0.1);
        border: 1px solid #00E676;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
        color: #00E676;
    }
    .hero-banner-alert {
        background-color: #3b0000;
        border: 2px solid #FF4B4B !important;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
        color: #FF4B4B;
        animation: hero-pulse 1.5s infinite;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: bold;
        letter-spacing: 2px;
        margin: 0;
    }
    
    @keyframes hero-pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png", width=10) # Spacer
    st.header("Navigation")
    st.markdown("🏡 **Room 102** - Active")
    st.markdown("---")
    
    st.subheader("🚨 Emergency Override")
    force_fall = st.button("TRIGGER FALL ALARM", type="primary", use_container_width=True)
    reset_fall = st.button("Reset System Status", use_container_width=True)
    
    st.markdown("---")
    
    # Hide developer tools in an expander
    with st.expander("⚙️ Developer Controls"):
        st.markdown("Adjust simulation parameters.")
        sim_speed = st.slider("Update Interval (sec)", min_value=0.1, max_value=2.0, value=1.0, step=0.1)

# State Management for fall detection
if 'fall_detected' not in st.session_state:
    st.session_state.fall_detected = False

if force_fall:
    st.session_state.fall_detected = True
if reset_fall:
    st.session_state.fall_detected = False

# State Management for data history (approx. last 30 readings)
if 'hr_history' not in st.session_state:
    st.session_state.hr_history = deque(maxlen=30)
    st.session_state.br_history = deque(maxlen=30)
    st.session_state.time_history = deque(maxlen=30)
    
    # Pre-fill with baseline data
    now = time.time()
    for i in range(30):
        st.session_state.time_history.append(now - (30 - i) * sim_speed)
        st.session_state.hr_history.append(np.random.randint(60, 81))
        st.session_state.br_history.append(np.random.randint(12, 21))

# --- SIMULATION DATA GENERATION ---
current_time = time.time()
last_hr = st.session_state.hr_history[-1]
last_br = st.session_state.br_history[-1]

# Random walk for more realistic vital sign fluctuations
current_hr = np.clip(last_hr + np.random.randint(-3, 4), 60, 80)
current_br = np.clip(last_br + np.random.randint(-1, 2), 12, 20)

st.session_state.time_history.append(current_time)
st.session_state.hr_history.append(current_hr)
st.session_state.br_history.append(current_br)

def generate_point_cloud():
    """Generates a 3D point cloud simulating a human shape based on fall status."""
    base_x = np.random.normal(0, 0.05)
    base_y = np.random.normal(2, 0.05) # Centered around 2 meters away
    
    num_points = 150
    
    if st.session_state.fall_detected:
        # Fallen: low to the ground, spread out
        x = np.random.normal(base_x, 0.5, num_points)
        y = np.random.normal(base_y, 0.6, num_points)
        z = np.random.normal(0.2, 0.15, num_points) 
    else:
        # Standing/Sitting: taller, concentrated
        x = np.random.normal(base_x, 0.25, num_points)
        y = np.random.normal(base_y, 0.2, num_points)
        z = np.random.normal(1.0, 0.4, num_points) 

    return pd.DataFrame({'x': x, 'y': y, 'z': z})

# Calculate trend arrows
hr_trend = "↑" if current_hr > last_hr else ("↓" if current_hr < last_hr else "→")
br_trend = "↑" if current_br > last_br else ("↓" if current_br < last_br else "→")

# --- HEADER & HERO STATUS ---
st.title("Kinora Dashboard")
st.markdown("Real-time privacy-preserving mmWave radar telemetry without optical cameras.")

# The 2-Second Rule: Massive Hero Banner for System Status
if st.session_state.fall_detected:
    st.markdown("""
        <div class="hero-banner-alert">
            <h1 class="hero-title">⚠️ CRITICAL: FALL DETECTED</h1>
            <p style="margin:0; font-size: 1.2rem;">Immediate assistance required in Room 102</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="hero-banner-normal">
            <h1 class="hero-title">✅ SYSTEM NORMAL</h1>
            <p style="margin:0; font-size: 1.2rem;">Active monitoring via mmWave sensors</p>
        </div>
    """, unsafe_allow_html=True)

# --- UI LAYOUT ---
# 1. Metrics Row (Now 2 columns instead of 3)
metrics_col1, metrics_col2 = st.columns(2)

with metrics_col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Heart Rate</div>
            <div class="metric-value" style="color: #FF4B4B;">
                {int(current_hr)} <span style="font-size: 1.5rem;">BPM {hr_trend}</span>
            </div>
            <div class="metric-baseline">30-Day Avg: 72 BPM</div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Breathing Rate</div>
            <div class="metric-value" style="color: #00B4D8;">
                {int(current_br)} <span style="font-size: 1.5rem;">RPM {br_trend}</span>
            </div>
            <div class="metric-baseline">30-Day Avg: 16 RPM</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. Charts Row
col_charts1, col_charts2 = st.columns([1, 1])

with col_charts1:
    st.subheader("📈 Real-Time Vitals")
    
    df_vitals = pd.DataFrame({
        'Time': st.session_state.time_history, 
        'HR': st.session_state.hr_history,
        'BR': st.session_state.br_history
    })
    # Convert timestamps to relative seconds for display
    df_vitals['Seconds Ago'] = df_vitals['Time'].apply(lambda t: round(current_time - t, 1))
    
    # Heart Rate Chart
    fig_hr = px.line(df_vitals, x='Seconds Ago', y='HR', color_discrete_sequence=['#FF4B4B'])
    fig_hr.update_layout(
        xaxis_autorange="reversed", margin=dict(l=0, r=0, t=10, b=0), height=220,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Seconds Ago", yaxis_title="BPM", yaxis=dict(range=[50, 90])
    )
    st.plotly_chart(fig_hr, use_container_width=True)

    # Breathing Rate Chart
    fig_br = px.line(df_vitals, x='Seconds Ago', y='BR', color_discrete_sequence=['#00B4D8'])
    fig_br.update_layout(
        xaxis_autorange="reversed", margin=dict(l=0, r=0, t=10, b=0), height=220,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Seconds Ago", yaxis_title="RPM", yaxis=dict(range=[8, 24])
    )
    st.plotly_chart(fig_br, use_container_width=True)

with col_charts2:
    st.subheader("🌐 De-identified Spatial Telemetry (Zero-Camera)")
    pc_data = generate_point_cloud()
    
    fig_pc = go.Figure()
    
    # Trace 1: The Human Subject (Point Cloud)
    fig_pc.add_trace(go.Scatter3d(
        x=pc_data['x'], y=pc_data['y'], z=pc_data['z'],
        mode='markers',
        marker=dict(size=4, color=pc_data['z'], colorscale='teal', opacity=0.8),
        name="Subject Signature"
    ))
    
    # Trace 2: Static Wireframe Context (Representing a Bed/Chair bounding box)
    # Define corners of a simple box (x: -0.6 to 0.6, y: 1.5 to 2.5, z: 0 to 0.5)
    bx, by, bz = [-0.6, 0.6, 0.6, -0.6, -0.6], [1.5, 1.5, 2.5, 2.5, 1.5], [0.0, 0.0, 0.0, 0.0, 0.0] # Bottom face
    tx, ty, tz = [-0.6, 0.6, 0.6, -0.6, -0.6], [1.5, 1.5, 2.5, 2.5, 1.5], [0.5, 0.5, 0.5, 0.5, 0.5] # Top face
    
    # Connect bottom and top faces with vertical lines
    vx1, vy1, vz1 = [-0.6, -0.6, None], [1.5, 1.5, None], [0.0, 0.5, None]
    vx2, vy2, vz2 = [0.6, 0.6, None], [1.5, 1.5, None], [0.0, 0.5, None]
    vx3, vy3, vz3 = [0.6, 0.6, None], [2.5, 2.5, None], [0.0, 0.5, None]
    vx4, vy4, vz4 = [-0.6, -0.6, None], [2.5, 2.5, None], [0.0, 0.5, None]
    
    wire_x = bx + [None] + tx + [None] + vx1 + vx2 + vx3 + vx4
    wire_y = by + [None] + ty + [None] + vy1 + vy2 + vy3 + vy4
    wire_z = bz + [None] + tz + [None] + vz1 + vz2 + vz3 + vz4
    
    fig_pc.add_trace(go.Scatter3d(
        x=wire_x, y=wire_y, z=wire_z,
        mode='lines',
        line=dict(color='rgba(255, 255, 255, 0.25)', width=3),
        name="Room Context (Bed)"
    ))
    
    # Layout fixing
    fig_pc.update_layout(
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5], title='X (m)', backgroundcolor="#1E1E1E"),
            yaxis=dict(range=[0, 4], title='Y - Distance (m)', backgroundcolor="#1E1E1E"),
            zaxis=dict(range=[0, 2.0], title='Z - Height (m)', backgroundcolor="#1E1E1E"),
            aspectmode='manual',
            aspectratio=dict(x=1, y=2, z=1)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)")
    )
    
    st.plotly_chart(fig_pc, use_container_width=True)

# 3. Trigger next update loop
time.sleep(sim_speed)
st.rerun()
