""" Experiment with face detection and image filtering using OpenCV """

import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()
    # comvert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create window displaying grayscale
    cv2.imshow('frame', gray)
    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()
