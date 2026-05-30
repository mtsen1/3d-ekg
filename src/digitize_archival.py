import cv2
import numpy as np
import pandas as pd
import os

def extract_clean_ecg(image_path):
    """Isolates the 1-pixel raw heartbeat trail from the paper image."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at: {image_path}")
    
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY_INV)
    
    glue_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, glue_kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    clean_signal = np.zeros_like(thresh)
    
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]
        
        if area > 60:  
            if width > 50 or height > 30:
                clean_signal[labels == i] = 255
            
    skeleton = cv2.ximgproc.thinning(clean_signal)
    return skeleton

def extract_1d_vector(skeleton_image, start_x=120, end_x=None):
    """Scans the skeleton left-to-right to extract raw numerical Y voltage coordinates."""
    height, width = skeleton_image.shape
    if end_x is None:
        end_x = width
        
    y_values = []
    
    for x in range(start_x, end_x):
        white_pixels = np.where(skeleton_image[:, x] == 255)[0]
        if len(white_pixels) > 0:
            # Invert Y so up on the image translates to a positive voltage value
            inverted_y = height - np.mean(white_pixels)
            y_values.append(inverted_y)
        else:
            if len(y_values) > 0:
                y_values.append(y_values[-1]) # Forward-fill gaps if the line drops out
                
    return np.array(y_values)

if __name__ == "__main__":
    # Setup our standardized root project directory bounds
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Target your raw image strip input path
    image_target_path = os.path.join(script_dir, "..", "data", "red_0001_v3.tif")
    
    # Define our output spreadsheet destination path
    output_folder = os.path.join(script_dir, "..", "data", "archival_ecg")
    os.makedirs(output_folder, exist_ok=True) # Automatically create directory if missing
    csv_output_path = os.path.join(output_folder, "processed_strip.csv")
    
    try:
        print("Step 1: Ingesting raw archival scan and running skeletonization transform...")
        skeleton_trace = extract_clean_ecg(image_target_path)
        
        print("Step 2: Scanning pixel grid to extract 1D numerical voltage vector...")
        raw_voltage_vector = extract_1d_vector(skeleton_trace, start_x=120)
        
        print(f"Step 3: Packaging {len(raw_voltage_vector)} coordinates into a data matrix...")
        # Pack the array into a clean table dataframe
        export_df = pd.DataFrame({
            'sample_index': np.arange(len(raw_voltage_vector)),
            'voltage': raw_voltage_vector
        })
        
        # Save out to disk as a clean comma-separated table
        export_df.to_csv(csv_output_path, index=False)
        print(f"\n[SUCCESS] Extracted data saved smoothly to:\n---> {os.path.abspath(csv_output_path)}")
        
    except Exception as err:
        print(f"\n[EXTRACTION FAILED]: {err}")