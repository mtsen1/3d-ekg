import cv2
import numpy as np
import os

def extract_ecg_signal(image_path):
    """
    Processes a historical or grayscale ECG scan, filters out grid lines,
    and isolates the heartbeat line down to a 1-pixel wide skeleton path.
    """
    # 1. Load the image as grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at path: {image_path}")

    # 2. Binarization via Otsu's Thresholding
    # Converts the image into binary (pure black and white). 
    # THRESH_BINARY_INV turns the ink WHITE and the background BLACK.
    _, thresh = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Create a small cross-shaped kernel to punch holes in grid intersections
    break_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_ERODE, break_kernel, iterations=1)

    # Create a kernel that is 1 pixel wide and 5 pixels tall
    # This reinforces vertical continuity while stripping away horizontal "branches"
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
    
    # 3. Filter out the Grid using Connected Components Area Analysis
    
    # Loop through every detected shape (index 0 is the black background, so we skip it)
    # 3. Filter out the Grid using Area AND Aspect Ratio
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    clean_signal = np.zeros_like(thresh)
    
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]
        
        # Calculate aspect ratio (width divided by height)
        aspect_ratio = width / float(height) if height > 0 else 0
        
        # CRITERIA 1: It must be large enough to be a signal line
        # CRITERIA 2: It must be taller than it is wide (aspect_ratio < 1.0)
        # These lingering horizontal bars have a massive aspect ratio (e.g., 5.0 or 10.0)
        if area > 50 and aspect_ratio < 0.8:  
            clean_signal[labels == i] = 255

    # 4. Optional: Close minor micro-gaps in the signal line left by the grid removal
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed_signal = cv2.morphologyEx(clean_signal, cv2.MORPH_CLOSE, kernel)

    # 5. Line Skeletonization (Thinning)
    # Collapses the remaining thick stroke down to a 1-pixel-wide path
    skeleton = cv2.ximgproc.thinning(closed_signal)
    
    return skeleton


if __name__ == "__main__":
    # --- Local Testing Block ---
    # Dynamically builds the absolute path to your file to avoid Windows CWD bugs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Points to your 'data' folder up one directory level
    test_path = os.path.join(script_dir, "..", "data", "grey_0001.tif")
    
    print(f"Current Script Directory: {script_dir}")
    print(f"Looking for image at: {test_path}\n")
    
    try:
        # Run the updated CV processing logic
        print("Processing pipeline running...")
        result_skeleton = extract_ecg_signal(test_path)
        
        # Display the output to visually confirm the brick grid is gone
        cv2.imshow("Filtered Archival Signal", result_skeleton)
        
        print("\n[SUCCESS] Pipeline executed perfectly!")
        print(" -> Click into the pop-up window and press ANY key to exit.")
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except FileNotFoundError as fnf:
        print(f"[ERROR] {fnf}")
        print("Please check that your image file matches the name and directory structure.")
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}")