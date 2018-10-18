""" Experiment with face detection and image filtering using OpenCV """

import cv2
import numpy as np
import math

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('~/Toolboxes/CompVis/Spin.avi')

def isDif(pixel1,pixel2):
    blue = pixel1[0]
    lastBlue = pixel2[0]
    green = pixel1[1]
    lastGreen = pixel2[1]
    red = pixel1[2]
    lastRed = pixel2[2]

    changeThresh = 120
    blueChanged = abs(blue-lastBlue) > changeThresh
    redChanged = abs(red-lastRed) > changeThresh
    greenChanged = abs(green-lastGreen) > changeThresh
    return blueChanged and redChanged and greenChanged

def findMove(frame, lastFrame, lastLastFrame):
    """Detects changing pixel colors and reports their x,y coordinates"""
    changes = [] #list of x,y tuples of pixels that changed
    for y in range(0, height-1, cS):
        for x in range(0, width-1, cS):
            # #Take the grayscale average and compare it to that of the last frame
            # avgVal = np.mean(frame[y][x][:])
            # lastAvgVal = np.mean(lastFrame[y][x][:])
            # if abs(avgVal-lastAvgVal) > 80:
            #     changes.append((x,y))
            if isDif(frame[y][x],lastFrame[y][x]) and isDif(lastFrame[y][x],lastLastFrame[y][x]):
                changes.append((x,y))

    return changes

def isNextTo(pixel1, changes):
    """checks if a pixel in changes has another pixel adjacent to it"""
    for pixel2 in changes:
        if abs(pixel1[0]-pixel2[0]) == cS and abs(pixel1[1]-pixel2[1]) == cS:
            return True
        #elif abs(pixel1[0]-pixel2[0]) == cS and pixel1[1] == pixel2[1]:
        #    return True
        #elif abs(pixel1[1]-pixel2[1]) == cS and pixel1[0] == pixel2[0]:
        #    return True
    return False

def findMajorMove(changes):
    """Detects a square of changing pixel colors and reports their x,y coordinates"""
    majorChanges = []
    for pixel in changes:
        if isNextTo(pixel,changes):
            majorChanges.append(pixel)
    return majorChanges


def showMove(frame, changes, color):
    """Changes the color of everything that changed in frame"""
    for pixel in changes:
        (x,y) = pixel[0], pixel[1]
        cv2.rectangle(frame, (x,y), (x+cS, y+cS), color, -1)
        # frame[y:(y+cS)][x:(x+cS)] = [0,0,255]
    return frame


#Cheating! Doing things once so we don't redefine constants constantly
ret, lastFrame = cap.read()
lastLastFrame = lastFrame
lastMajorChanges = []
height, width = lastFrame.shape[:2]
cS = 7

while(True):
    ret, frame = cap.read()

    # comvert frame to grayscale
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    changes = findMove(frame, lastFrame, lastLastFrame)
    majorChanges = findMajorMove(changes)
    #changes is a list of tuples of x,y values
    frame = showMove(frame, majorChanges, (0,0,255))
    frame = showMove(frame, lastMajorChanges, (255,0,0))

    # Create window displaying grayscale
    cv2.imshow('Frame', frame)

    lastLastFrame = lastFrame
    lastFrame = frame
    lastMajorChanges = majorChanges

    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break



# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()
