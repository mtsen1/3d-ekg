import streamlit as st
import plotly.graph_objects as go
import os
import sys
import time
import numpy as np

# Force Python to look inside the 'src' directory for your custom modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from modern_topology import extract_digital_phase_space

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="3D ECG High-Performance Dashboard")

# 2. SEAMLESS PRESENTATION CSS: Pure white panel with ambient halo glow
st.markdown("""
    <style>
        /* Hide default Streamlit header artifacts */
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        
        /* Force root application background canvas to pure white */
        .stApp {
            background-color: #FFFFFF !important; 
        }

        /* Main floating white presentation dashboard card */
        .block-container {
            padding: 3rem 4rem !important;
            max-width: 90% !important;
            margin-top: 2rem;
            background-color: #FFFFFF !important; 
            border-radius: 32px !important; 
            
            /* Multi-layered quadrant ambient rainbow shadow */
            box-shadow: 
                -30px -30px 80px rgba(255, 75, 75, 0.18),    
                -30px 30px 80px rgba(0, 242, 254, 0.22),     
                30px 30px 80px rgba(0, 230, 118, 0.15),      
                30px -30px 80px rgba(255, 165, 0, 0.18)      
                !important; 
        }
        
        /* High-contrast slate typography */
        p, span, label, h3 { color: #1A202C !important; }
        
        /* Center Separation Column Accent Line */
        .divider-line {
            border-left: 1px solid #E2E8F0;
            height: 650px;
            margin-left: 10px;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Phase-locked color spectrum background generator
def get_phase_color(percentage):
    if percentage < 20: return "rgba(71, 41, 184, 0.05)"    
    elif percentage < 45: return "rgba(0, 180, 216, 0.05)"   
    elif percentage < 70: return "rgba(0, 230, 118, 0.05)"   
    else: return "rgba(255, 61, 0, 0.05)"                    

# Split page components cleanly into functional layout columns
left_col, center_spacer, right_col = st.columns([1, 0.05, 3.2])

with left_col:
    st.markdown("### **3D ECG Waveform**<br><span style='font-size:18px; color:#718096 !important;'>Visualization Panel</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("**File Input:**")
    target_file = st.text_input(label="Path", value="data/kaggle_ecg/s0141lre.csv", label_visibility="collapsed")
    st.caption("Supported formats: `.csv`, `.tif` via extraction layer.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("**Sliders:**")
    param_tau = st.slider("Step (τ)", min_value=5, max_value=40, value=22)
    param_samples = st.slider("Window Length", min_value=500, max_value=3000, value=1500)

with center_spacer:
    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

with right_col:
    if os.path.exists(target_file):
        topology_df = extract_digital_phase_space(
            csv_path=target_file,
            lead_column='ii',
            num_samples=param_samples
        )
        
        total_points = len(topology_df)
        
        # Initialize animation state management variables in session memory
        if 'animation_on' not in st.session_state:
            st.session_state.animation_on = False
        if 'timeline_step' not in st.session_state:
            st.session_state.timeline_step = 10

        # Set fixed axis scale boundaries based on data limits
        x_min, x_max = float(topology_df['X'].min()*1.2), float(topology_df['X'].max()*1.2)
        y_min, y_max = float(topology_df['Y'].min()*1.2), float(topology_df['Y'].max()*1.2)
        z_min, z_max = float(topology_df['Z'].min()*1.2), float(topology_df['Z'].max()*1.2)

        # -------------------------------------------------------------
        # NATIVE STREAMLIT FRAGMENT: Isolates the loop rendering pipeline
        # -------------------------------------------------------------
        @st.fragment
        def render_animated_canvas():
            st.markdown("**Media Playback Engine:**")
            play_col1, play_col2, play_col3 = st.columns([1, 1, 4])
            
            with play_col1:
                play_btn = st.button("▶ Play", width='stretch')
            with play_col2:
                pause_btn = st.button("⏸ Pause", width='stretch')
            with play_col3:
                # Scrubber acts as a real-time monitor or fallback controller
                current_step = st.slider(
                    label="Timeline Scrubber",
                    min_value=10,
                    max_value=total_points - 1,
                    value=st.session_state.timeline_step,
                    step=15,
                    label_visibility="collapsed"
                )
            
            # Handle user interaction inputs smoothly
            if play_btn:
                st.session_state.animation_on = True
            if pause_btn:
                st.session_state.animation_on = False
            if not play_btn and not pause_btn:
                st.session_state.timeline_step = current_step

            # Initialize empty presentation viewport slots
            chart_slot = st.empty()
            timeline_slot = st.empty()

            # ANIMATION DRIVER LOOP
            if st.session_state.animation_on:
                for idx in range(st.session_state.timeline_step, total_points - 1, 35):
                    st.session_state.timeline_step = idx
                    
                    active_trail = topology_df.iloc[:idx]
                    pct = topology_df['Timeline'].iloc[idx]
                    glow = get_phase_color(pct)
                    
                    # Draw 3D Attractor Wave
                    f3d = go.Figure(data=go.Scatter3d(
                        x=active_trail['X'], y=active_trail['Y'], z=active_trail['Z'],
                        mode='lines', line=dict(color=active_trail['Timeline'], colorscale='Turbo', width=5)
                    ))
                    f3d.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=440, showlegend=False,
                        scene=dict(
                            bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Signal State, x(t)", range=[x_min, x_max], autorange=False),
                            yaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Phase Vector", range=[y_min, y_max], autorange=False),
                            zaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Velocity Vector", range=[z_min, z_max], autorange=False)
                        ),
                        uirevision='constant'
                    )
                    chart_slot.plotly_chart(f3d, width='stretch', config={'displayModeBar': False})
                    
                    # Draw 2D Waveform Tracker
                    f2d = go.Figure()
                    f2d.add_trace(go.Scatter(x=np.arange(total_points), y=topology_df['Raw_Signal'], mode='lines', line=dict(color='#2D3748', width=2), hoverinfo='skip'))
                    f2d.add_shape(type="line", x0=idx, y0=min(topology_df['Raw_Signal']) * 1.2, x1=idx, y1=max(topology_df['Raw_Signal']) * 1.2, line=dict(color="#FF4B4B", width=2.5))
                    f2d.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=glow, margin=dict(l=0, r=0, b=0, t=0), height=130, showlegend=False,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, total_points]),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    )
                    timeline_slot.plotly_chart(f2d, width='stretch', config={'displayModeBar': False})
                    
                    time.sleep(0.01)
                
                # Turn off animation flag upon stream completion cleanly
                st.session_state.animation_on = False
                st.rerun()
            else:
                # STATIC RENDER MODE
                playback_index = st.session_state.timeline_step
                active_trail = topology_df.iloc[:playback_index]
                current_glow_color = get_phase_color(topology_df['Timeline'].iloc[playback_index])

                f3d = go.Figure(data=go.Scatter3d(
                    x=active_trail['X'], y=active_trail['Y'], z=active_trail['Z'],
                    mode='lines', line=dict(color=active_trail['Timeline'], colorscale='Turbo', width=5)
                ))
                f3d.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), height=440, showlegend=False,
                    scene=dict(
                        bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Signal State, x(t)", range=[x_min, x_max]),
                        yaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Phase Vector", range=[y_min, y_max]),
                        zaxis=dict(gridcolor="rgba(0,0,0,0.05)", title="Velocity Vector", range=[z_min, z_max])
                    ),
                    uirevision='constant'
                )
                chart_slot.plotly_chart(f3d, width='stretch', config={'displayModeBar': False})

                f2d = go.Figure()
                f2d.add_trace(go.Scatter(x=np.arange(total_points), y=topology_df['Raw_Signal'], mode='lines', line=dict(color='#2D3748', width=2), hoverinfo='skip'))
                f2d.add_shape(type="line", x0=playback_index, y0=min(topology_df['Raw_Signal']) * 1.2, x1=playback_index, y1=max(topology_df['Raw_Signal']) * 1.2, line=dict(color="#FF4B4B", width=2.5))
                f2d.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=current_glow_color, margin=dict(l=0, r=0, b=0, t=0), height=130, showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, total_points]),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
                timeline_slot.plotly_chart(f2d, width='stretch', config={'displayModeBar': False})

        # Call the isolated fragment engine loop cleanly
        render_animated_canvas()

        # Lower UI labels overlay bar elements
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; color: #718096; font-size: 13px; margin-top: 10px;">
                <div>⚡ Fragment Isolated State Management Architecture Active</div>
                <div>1x &nbsp;&nbsp; 2x &nbsp;&nbsp; 🔄</div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error(f"Target file not located at: {target_file}")