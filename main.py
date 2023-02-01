import os
import sys
from PIL import Image
import argparse
from pathlib import Path

##
#  
# Note DMC 3346 Hunter Green has been mapped to DD 8266 Hunter Green.
#
##

def read_input( fname, t=lambda x: x ):
    path = Path(os.path.join(sys.path[0], fname))
    
    if not path.is_file():
        print("ERROR",fname,"is missing.")
        return None

    with open(os.path.join(sys.path[0], fname), "r") as f:
        contents = f.read()
        lines = contents.strip().split('\n')

    return list(map(t, lines))

def getColorsFromImage(fileName):
    colors = {}
    w = 0
    h = 0
    with Image.open(os.path.join(sys.path[0], fileName)) as img:
        img = img.convert('RGBA')
        w,h = img.size
        for x in range(0,w):
            for y in range(0,h):
                r,g,b,a = img.getpixel((x,y))
                if a > 0:
                    if not (r,g,b) in colors:
                        colors[(r,g,b)] = 1
                    else:
                        colors[(r,g,b)] += 1

    return w,h,colors

class dmcColor:
    def __init__(self,id,name,r,g,b,hex):
        self.id = id
        self.name = name
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.hex = hex

class dmc2dd:
    def __init__(self,dmc,dd,name):
        self.dmc = dmc
        self.dd = int(dd)
        self.name = name

parser = argparse.ArgumentParser(description='DMCtoDD takes a small pixel sprite image and outputs the Diamond Dotz color and amount needed to reporduce it.')
parser.add_argument("input", help="Input pixel art file [file.png]")
parser.add_argument("-o","--output", help="Output location for the pixel to DD color table [output.txt]")
parser.add_argument("-showDMC", help="Show the DMC colors found in the given art file.", action="store_true")
args = parser.parse_args()

# Load conversion files.
data = read_input("DMCrgb.csv")
if data == None:
    exit(0)

DMC = []
for l in data:
    id,name,r,g,b,hex = l.split(",")
    DMC.append( dmcColor(id,name,r,g,b,hex) )

data2 = read_input("DMCtoDD.csv")
if data == None:
    exit(0)
DMC2DD = []
for l in data2:
    dmc,dd,name = l.split(",")
    DMC2DD.append( dmc2dd(dmc,dd,name) )

# Function to find the closest RGB color of a given RGB in the DMC color chart.
def find( r,g,b ):
    closest_color = None
    closest_distance = float("inf")
    for c in DMC:
        distance = sum( (a-b)**2 for a,b,in zip((c.r,c.g,c.b),(r,g,b)) )
        if distance < closest_distance:
            closest_color = c
            closest_distance = distance
    return closest_color

# Convert DMC to DD    
def DMC_to_DD(dmcID):
    for c in DMC2DD:
        if c.dmc == dmcID:
            return c.dd, c.name
    return None,None

# load image.
sizeW, sizeH, image_colors = getColorsFromImage(args.input)

fptr = None
if args.output or args.o:
    fptr = open(args.output, "w")

if fptr:
    fptr.write("%s\n" %args.input)
    fptr.write("DMC->DD\n")
    fptr.write("Image Size %i x %i\n" %(sizeW, sizeH))
else:
    print("DMC -> DD")
    print("Image Size ", sizeW, "x", sizeH)

buyList = []
totalGems = 0
showDMC = False
for color in image_colors:
    count = image_colors[(color[0],color[1],color[2])]
    best_color = find(color[0],color[1],color[2])
    if not best_color in buyList:
        buyList.append(best_color)
        if args.showDMC:
            if fptr:
                fptr.write("%s %s -> " %(best_color.id,best_color.name))                    
            else:
                print(best_color.id,best_color.name,end=" -> ")
        dd, ddName = DMC_to_DD( best_color.id )
            
        if dd == None or ddName == None:
            print("WARNING DMZ color [", best_color.id, best_color.name, "] was not Found and is used", count, "times.")
        else:
            if fptr:
                fptr.write("%s %s x %i\n" %(dd,ddName,count))
            else:
                print(dd,ddName,"x",count)

    totalGems += count
if fptr:
    fptr.write("Total %i\n" % (totalGems))
else:
    print("Total",totalGems)
    print("Done")

if fptr:
    fptr.close()

