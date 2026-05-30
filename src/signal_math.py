import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

def extract_1d_vector(skeleton_image, start_x=120, end_x=None):
    """
    Scans the skeleton image left-to-right to extract the raw Y-coordinates.
    Slices out the calibration box on the left by starting at 'start_x'.
    """
    height, width = skeleton_image.shape
    if end_x is None:
        end_x = width
        
    y_values = []
    
    for x in range(start_x, end_x):
        white_pixels = np.where(skeleton_image[:, x] == 255)[0]
        if len(white_pixels) > 0:
            inverted_y = height - np.mean(white_pixels)
            y_values.append(inverted_y)
        else:
            if len(y_values) > 0:
                y_values.append(y_values[-1])
                
    return np.array(y_values)

def clean_and_embed_signal(y_vector, tau=12):
    """
    Smooths the signal, embeds it into 3D space, and accurately maps 
    cardiac phases by calculating coordinate distances from the resting baseline center.
    """
    # 1. Low-pass filter to smooth out pixel stepping
    b, a = butter(3, 0.08, btype='low', analog=False)
    smoothed_y = filtfilt(b, a, y_vector)
    
    signal_len = len(smoothed_y)
    max_shift = 2 * tau
    
    # 2. Extract Phase Space Dimensions
    x_dim = smoothed_y[0 : signal_len - max_shift]
    y_dim = smoothed_y[tau : signal_len - tau]
    z_dim = smoothed_y[max_shift : signal_len]
    
    # 3. Dynamic Center Detection
    center_x = np.median(x_dim)
    center_y = np.median(y_dim)
    center_z = np.median(z_dim)
    
    # Calculate spatial distances from the resting baseline node
    distances = np.sqrt((x_dim - center_x)**2 + (y_dim - center_y)**2 + (z_dim - center_z)**2)
    max_dist = np.max(distances)
    
    wave_labels = []
    for idx, dist in enumerate(distances):
        # Far outliers = QRS complex
        if dist > max_dist * 0.35:
            wave_labels.append('QRS Complex (Ventricle Contraction)')
        # Mid-tier expansions = P or T wave depending on slope orientation
        elif dist > max_dist * 0.12:
            if x_dim[idx] > center_x:
                wave_labels.append('T Wave (Ventricle Resting)')
            else:
                wave_labels.append('P Wave (Atrial Contraction)')
        else:
            wave_labels.append('Baseline')
            
    # Pack into DataFrame with an explicit chronological tracking index
    df_3d = pd.DataFrame({
        'Time_Step': np.arange(len(x_dim)),
        'X': x_dim,
        'Y': y_dim,
        'Z': z_dim,
        'Phase': wave_labels
    })
    
    return df_3d