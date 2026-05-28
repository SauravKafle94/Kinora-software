import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from collections import deque

# --- CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Kinora Dashboard: Ambient Care Monitoring",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme aesthetics
st.markdown("""
    <style>
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
    .alert-card {
        background-color: #3b0000;
        border: 2px solid #FF4B4B !important;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    st.markdown("Adjust parameters for the pitch demo.")
    sim_speed = st.slider("Update Interval (seconds)", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
    
    st.markdown("---")
    st.subheader("🚨 Emergency Override")
    force_fall = st.button("TRIGGER FALL ALARM", type="primary", use_container_width=True)
    reset_fall = st.button("Reset System Status", use_container_width=True)

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

# --- HEADER ---
st.title("Kinora Dashboard: Ambient Care Monitoring")
st.markdown("Real-time privacy-preserving mmWave radar telemetry without cameras.")

# If fall is detected, show massive warning
if st.session_state.fall_detected:
    st.error("⚠️ **CRITICAL ALERT: FALL DETECTED!** Immediate assistance required in Living Room. ⚠️", icon="🚨")

# --- SIMULATION DATA GENERATION ---
current_time = time.time()
# Smooth out the vital signs slightly so it looks somewhat realistic (random walk)
last_hr = st.session_state.hr_history[-1]
last_br = st.session_state.br_history[-1]

current_hr = np.clip(last_hr + np.random.randint(-3, 4), 60, 80)
current_br = np.clip(last_br + np.random.randint(-1, 2), 12, 20)

st.session_state.time_history.append(current_time)
st.session_state.hr_history.append(current_hr)
st.session_state.br_history.append(current_br)

def generate_point_cloud():
    """Generates a 3D point cloud simulating a human shape based on fall status."""
    # Base position (Center of the room)
    base_x = np.random.normal(0, 0.05)
    base_y = np.random.normal(2, 0.05) # 2 meters away from sensor
    
    num_points = 150
    
    if st.session_state.fall_detected:
        # Fallen position: low Z (height), spread out across X/Y (floor)
        x = np.random.normal(base_x, 0.5, num_points)
        y = np.random.normal(base_y, 0.6, num_points)
        z = np.random.normal(0.2, 0.15, num_points) # Close to ground
    else:
        # Standing position: high Z, concentrated X/Y
        x = np.random.normal(base_x, 0.25, num_points)
        y = np.random.normal(base_y, 0.2, num_points)
        z = np.random.normal(1.0, 0.4, num_points) # Standing height (approx 1m center)

    return pd.DataFrame({'x': x, 'y': y, 'z': z})

# --- UI LAYOUT ---
# 1. Metrics Row
metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

with metrics_col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Heart Rate</div>
            <div class="metric-value" style="color: #FF4B4B;">{int(current_hr)} <span style="font-size: 1.5rem;">BPM</span></div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Breathing Rate</div>
            <div class="metric-value" style="color: #00B4D8;">{int(current_br)} <span style="font-size: 1.5rem;">RPM</span></div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col3:
    status_color = "#FF4B4B" if st.session_state.fall_detected else "#00E676"
    status_text = "FALL DETECTED" if st.session_state.fall_detected else "NORMAL"
    status_class = "metric-card alert-card" if st.session_state.fall_detected else "metric-card"
    st.markdown(f"""
        <div class="{status_class}" style="border-color: {status_color};">
            <div class="metric-label">System Status</div>
            <div class="metric-value" style="color: {status_color}; font-size: 2.5rem; margin-top: 10px;">{status_text}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. Charts Row
col_charts1, col_charts2 = st.columns([1, 1])

with col_charts1:
    st.subheader("📈 Real-Time Vitals")
    
    # Prepare data for Plotly
    df_vitals = pd.DataFrame({
        'Time': st.session_state.time_history, 
        'HR': st.session_state.hr_history,
        'BR': st.session_state.br_history
    })
    # Convert timestamps to relative seconds for display
    df_vitals['Seconds Ago'] = df_vitals['Time'].apply(lambda t: round(current_time - t, 1))
    
    # Heart Rate Line Chart
    fig_hr = px.line(df_vitals, x='Seconds Ago', y='HR', 
                     color_discrete_sequence=['#FF4B4B'])
    fig_hr.update_layout(
        xaxis_autorange="reversed", 
        margin=dict(l=0, r=0, t=10, b=0), 
        height=220,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Seconds Ago",
        yaxis_title="BPM",
        yaxis=dict(range=[50, 90])
    )
    st.plotly_chart(fig_hr, use_container_width=True)

    # Breathing Rate Line Chart
    fig_br = px.line(df_vitals, x='Seconds Ago', y='BR', 
                     color_discrete_sequence=['#00B4D8'])
    fig_br.update_layout(
        xaxis_autorange="reversed", 
        margin=dict(l=0, r=0, t=10, b=0), 
        height=220,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Seconds Ago",
        yaxis_title="RPM",
        yaxis=dict(range=[8, 24])
    )
    st.plotly_chart(fig_br, use_container_width=True)

with col_charts2:
    st.subheader("🌐 Live Spatial Mapping (mmWave)")
    pc_data = generate_point_cloud()
    
    # 3D Scatter Plot
    fig_pc = px.scatter_3d(pc_data, x='x', y='y', z='z', 
                           color='z', color_continuous_scale='teal',
                           opacity=0.8)
    
    # Fix axis ranges so the room doesn't "jump" around
    fig_pc.update_layout(
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5], title='X (m)', backgroundcolor="#1E1E1E"),
            yaxis=dict(range=[0, 4], title='Y - Distance (m)', backgroundcolor="#1E1E1E"),
            zaxis=dict(range=[0, 2.0], title='Z - Height (m)', backgroundcolor="#1E1E1E"),
            aspectmode='manual',
            aspectratio=dict(x=1, y=2, z=1) # Makes the room look more proportional
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    # Hide the colorbar for a cleaner look
    fig_pc.update_coloraxes(showscale=False)
    
    st.plotly_chart(fig_pc, use_container_width=True)

# 3. Trigger next update loop
time.sleep(sim_speed)
st.rerun()
