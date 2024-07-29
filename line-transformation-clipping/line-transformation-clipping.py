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
inside = 0
left = 1
right = 2
bottom = 4
top = 8

#method to compute and update the code for endpoints of a line
def updateCode(x, y):
    code = inside
    if (x < xLowerBound):
        code = code | left
    elif (x > xUpperBound):
        code = code | right
    if(y < yLowerBound):
        code = code | bottom
    elif(y > yUpperBound):
        code = code | top
    return code

def lineClipping(transformedLines):
    clippedLines = []
    for i in range(len(transformedLines)):
        x1 = transformedLines[i][0]
        y1 = transformedLines[i][1]
        x2 = transformedLines[i][2]
        y2 = transformedLines[i][3]

        code1 = updateCode(x1, y1)
        code2 = updateCode(x2, y2)

        accept = False
        
        while(True):
            if ((code1 | code2) == 0):
                accept = True
                break
            elif ((code1 & code2) != 0):
                break
            else:
                if (code1 > code2):
                    outcode = code1
                else:
                    outcode = code2
                if((outcode & top) >= 1):
                    x = x1 + (x2 - x1) * (yUpperBound - y1) / (y2 - y1)
                    y = yUpperBound
                elif((outcode & bottom) >= 1):
                    x = x1 + (x2 - x1) * (yLowerBound - y1) / (y2 - y1)
                    y = yLowerBound
                elif((outcode & right) >= 1):
                    y = y1 + (y2 - y1) * (xUpperBound - x1) / (x2 - x1)
                    x = xUpperBound
                elif((outcode & left) >= 1):
                    y = y1 + (y2 - y1) * (xLowerBound - x1) / (x2 - x1)
                    x = xLowerBound
                if (outcode == code1):
                    x1 = x
                    y1 = y
                    code1 = updateCode(x1, y1)
                else:
                    x2 = x
                    y2 = y
                    code2 = updateCode(x2, y2)
        if(accept):
            acceptedRow = []
            acceptedRow.append(x1)
            acceptedRow.append(y1)
            acceptedRow.append(x2)
            acceptedRow.append(y2)
            clippedLines.append(acceptedRow)

    return clippedLines

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
                if l[j] == "%%%END\n":
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
        print("%d %d m" % (finalLines[i][0], finalLines[i][1]))
        print("%d %d l" % (finalLines[i][2], finalLines[i][3]))
        print("s")
    print("0 sg")
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
    shortOption = "f:s:r:m:n:a:b:c:d:"
    longOption = ["fileName", "scalingFactor", "rotation", "xtranslation", "ytranslation", "xLowerBound", "yLowerBound", "xUpperBound", "yUpperBound"]
    argumentList = sys.argv[1:]
    fileName = "hw1.ps"
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
    #(transformedLines)
    finalLines = lineClipping(transformedLines)
    #print(len(transformedLines), len(finalLines))
    #print(finalLines)
    writeOutputFile(finalLines)

if __name__ == "__main__":
    main()