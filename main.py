import os
import sys
from PIL import Image
from typing import List

def read_input( fname, t=lambda x: x ):
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

data = read_input("DMCrgb.csv")
DMC = []
for l in data:
    id,name,r,g,b,hex = l.split(",")
    DMC.append( dmcColor(id,name,r,g,b,hex) )

data2 = read_input("DMCtoDD.csv")
DMC2DD = []
for l in data2:
    dmc,dd,name = l.split(",")
    DMC2DD.append( dmc2dd(dmc,dd,name) )

def find( r,g,b ):
    closest_color = None
    closest_distance = float("inf")
    for c in DMC:
        distance = sum( (a-b)**2 for a,b,in zip((c.r,c.g,c.b),(r,g,b)) )
        if distance < closest_distance:
            closest_color = c
            closest_distance = distance
    return closest_color
    
def DMC_to_DD(dmcID):
    for c in DMC2DD:
        if c.dmc == dmcID:
            return c.dd, c.name
    return None,None

sizeW, sizeH, image_colors = getColorsFromImage("SnesSamus.png")

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
        if showDMC:
            print(best_color.id,best_color.name,end=" -> ")
        dd, ddName = DMC_to_DD( best_color.id )
        print(dd,ddName,"x",count)
    totalGems += count
print("Total",totalGems)
print("Done")