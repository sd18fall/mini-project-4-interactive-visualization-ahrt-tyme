""" Experiment with face detection and image filtering using OpenCV """

import cv2
import numpy as np
import math

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('~/Toolboxes/CompVis/Spin.avi')

class color():
    """A container for blue, green, red values to return to OpenCV"""
    def __init__(self, B, G=0, R=0):
        if type(B) != int:
            R = int(B[2])
            G = int(B[1])
            B = int(B[0])
        self.B = B
        self.G = G
        self.R = R

    def __str__(self):
        return "({}, {}, {})".format(self.B, self.G, self.R)

    def tuple(self):
        return (self.B, self.G, self.R)

    def list(self):
        return [self.B, self.G, self.R]

black = color(0,0,0)
white = color(255,255,255)
red = color(0,0,255)
orange = color(0,140,255)
yellow = color(0,215,255)
green = color(0,255,0)
cyan = color(255,255,0)
blue = color(255,0,0)
purple = color(211,0,148)
magenta = color(255,0,255)


class pixel():
    """A container for x, y, and color values to be packed into changes lists and groups"""
    def __init__(self, x, y, c=black):
        self.x = x
        self.y = y
        if type(c) != color:
            c = color(c)
        self.color = c

    # def __repr__(self):
    #     return "("+str(self.x)+' , '+str(self.y)+")"

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.color)

    def getXY(self):
        return (self.x, self.y)

class group():
    """Batches of pixels"""
    def __init__(self, pixelList):
        self.pixels = pixelList

    # def __repr__(self):
    #     return self.pixels

    def addPixels(self, pixelList):
        if type(pixelList) != list:
            pixelList = [pixelList]
        self.pixels += pixelList

    def size(self):
        return len(self.pixels)

    def __str__(self):
        ret = ''
        for pixel in self.pixels:
            ret += str(pixel)
        return ret

def isDif(pixelColor1,pixelColor2):
    currBlue = pixelColor1.B
    lastBlue = pixelColor2.B
    currGreen = pixelColor1.G
    lastGreen = pixelColor2.G
    currRed = pixelColor1.R
    lastRed = pixelColor2.R

    changeThresh = 20
    blueChanged = abs(currBlue-lastBlue) > changeThresh
    greenChanged = abs(currGreen-lastGreen) > changeThresh
    redChanged = abs(currRed-lastRed) > changeThresh
    ret = blueChanged and redChanged and greenChanged
    return ret

def findMove(frame, lastFrame, lastLastFrame):
    """Detects changing pixel colors and reports their x,y coordinates"""
    changes = group([]) #list of x,y tuples of pixels that changed
    for y in range(0, height-1, cS):
        for x in range(0, width-1, cS):
            if isDif(color(frame[y][x]),color(lastFrame[y][x])) and isDif(color(lastFrame[y][x]),color(lastLastFrame[y][x])):
                changes.addPixels(pixel(x,y,frame[y][x]))
    return changes

def isDiagonalTo(pixel1, changes):
    """checks if a pixel in changes has another pixel adjacent to it"""
    for pixel2 in changes.pixels:
        # print('xDiff:', pixel1.x-pixel2.x, 'yDiff:', pixel1.y-pixel2.y, 'testing against cS of:', cS)
        if abs(pixel1.x-pixel2.x) == cS and abs(pixel1.y-pixel2.y) == cS:
            return True
    return False

def isLine(pixel1, changes):
    for pixel2 in changes.pixels:
        if abs(pixel1.x-pixel2.x) == cS and pixel1.y == pixel2.y:
            return True
        elif abs(pixel1.y-pixel2.y) == cS and pixel1.x == pixel2.x:
            return True
    return False

def findDiagonals(changes):
    """Detects a diagonal pair of changing pixel colors and reports their x,y coordinates"""
    diagonalChanges = group([])
    for pixel in changes.pixels:
        if isDiagonalTo(pixel,changes):
            diagonalChanges.addPixels(pixel)
    return diagonalChanges

def findLines(changes):
    """Detects a square of changing pixel colors and reports their x,y coordinates"""
    lineChanges = group([])
    for pixel in changes.pixels:
        if isLine(pixel,changes):
            lineChanges.addPixels(pixel)
    return lineChanges


def showMove(frame, changes, color):
    """Changes the color of everything that changed in frame"""
    for pixel in changes.pixels:
        (x,y) = pixel.x, pixel.y
        cv2.rectangle(frame, (x,y), (x+cS, y+cS), color.tuple(), -1)
        # frame[y:(y+cS)][x:(x+cS)] = [0,0,255]
    return frame


#Cheating! Doing things once so we don't redefine constants constantly
ret, lastFrame = cap.read()
lastLastFrame = lastFrame
lastMajorChanges = group([])
height, width = lastFrame.shape[:2]
cS = 7

while(True):
    ret, frame = cap.read()

    changes = findMove(frame, lastFrame, lastLastFrame)
    majorChanges = findDiagonals(changes)
    #changes is a group object
    frame = showMove(frame, majorChanges, magenta)
    frame = showMove(frame, lastMajorChanges, cyan)

    # Create window displaying frame, with colors drawn on top
    cv2.imshow('Frame', frame)

    lastLastFrame = lastFrame
    lastFrame = frame
    lastMajorChanges = majorChanges

    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break



# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()


#Debugging and testing dumping ground:
#to use, change != to == and the while(True) to while(False)
if __name__ != "__main__":
    newGroup = group([])
    print(newGroup)
    p1 = pixel(3, 8)
    p2 = pixel(5,2)
    p3 = pixel(2, 1, [0,255,0])
    p4 = pixel(3,1, blue)
    c1 = color(1,1,1)
    c2 = color([2,2,2])
    c3 = color ([3,2,2])

    # newGroup.addPixels([p1,p2,p3,p4])
    # print(type(newGroup.pixels))
    # print(newGroup.pixels)
    # newGroup.addPixels([p1,p1,p2])
    # print(newGroup.pixels)
    # print(p1.color, p2.color, p3.color, p4.color)

    print(type(c1))
    print(type(c2.tuple()))
    bs = c2.tuple()
    print(bs)
    print(type(bs))
    bull = c3.list()
    print(bull)
    print(type(bull))
    print(str(c3))
