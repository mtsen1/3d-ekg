import plotly.graph_objects as go
import os
import sys

# Maintain your path appending code...
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.modern_vcg import extract_digital_phase_space

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_target_path = os.path.join(script_dir, "..", "data", "kaggle_ecg", "s0141lre.csv")    

    try:
        print("Ingesting high-resolution digital data stream...")
        embedded_topology = extract_digital_phase_space(
            csv_path=csv_target_path,
            lead_column='ii', 
            start_sample=0,
            # -------------------------------------------------------------
            # ADJUST YOUR CYCLE COUNT HERE:
            # At a 1000Hz sampling rate, 1000 samples is roughly 1 second of data.
            # - 1200 samples will show ~1.5 heartbeats (Beautiful overlap)
            # - 2500 samples will show ~3 full consecutive cardiac cycles
            # -------------------------------------------------------------
            num_samples=2200 
        )
        
        print("Constructing 3D Spatiotemporal Phase Space Canvas...")
        
        # Build the single continuous 3D line trace natively using Graph Objects
        fig = go.Figure(data=go.Scatter3d(
            x=embedded_topology['X'],
            y=embedded_topology['Y'],
            z=embedded_topology['Z'],
            mode='lines',
            line=dict(
                color=embedded_topology['Timeline'], # Map color smoothly to our timeline array
                colorscale='Turbo',                 # The beautiful, fluid rainbow spectrum
                width=5.5                           # Give it a nice, crisp ribbon thickness
            )
        ))
        
        # Configure layout, labels, and hide the color scale bar
        fig.update_layout(
            title="Digital Health Science: Continuous Phase-Locked 3D Attractor",
            height=850,
            margin=dict(l=0, r=0, b=0, t=40),
            scene=dict(
                xaxis_title='Signal State, x(t)',
                yaxis_title='Phase Shifted Orthogonal Vector',
                zaxis_title='Signal Velocity Vector',
                xaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)"),
                yaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)"),
                zaxis=dict(gridcolor="rgba(180, 200, 230, 0.25)")
            ),
            # RE-ENABLE COLOR SCALE TO ACT AS A DIAGNOSTIC LEGEND
            coloraxis=dict(
                colorscale='Turbo',
                showscale=True,
                colorbar=dict(
                    title="Cardiac Phase Vector",
                    tickvals=[15, 50, 85],
                    ticktext=["P Wave Domain", "QRS Target Zone", "T Wave Domain"]
                )
            )
        )
        
        print("Launching interactive browser visualization panel...")
        fig.show()

    except Exception as err:
        print(f"Pipeline execution halted: {err}")
        print("\n💡 Confirm that your file exists in your data/ folder and that the column key matches your headers!")