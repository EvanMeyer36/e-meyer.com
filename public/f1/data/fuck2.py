import cv2
import os

# Replace with the path to your video file
video_path = input("Please enter video path: ")

# Replace with the output folder where the image sequence will be saved
output_folder = input("Please enter output folder")

os.makedirs(output_folder, exist_ok=True)

# Open the video file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Unable to open video file '{video_path}'")
else:
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save the frame as an image
        frame_filename = os.path.join(output_folder, f"frame_{frame_number:04d}.png")
        cv2.imwrite(frame_filename, frame)
        
        frame_number += 1
    
    cap.release()
    print(f"Video frames converted to image sequence in '{output_folder}'")
