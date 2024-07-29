Pranav Bhogal
CS-430 Assignment 2

Programming Language used - Python3
file containing main - CG_hw2

polygon clipping function - clipping(transformedLines) in the file CG_hw2

Running the executable - The python file has a shebang on top therefore it can be run without the need of a makefile.
To run the file write: ./CG_hw1 "additional arguments here" > "output file name here"

A simple makefile is provided to change the permissions of the executable and run the file with defualt argument values

Additional Information - The file submitted is a windows file. Incase the command to run does not work please open the file in vim and remove "^M" from the end of the shebang. 

Features -

The program takes input from a postscript file. It then performs transformations such as scaling, rotating and translation.
It then clips the transormed polygon using the sutherland-hodgman algorithm into the worldwindow and generates output text in the format of a simplified .ps file.