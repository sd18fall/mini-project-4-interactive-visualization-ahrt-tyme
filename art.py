""" Experiment with face detection and image filtering using OpenCV """

import cv2
import numpy as np
import math

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('~/Toolboxes/CompVis/Spin.avi')

def findMove(frame, lastFrame):
    """Detects changing pixel colors and reports their x,y coordinates"""
    changes = [] #list of x,y tuples of pixels that changed
    for y in range(height):
        for x in range(width):
            avgVal = np.mean(frame[y][x][:])
            lastAvgVal = np.mean(lastFrame[y][x][:])
            if abs(avgVal-lastAvgVal) > 25:
                changes.append((x,y))
    return changes


ret, lastFrame = cap.read()
height, width = lastFrame.shape[:2]

while(True):
    ret, frame = cap.read()
    # comvert frame to grayscale
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    changes = findMove(frame, lastFrame)
    #changes is a list of tuples of x,y values

    # Create window displaying grayscale
    cv2.imshow('frame', frame)
    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

    lastFrame = frame


# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()
