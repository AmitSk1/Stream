import cv2
import numpy as np
import pyautogui

# Initialize the camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
    # If frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Frame processing can go here
    # For example, displaying the frame
    cv2.imshow('frame', frame)
    cv2.imshow('screen', screen_np)
    if cv2.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
