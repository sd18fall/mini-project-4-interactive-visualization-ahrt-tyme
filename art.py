""" Motion detecting art! Using a webcam, detects pixels changing color
and displays them according to several options."""

# ==============================================================================
#                               Setup
# ==============================================================================
import cv2
import numpy as np
import math
import copy

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('~/Toolboxes/CompVis/Spin.avi')

print("\n         Welcome to Ahrt Tyme! Press 'q' on the pop-up window to quit.\n")


# ==============================================================================
#                               Classes
# ==============================================================================

class Color():
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

black = Color(0,0,0)
white = Color(255,255,255)
red = Color(0,0,255)
orange = Color(0,140,255)
yellow = Color(0,215,255)
green = Color(0,255,0)
cyan = Color(255,255,0)
blue = Color(255,0,0)
purple = Color(211,0,148)
magenta = Color(255,0,255)


class Pixel():
    """A container for x, y, and color values to be packed into changes lists and groups"""
    def __init__(self, x=None, y=None, c=black, oldPixel = None):
        if oldPixel != None:
            self.color = copy.deepcopy(oldPixel.color)
            self.x = oldPixel.x
            self.y = oldPixel.y
        else:
            self.x = x
            self.y = y

            if type(c) != Color:
                c = Color(c)
            self.color = c

            self.pixels = [self]

    # def __repr__(self):
    #     return "("+str(self.x)+' , '+str(self.y)+")"

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.color)

    # def __repr__(self):
    #     return "{}, {}, {}".format(self.x, self.y, self.color)

    def getXY(self):
        return (self.x, self.y)

    # def size(self):
    #     return 1

    def __eq__(self, pixel2):
        if pixel2 is None:
            return False
        return self.x == pixel2.x and self.y == pixel2.y

class Group():
    """Batches of pixels"""
    def __init__(self, pixelList):
        self.pixels = pixelList

    # def __repr__(self):
    #     return self.pixels

    def addPixels(self, pixelList):
        if type(pixelList) != list:
            pixelList = [pixelList]
        self.pixels += pixelList

    def removePixel(self, pixelList):
        # if type(pixelList) != list:
        if type(pixelList) == Group:
            pixelList = pixelList.pixels
        elif type(pixelList) == Pixel:
            pixelList = [Pixel(oldPixel = pixelList)]
        for pixel in pixelList:
            self.pixels.remove(pixel)

    def size(self):
        return len(self.pixels)

    def __str__(self):
        ret = ''
        if self.pixels != []:
            ret = str(self.pixels[0])
            for pixel in self.pixels[1:]:
                ret += ', ' + str(pixel)
        return ret

    def __add__(self, other):
        if type(other) == Group:
            self.addPixels(other.pixels)



# ==============================================================================
#                               Functions
# ==============================================================================

def isDif(pixelColor1,pixelColor2):
    currBlue = pixelColor1.B
    lastBlue = pixelColor2.B
    currGreen = pixelColor1.G
    lastGreen = pixelColor2.G
    currRed = pixelColor1.R
    lastRed = pixelColor2.R

    blueChanged = abs(currBlue-lastBlue) > changeThresh
    greenChanged = abs(currGreen-lastGreen) > changeThresh
    redChanged = abs(currRed-lastRed) > changeThresh
    ret = blueChanged and redChanged and greenChanged
    return ret

def findMove(frame, lastFrame, lastLastFrame):
    """Detects changing pixel colors and reports their x,y coordinates"""
    changes = Group([]) #list of x,y tuples of pixels that changed
    for y in range(0, height-1, cS):
        for x in range(0, width-1, cS):
            if isDif(Color(frame[y][x]),Color(lastFrame[y][x])) and isDif(Color(lastFrame[y][x]),Color(lastLastFrame[y][x])):
                changes.addPixels(Pixel(x,y,frame[y][x]))
    return changes

def isDiagonalTo(pixel1, changes):
    """checks if a pixel in changes has another pixel diagonally adjacent to it"""
    for pixel2 in changes.pixels:
        if abs(pixel1.x-pixel2.x) == cS and abs(pixel1.y-pixel2.y) == cS:
            return True
    return False

def isLine(pixel1, changes):
    """checks if a pixel in changes has another horizontally or vertically pixel adjacent to it"""
    for pixel2 in changes.pixels:
        if abs(pixel1.x-pixel2.x) == cS and pixel1.y == pixel2.y:
            return True
        elif abs(pixel1.y-pixel2.y) == cS and pixel1.x == pixel2.x:
            return True
    return False

def isTouching(pixel1,pixel2):
    """checks if a pixel 2 pixels are touching diagonally, vertically or horizontally"""
    return isDiagonalTo(pixel1,pixel2) or isLine(pixel1,pixel2)

def findDiagonals(changes):
    """Detects a diagonal pair of changing pixel colors and reports their x,y coordinates"""
    diagonalChanges = Group([])
    for pixel in changes.pixels:
        if isDiagonalTo(pixel,changes):
            diagonalChanges.addPixels(pixel)
    return diagonalChanges

def findLines(changes):
    """Detects a line of changing pixel colors and reports their x,y coordinates"""
    lineChanges = Group([])
    for pixel in changes.pixels:
        if isLine(pixel,changes):
            lineChanges.addPixels(pixel)
    return lineChanges

def findTouching(changes):
    """Detects lines or diagonals of changing pixel colors and reports their x,y coordinates"""
    touchingChanges = Group([])
    for pixel in changes.pixels:
        if isTouching(pixel,changes):
            touchingChanges.addPixels(pixel)
    return touchingChanges


def showMove(frame, changes, color):
    """Changes the color of everything that changed in frame"""
    for pixel in changes.pixels:
        (x,y) = pixel.x, pixel.y
        cv2.rectangle(frame, (x,y), (x+cS, y+cS), color.tuple(), -1)
        # frame[y:(y+cS)][x:(x+cS)] = [0,0,255]
    return frame

def findThisGroup(foundPixel, changes):
    """finds a a group of touching pixels starting from one specific pixel"""
    adjPixels = []
    for pixel in changes.pixels:
        if isTouching(pixel, foundPixel):
            adjPixels.append(pixel)
    if len(adjPixels) == 0:
        return Group([foundPixel])
    if foundPixel in changes.pixels:
        changes.removePixel(foundPixel)
    changes.removePixel(adjPixels)
    res = Group([foundPixel])
    for pixel in adjPixels:
        temp = findThisGroup (pixel, changes)
        res.addPixels(temp.pixels)
    return res

def findAllGroups(changes):
    """Finds the groups of changed pixels in frame"""
    groupToSplit = copy.deepcopy(changes)
    contigGroups = []
    for pixel in groupToSplit.pixels:
        if pixel in groupToSplit.pixels:
            newGroup = findThisGroup(pixel, groupToSplit)
            contigGroups.append(newGroup)
            #groupToSplit.removePixel(newGroup.pixels)
    return contigGroups
        # groupToSplit.remove(those pixels)

def findLargestGroup(changes):
    """Finds the largest group of changed pixels in frame"""
    largestGroup = Group([])
    groupList = findAllGroups(changes)
    if len(groupList) != 0:
        lengthList = []
        for group in groupList:
            lengthList.append(group.size())
        longestLength = max(lengthList)
        longestIndex = lengthList.index(longestLength)
        largestGroup = groupList[longestIndex]
    return largestGroup
    #groupName.size each group
    #find the max amond the sizes, return that group

def options(frame, changes):
    """sets different factors for display"""
    if not showSelf:
        frame = np.zeros((height, width, 3))

    if pickiness == 0:
        majorChanges = findTouching(changes)
    elif pickiness == 1:
        majorChanges = findLines(changes)
    elif pickiness == 2:
        majorChanges = findDiagonals(changes)
    elif pickiness == 3:
        majorChanges = findLines(findDiagonals(changes))

    if trail:
        display = frame
    else:
        display = copy.deepcopy(frame)

    if showSmallChanges:
        display = showMove(display, majorChanges, smallChangesColor)

    if showPastChanges:
        global lastMajorChanges
        display = showMove(display, lastMajorChanges, pastChangesColor)
        lastMajorChanges = majorChanges

    if showBigGroup:
        bigGroup = findLargestGroup(majorChanges)
        display = showMove(display, bigGroup, bigGroupColor)

    return display


#-----Cheating! Doing things once so we don't redefine constants constantly-----
ret, lastFrame = cap.read()
lastLastFrame = lastFrame
lastMajorChanges = Group([])
height, width = lastFrame.shape[:2]



# ==============================================================================
#        Choices: things to change to affect sensitivity and modes
# ==============================================================================

# Color options are red, orange, yellow, green, cyan, blue, purple, magenta, white, black
# Or create a tuple of B, G, R values between 0 and 255, such as (0, 126, 0)


# The size of the pixel block it checks.
# Smaller means more precise and slower. The minimum a laptop can handle is 7
cS = 7
# The color change threshold before a pixel is said to change color
# Anywhere between 10 and 50 will get results
changeThresh = 20

# Miliseconds per frame; higher is slower
# 0 is a single image, which will have no changes to show
# 20 is a reasonable rate but occasionally laggy with big movements,
# 50 starts to visually look slightly choppy but runs more smoothly
# too much higher will run more consistently but look choppier and miss short movements
speed = 25

#show image from webcam? falsey is a black background
showSelf = 0 #boolean

# how big things need to be before they're considered not just noise
# 0 for what we like (either or), 1 for only findLines,
# 2 for only findDiagonals, 3 to require both
# increasing number generally increases pickiness and decreases number of changes found
pickiness = 0 #0,1,2,3

# find and show the largest group of changed pixels?
showBigGroup = 1 #boolean
bigGroupColor = yellow #Color

# show all the small changes that aren't in that biggest group?
showSmallChanges = 1 #boolean
smallChangesColor = magenta #Color

# track and show the past frame's changes, for a total of two sets of changes?
showPastChanges = 1 #boolean
pastChangesColor = cyan #Color

# Have the pixel changes trail their way off the screen rather than dissipating?
trail = 0 #boolean

# Show the tutorial and preset options?
tutorial = 1 #boolean
if tutorial:
    print("\n--------------------------------------------------------------------------------\n")
    print("If you haven't yet, use the options in the code to optimize your art experience.\n")
    print("     You can change several threshold options, choose what is shown,")
    print("                     and the color it will appear in.")
    print("    This includes the webcam image itself, movement groupings, and trails.")
    print("      Remember that Booleans treat 0 as false and anything else as true.\n")
    print("\n--------------------------------------------------------------------------------\n")
    print("         For now, try a preset: 'retro', 'minimalist', 'techno'")
    print("       Anything else will simply keep the most recent coded settings")
    preset = input('\nPreset to use: ')

    if preset == 'retro':
        showSelf = 1; showBigGroup = 0; showPastChanges = 1; showSmallChanges = 1; trail = 1
        smallChangesColor = magenta; pastChangesColor = cyan
    elif preset == 'minimalist':
        showSelf = 1; showBigGroup = 1; showPastChanges = 0; showSmallChanges = 0; trail = 0
    elif preset == 'techno':
        showSelf = 0; showBigGroup = 1; showPastChanges = 1; showSmallChanges = 1; trail = 0
        smallChangesColor = red; pastChangesColor = blue; bigGroupColor = yellow
# ==============================================================================
#                               Main loop
# ==============================================================================
while(True):
    ret, frame = cap.read()

    changes = findMove(frame, lastFrame, lastLastFrame)
    artFrame = options(frame, changes)

    cv2.imshow('Art', artFrame)

    lastLastFrame = lastFrame
    lastFrame = frame

    # Wait between frames. Changing this is how slow and fast motion happen
    if cv2.waitKey(speed) & 0xFF == ord('q'):
        break

# Unbind video capture object and close any created windows.
cap.release()
cv2.destroyAllWindows()



# ==============================================================================
#                 Debugging and testing dumping ground:
#       to use, change != to == and the while(True) to while(False)
# ==============================================================================

if __name__ != "__main__":
    testFrame = np.zeros((250,250,3))

    p1 = Pixel(10, 3)
    p2 = Pixel(10+cS, 3+cS)
    p3 = Pixel(100, 100)
    p4 = Pixel(200,200)
    p5 = Pixel(10, 3+cS)
    p6 = Pixel(100, 100+cS)
    p7 = Pixel(10+2*cS, 3)
    p8 = Pixel(10, 3+2*cS)
    p9 = Pixel(10+3*cS, 3)


    testChanges = Group([p1,p2,p3,p4,p5,p6,p7,p8,p9])

    #output = findThisGroup(p1,testChanges)
    #output = findAllGroups(testChanges)
    output = findLargestGroup(testChanges)

    testDisplay = showMove(testFrame, testChanges, blue)
    testDisplay = showMove(testFrame, output, red)
    # bleh = 50
    # for gropus in output:
    #     clur = Color(bleh,0,0)
    #     testDisplay = showMove(testFrame, gropus, clur)
    #     bleh += 75

    cv2.imshow('Testing', testDisplay)

    cv2.waitKey(0) & 0xFF == ord('q')
