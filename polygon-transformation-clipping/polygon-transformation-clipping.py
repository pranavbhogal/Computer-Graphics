#!/usr/bin/python3

import sys, getopt, math

#default argument values
scalingFactor =1.0
rotation = 0
xTranslation = 0
yTranslation = 0
xLowerBound = 0
yLowerBound = 0
xUpperBound = 499
yUpperBound = 499

#section codes
top = 8
left = 1
right = 2
bottom = 4 
clipBoundary = top


def checkInside(x, y, clipBoundary):
    if(clipBoundary == top and y < yUpperBound):
        return True
    elif(clipBoundary == left and x > xLowerBound):
        return True
    elif(clipBoundary == right and x < xUpperBound):
        return True
    elif(clipBoundary == bottom and y > yLowerBound):
        return True
    return False


def checkIntersection(x1, y1, x2, y2, clipBoundary):
    dx = x2 - x1
    dy = y2 - y1

    if(dx == 0 or dy == 0):
        if (clipBoundary == top):
            xIntersect = x1
            yIntersect = yUpperBound
        elif (clipBoundary == left):
            xIntersect = xLowerBound
            yIntersect = y1
        elif (clipBoundary == bottom):
            xIntersect = x1
            yIntersect = yLowerBound
        elif (clipBoundary == right):
            xIntersect = xUpperBound
            yIntersect = y1
        return (xIntersect, yIntersect)
    
    slope = dy/dx
    if (clipBoundary == top):
            xIntersect = (yUpperBound - y1)/slope + x1
            yIntersect = yUpperBound
    if (clipBoundary == left):
            xIntersect = xLowerBound
            yIntersect = (xLowerBound - x1)*slope + y1
    if (clipBoundary == bottom):
            xIntersect = (yLowerBound - y1)/slope + x2
            yIntersect = yLowerBound
    if (clipBoundary == right):
            xIntersect = xUpperBound
            yIntersect = (xUpperBound - x1)*slope + y1

    return (xIntersect, yIntersect)


def clipping(transformedLines, clipBoundary):
    clippedLines = []
    for i in range(0, len(transformedLines)-1):
        row1 = []
        row2 = []
        x1 = transformedLines[i][0]
        y1 = transformedLines[i][1]
        x2 = transformedLines[i+1][0]
        y2 = transformedLines[i+1][1]
        if(checkInside(x1, y1, clipBoundary)):
            if(checkInside(x2, y2, clipBoundary)): #case 1
                row2.append(x2)
                row2.append(y2)
                clippedLines.append(row2)
            else:
                xIntersect, yIntersect = checkIntersection(x1, y1, x2, y2, clipBoundary)
                row2.append(xIntersect)
                row2.append(yIntersect)
                clippedLines.append(row2) #case 2
        else:
            if(checkInside(x2, y2, clipBoundary)): #case 4
                xintersection, yintersection = checkIntersection(x2, y2, x1, y1, clipBoundary)
                row1.append(xintersection)
                row1.append(yintersection)
                row2.append(x2)
                row2.append(y2)
                clippedLines.append(row1)
                clippedLines.append(row2)

    return clippedLines


def SutherlandHodgman(transformedLines):
    leftClip = clipping(transformedLines, left)
    if(len(leftClip)) != 0:
        leftClip.append(leftClip[0])
    topClip = clipping(leftClip, top)
    if(len(topClip)) != 0:
        topClip.append(topClip[0])
    bottomClip = clipping(topClip, bottom)
    if(len(bottomClip)) != 0:
        bottomClip.append(bottomClip[0])
    rightClip = clipping(bottomClip, right)
    if(len(rightClip)) != 0:
        rightClip.append(rightClip[0])

    return rightClip

def windowing(lineArray):
    for row in lineArray:
        row[0] = row[0] - xLowerBound
        row[1] = row[1] - yLowerBound
    return lineArray


def lineTransformation(lineArray):

    #scalling original lines
    scaledLines = []
    for i in range(0, len(lineArray)):
        scaledRow = []
        for j in range(0, len(lineArray[i])):
           temp = float(lineArray[i][j])
           temp = temp * float(scalingFactor)
           scaledRow.append(temp)
        scaledLines.append(scaledRow)
    
    #rotating scaled lines
    rotatedLines = []
    for i in range(len(scaledLines)):
        rotatedRow = []
        for j in range(0, len(scaledLines[i]), 2):
            x = scaledLines[i][j]
            y = scaledLines[i][j+1]
            rotatedx = x * math.cos(math.radians(int(rotation))) - y * math.sin(math.radians(int(rotation)))
            rotatedy = x * math.sin(math.radians(int(rotation))) + y * math.cos(math.radians(int(rotation)))
            rotatedRow.append(rotatedx)
            rotatedRow.append(rotatedy)
        rotatedLines.append(rotatedRow)

    #translating the scaled lines
    translatedLines = []
    for i in range(len(rotatedLines)):
        translatedRow = []
        for j in range(0, len(rotatedLines[i]), 2):
            x = rotatedLines[i][j]
            y = rotatedLines[i][j+1]
            translatedx = x + int(xTranslation)
            translatedy = y + int(yTranslation)
            translatedRow.append(translatedx)
            translatedRow.append(translatedy)
        translatedLines.append(translatedRow)

    return translatedLines

#method to read the postscript file
def readFile(fileName):
    f = open(fileName, "r")
    l = f.readlines()
    lines = []
    for i in range(0, len(l)):
        if l[i] == "%%%BEGIN\n":
            for j in range(i+1, len(l)):
                if l[j] == "stroke\n":
                    break
                elements = l[j].split(" ")
                elements.pop()
                lines.append(elements)
    return(lines)

def writeOutputFile(finalLines):
    print("%!PS\n")
    print("/m {moveto} bind def")
    print("/l {lineto} bind def")
    print("/cp {closepath} bind def")
    print("/s {stroke} bind def")
    print("/sg {setgray} bind def")
    print("0.1 setlinewidth")
    print("%%BeginSetup")
    print("  << /PageSize [%d %d] >> setpagedevice" % (xsize, ysize) )
    print("%%EndSetup\n")
    print("%%%BEGIN")
    for i in range(len(finalLines)):
        if(i == 0):
            print("%d %d m" % (finalLines[i][0], finalLines[i][1]))
        else:
            print("%d %d l" % (finalLines[i][0], finalLines[i][1]))
    print("stroke")
    print("%%%END")
    return

def main():
    global scalingFactor
    global rotation
    global xTranslation
    global yTranslation
    global xLowerBound
    global yLowerBound
    global xUpperBound
    global yUpperBound
    global xsize, ysize
    global clipBoundary
    shortOption = "f:s:r:m:n:a:b:c:d:"
    longOption = ["fileName", "scalingFactor", "rotation", "xtranslation", "ytranslation", "xLowerBound", "yLowerBound", "xUpperBound", "yUpperBound"]
    argumentList = sys.argv[1:]
    fileName = "hw2_a.ps"
    try:
        arguments, values = getopt.getopt(argumentList, shortOption, longOption)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    for currentArg, currentVal in arguments:
        if currentArg in ("-f", "--fileName"):
            fileName = currentVal
        elif currentArg in ("-s", "--scalingFactor"):
            scalingFactor = float(currentVal)
        elif currentArg in ("-r", "--rotation"):
            rotation = int(currentVal)
        elif currentArg in ("-m", "--xtranslation"):
            xTranslation = int(currentVal)
        elif currentArg in ("-n", "--ytranslation"):
            yTranslation = int(currentVal)
        elif currentArg in ("-a", "--xLowerBound"):
            xLowerBound = int(currentVal)
        elif currentArg in ("-b", "--yLowerBound"):
            yLowerBound = int(currentVal)
        elif currentArg in ("-c", "--xUpperBound"):
            xUpperBound = int(currentVal)
        elif currentArg in ("-d", "--yUpperBound"):
            yUpperBound = int(currentVal)
    #print(fileName, scalingFactor, rotation, xTranslation, yTranslation, xLowerBound, yLowerBound, xUpperBound, yUpperBound)
    xsize = (int(xUpperBound) - int(xLowerBound)) + 1
    ysize = (int(yUpperBound) - int(yLowerBound)) + 1
    originalLines = readFile(fileName)
    transformedLines = lineTransformation(originalLines)
    finalLines = SutherlandHodgman(transformedLines)
    outputLines = windowing(finalLines)
    writeOutputFile(outputLines)

if __name__ == "__main__":
    main()
