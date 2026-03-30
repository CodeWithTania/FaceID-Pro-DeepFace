import cv2
from deepface import DeepFace
import os

#Setup Face Database Folder

db_path = "db"

# Create database folder if it does not exist
if not os.path.exists(db_path):
    os.makedirs(db_path)

#Start Webcam

cap = cv2.VideoCapture(0)  # 0 = default camera

# Face recognition is heavy, so we will run it

frame_count = 0
current_name = "Scanning..."

# Main Camera Loop

while True:
    ret, frame = cap.read()
    
    # If frame is not captured properly, exit loop
    if not ret:
        break

    frame_count += 1
    
    # Copy frame for display (original remains unchanged)
    display_frame = frame.copy()

    # Face Recognition (Every 10th Frame)
    
    if frame_count % 10 == 0:
        try:
            # Check if database contains any registered faces
            if len(os.listdir(db_path)) > 0:
                
                # Find face match from database
                # silent=True avoids excessive terminal logs
                results = DeepFace.find(
                    img_path=frame,
                    db_path=db_path,
                    model_name='VGG-Face',
                    enforce_detection=False,
                    silent=True
                )

                # If a match is found
                if len(results) > 0 and not results[0].empty:
                    match = results[0].iloc[0]
                    
                    # Extract name from image filename
                    current_name = os.path.basename(
                        match['identity']
                    ).split('.')[0]
                else:
                    current_name = "Unknown"

        except:
            # If any error occurs during recognition
            current_name = "Scanning..."

    # Display Name on Screen
    
    cv2.putText(
        display_frame,
        f"Person: {current_name}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Show camera window
    cv2.imshow("Face Recognition Speed+", display_frame)

    # Keyboard Controls

    key = cv2.waitKey(1) & 0xFF

    # Press 's' to save/register a new face
    if key == ord('s'):
        name = input("Enter Name: ")

        if name:
            # Save current frame as a new face image
            img_path = os.path.join(db_path, f"{name}.jpg")
            cv2.imwrite(img_path, frame)

            # Delete old DeepFace cache (.pkl files)
            # This ensures the new face is recognized immediately
            for f in os.listdir(db_path):
                if f.endswith(".pkl"):
                    os.remove(os.path.join(db_path, f))

            print(f"Registered {name}!")

    # Press 'q' to quit program
    elif key == ord('q'):
        break

# Release Resources
cap.release()
cv2.destroyAllWindows()