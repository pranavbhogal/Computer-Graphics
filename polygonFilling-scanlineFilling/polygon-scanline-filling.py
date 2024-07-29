#!/usr/bin/python3

import sys, getopt, math


#default argument values
scalingFactor =1.0
rotation = 0
xTranslation = 0
yTranslation = 0
xLowerBound = 0
yLowerBound = 0
xUpperBound = 250
yUpperBound = 250
xviewLower = 0
yviewLower = 0
xviewUpper = 200
yviewUpper = 200
pixels = [[0 for _ in range(501)] for y in range(501)]

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

def calculateIntersection(x1, y1, x2, y2, y):
    row = []
    dx = x2 - x1
    dy = y2 - y1
    if(dx == 0):
        x = x1
    else:
        x = round(x1 + (dy/dx)*(y-y1))
    row.append(x)
    row.append(y)
    return x

def sort(intersectionList):
    for i in range(0, len(intersectionList)):
        intersectionList.sort()
    return


def scanFill(intersectionList, y1):
    for i in range(0, len(intersectionList)-1, 2):
        x1 = intersectionList[i]
        x2 = intersectionList[i+1]
        while(x1 != x2):
            pixels[y1][x1] = 1
            x1 += 1
    return


def polygonFilling(polygonArray):
    edgeList = dict()
    for i in range(0, len(polygonArray)-1):
        yminEdge =  min(polygonArray[i][1], polygonArray[i+1][1])
        ymaxEdge =  max(polygonArray[i][1], polygonArray[i+1][1])
        if yminEdge == ymaxEdge:
            continue
        else:
            for y in range(yminEdge, ymaxEdge+1):
                row = []
                x1 = polygonArray[i][0]
                x2 = polygonArray[i+1][0]
                y1 = polygonArray[i][1]
                y2 = polygonArray[i+1][1]
                row.append(x1)
                row.append(y1)
                row.append(x2)
                row.append(y2)
                if(y not in edgeList.keys()):
                    edgeList[y]= [row]
                else:
                    edgeList[y].append(row)
    for key, value in edgeList.items():
        intersectionList = []
        for j in range(len(value)):
            x1 = value[j][0]
            y1 = value[j][1]
            x2 = value[j][2]
            y2 = value[j][3]   
            x = calculateIntersection(x1, y1, x2, y2, key)
            intersectionList.append(x)
        sort(intersectionList)
        scanFill(intersectionList, key)          
    return

def rounding(polygonArray):
    finalPolygons = []
    for i in range(0, len(polygonArray)):
        polygonRow = []
        x = round(polygonArray[i][0])
        y = round(polygonArray[i][1])
        polygonRow.append(x)
        polygonRow.append(y)
        finalPolygons.append(polygonRow)
    return finalPolygons

def viewportTransforms(lineArray):
    
    #scalling original polygon
    scaledLines = []
    for i in range(0, len(lineArray)):
        scaledRow = []
        x = float(lineArray[i][0])
        y = float(lineArray[i][1])
        xvport = xviewUpper - xviewLower
        yvport = yviewUpper - yviewLower
        xworld = xUpperBound - xLowerBound
        yworld = yUpperBound - yLowerBound
        x = x * (xvport/xworld)
        y = y * (yvport/yworld)
        scaledRow.append(x)
        scaledRow.append(y)
        scaledLines.append(scaledRow)

    #translating to world window
    translatedLinesWorld = []
    for i in range(len(scaledLines)):
        translatedRow = []
        x = scaledLines[i][0]
        y = scaledLines[i][1]
        translatedx = x - xLowerBound
        translatedy = y - yLowerBound
        translatedRow.append(translatedx)
        translatedRow.append(translatedy)
        translatedLinesWorld.append(translatedRow)
    
    #translating to viewport
    translatedLinesViewport = []
    for i in range(len(scaledLines)):
        translatedRow = []
        x = scaledLines[i][0]
        y = scaledLines[i][1]
        translatedx = x - xviewLower
        translatedy = y - yviewLower
        translatedRow.append(translatedx)
        translatedRow.append(translatedy)
        translatedLinesViewport.append(translatedRow)

    return scaledLines

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

def windowing(lineArray):
    for row in lineArray:
        row[0] = row[0] - xLowerBound
        row[1] = row[1] - yLowerBound
    return lineArray

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
            if(checkInside(x2, y2, clipBoundary)):
                row2.append(x2)
                row2.append(y2)
                clippedLines.append(row2)
            else:
                xIntersect, yIntersect = checkIntersection(x1, y1, x2, y2, clipBoundary)
                row2.append(xIntersect)
                row2.append(yIntersect)
                clippedLines.append(row2)
        else:
            if(checkInside(x2, y2, clipBoundary)):
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
    allPolygons = []
    for i in range(0, len(l)):
        polygon = []
        if l[i] == "%%%BEGIN\n":
            for j in range(i+1, len(l)):
                if len(l[j]) == 1:
                    continue
                if l[j] == "stroke\n":
                    allPolygons.append(polygon)
                    polygon = []
                    continue
                if l[j].strip() == "":
                    continue
                if l[j] == "%%%END\n":
                    break
                elements = l[j].split()
                elements.pop()
                polygon.append(elements)
                
    return(allPolygons)

def writeOutputFile():
    print("P1")
    print("501 501")
    for i in range(len(pixels)-1, -1, -1):
        for j in range(0, len(pixels[i])):
            print(pixels[i][j], end=" ")
        print()
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
    global xviewLower, yviewLower, xviewUpper, yviewUpper
    global pixels
    shortOption = "f:s:r:m:n:a:b:c:d:j:k:o:p"
    longOption = ["fileName", "scalingFactor", "rotation", "xtranslation", "ytranslation", "xLowerBound", "yLowerBound", "xUpperBound", "yUpperBound","xviewLower", "yviewLower", "xviewUpper", "yviewUpper"]
    argumentList = sys.argv[1:]
    fileName = "hw3.ps"
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
        elif currentArg in ("-j", "--xviewLower"):
            xviewLower = int(currentVal)
        elif currentArg in ("-k", "--yviewLower"):
            yviewLower = int(currentVal)
        elif currentArg in ("-o", "--xviewUpper"):
            xviewUpper = int(currentVal)
        elif currentArg in ("-o", "--yviewUpper"):
            yviewUpper = int(currentVal)
    xsize = (int(xUpperBound) - int(xLowerBound)) + 1
    ysize = (int(yUpperBound) - int(yLowerBound)) + 1
    allPolygons = readFile(fileName)
    transformedPolygons = []
    for polygon in allPolygons:
        transformed = lineTransformation(polygon)
        transformedPolygons.append(transformed)
    clippedPolygons = []
    for polygon in transformedPolygons:
        clipped = SutherlandHodgman(polygon)
        clippedPolygons.append(clipped)
    windowedPolygons = []
    for polygon in clippedPolygons:
        windowed = windowing(polygon)
        windowedPolygons.append(windowed)
    viewportTransformedPolygons = []
    for polygon in windowedPolygons:
        viewportTransformed = viewportTransforms(polygon)
        viewportTransformedPolygons.append(viewportTransformed)
    finalPolygonList = []
    for polygon in viewportTransformedPolygons:
        rounded = rounding(polygon)
        finalPolygonList.append(rounded)
    filledPolygons = []
    for polygon in finalPolygonList:
        filledPolygon = polygonFilling(polygon)
        filledPolygons.append(filledPolygon)
    writeOutputFile()

if __name__ == "__main__":
    main()
