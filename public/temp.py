import json
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

# --- YOUR DATA PROCESS ENGINE ---
def clean_and_embed_signal(y_vector, tau=12):
    b, a = butter(3, 0.08, btype='low', analog=False)
    smoothed_y = filtfilt(b, a, y_vector)
    signal_len = len(smoothed_y)
    max_shift = 2 * tau
    
    x_dim = smoothed_y[0 : signal_len - max_shift]
    y_dim = smoothed_y[tau : signal_len - tau]
    z_dim = smoothed_y[max_shift : signal_len]
    
    center_x = np.median(x_dim)
    center_y = np.median(y_dim)
    center_z = np.median(z_dim)
    
    distances = np.sqrt((x_dim - center_x)**2 + (y_dim - center_y)**2 + (z_dim - center_z)**2)
    max_dist = np.max(distances)
    
    wave_labels = []
    for idx, dist in enumerate(distances):
        if dist > max_dist * 0.35:
            wave_labels.append('QRS')
        elif dist > max_dist * 0.12:
            if x_dim[idx] > center_x:
                wave_labels.append('T Wave')
            else:
                wave_labels.append('P Wave')
        else:
            wave_labels.append('Baseline')
            
    return pd.DataFrame({
        'Time_Step': np.arange(len(x_dim)),
        'X': x_dim, 'Y': y_dim, 'Z': z_dim, 'Phase': wave_labels
    })

# --- EXECUTE ENGINE & GENERATE SMOOTH GEOMETRIC BRIDGES ---
df_raw = pd.read_csv("data/kaggle_ecg/s0141lre.csv")
y_vector = df_raw['ii'].values[:2400]
df_3d = clean_and_embed_signal(y_vector, tau=12)

web_data = []
steps = len(df_3d)

for i in range(steps):
    current_row = df_3d.iloc[i]
    
    # Append the primary tracking coordinate point
    web_data.append({
        "index": int(current_row['Time_Step']),
        "raw": float(current_row['X']),
        "x": float(current_row['X']),
        "y": float(current_row['Y']),
        "z": float(current_row['Z']),
        "phase": str(current_row['Phase'])
    })
    
    # GEOMETRIC SUB-SAMPLING: If the next point changes phases, inject an intermediate bridge point
    if i < steps - 1:
        next_row = df_3d.iloc[i + 1]
        if current_row['Phase'] != next_row['Phase']:
            # Create a 50/50 blend point halfway between them to catch the WebGL vertex color interpolation
            web_data.append({
                "index": int(current_row['Time_Step']),
                "raw": float((current_row['X'] + next_row['X']) / 2),
                "x": float((current_row['X'] + next_row['X']) / 2),
                "y": float((current_row['Y'] + next_row['Y']) / 2),
                "z": float((current_row['Z'] + next_row['Z']) / 2),
                "phase": str(next_row['Phase']) # Group it smoothly with the incoming phase color
            })

with open("public/ecg_data.json", "w") as f:
    json.dump(web_data, f)

print("Exported enhanced phase-labeled vectors with geometric gradient patches!")