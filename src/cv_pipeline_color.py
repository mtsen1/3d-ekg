import cv2
import numpy as np
import os

def extract_clean_ecg(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at: {image_path}")
    
    # 1. Smooth slightly to eliminate compression artifacts
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # 2. OPTIMIZED THRESHOLD: Raised to 140 to keep thin R-wave peaks intact
    _, thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY_INV)
    
    # 3. DIGITAL GLUE: Morphological Close
    # This bridges micro-gaps to ensure peaks stay welded to the baseline
    glue_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, glue_kernel)

    # 4. FILTER BY SIZE & GEOMETRY
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
    clean_signal = np.zeros_like(thresh)
    
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]
        
        # Lowered area threshold to 60 so we don't drop legitimate waves
        if area > 60:  
            # Secondary check: If it's a floating letter like "aVL", 
            # its width and height will be almost equal (square bounding box).
            # Legitimate signal components are much longer than they are tall, or vice versa.
            if width > 50 or height > 30:
                clean_signal[labels == i] = 255
            
    # 5. SKELETONIZATION
    skeleton = cv2.ximgproc.thinning(clean_signal)
    return thresh, clean_signal, skeleton

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(script_dir, "..", "data", "red_0001_v2.tif")
    
    try:
        thresh, clean, skeleton = extract_clean_ecg(test_path)
        
        # Display the crucial check stages side by side
        cv2.imshow("1. Binary Canvas (Check if peaks are attached)", thresh)
        cv2.imshow("2. Filtered Signal (Check if text dropped but peaks stayed)", clean)
        cv2.imshow("3. Final 1-Pixel Trajectory", skeleton)
        
        print("[SUCCESS] Look closely at Window 1 to ensure the spikes are fully connected!")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error: {e}")