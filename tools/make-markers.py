#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils, commands, sys, os
#import commands, sys
#sys.path.append("../cgi-src")
#from index import menu_groupes, menu_autres

################################################################################

all_items = []
for g in utils.get_categories():
    all_items += g["item"]

################################################################################
## symboles

## O point
## L losange
## K carré
## P plus
## M moins

def get_symb(symbole, x, y, r):
    if symbole in "O":
        return "<circle cx='"+str(x)+"' cy='"+str(y)+"' r='"+str(r)+"' style='fill:#000000;' />"
    if symbole in "L":
        r += 1
        return "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x)+","+str(y+r)+" L "+str(x-r)+","+str(y)+" L "+str(x)+","+str(y-r)+" L "+str(x+r)+","+str(y)+" L "+str(x)+","+str(y+r)+" z\" />"
    if symbole in "K":
        return "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y+r)+" L "+str(x-r)+","+str(y+r)+" L "+str(x-r)+","+str(y-r)+" L "+str(x+r)+","+str(y-r)+" L "+str(x+r)+","+str(y+r)+" z\" />"
    if symbole in "P":
        l1 = "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y+r)+" z\" />"
        l2 = "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y+r/3)+" z\" />"       
        return l1+l2
    if symbole in "F":
        r += 1
        l1 = "<path transform=\"rotate(-45 "+str(x)+" "+str(y)+")\" style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y+r)+" z\" />"
        l2 = "<path transform=\"rotate(-45 "+str(x)+" "+str(y)+")\" style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y+r/3)+" z\" />"       
        return l1+l2
    if symbole in "M":
        return "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y-r/3)+" L "+str(x+r)+","+str(y+r/3)+" z\" />"       
    if symbole in "=":
        l1 = "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y+r/3)+" L "+str(x-r)+","+str(y+r)+" L "+str(x+r)+","+str(y+r)+" L "+str(x+r)+","+str(y+r/3)+" z\" />"
        l2 = "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r)+","+str(y-r/3)+" L "+str(x-r)+","+str(y-r/3)+" L "+str(x-r)+","+str(y-r)+" L "+str(x+r)+","+str(y-r)+" L "+str(x+r)+","+str(y-r/3)+" z\" />"
        return l1+l2
    if symbole in "|":
        l1 = "<path style=\"fill:#000000;fill-opacity:1;\" d=\"M "+str(x+r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y+r)+" L "+str(x-r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y-r)+" L "+str(x+r/3)+","+str(y+r)+" z\" />"
        return l1
    
################################################################################
## marqueurs

## M marqueur
## L légende

def get_marker(contour, symbole, couleur):
    if contour == "M": # marqueur
        h = 32
        l = 20
        c = "<path style=\"fill:" + couleur + ";stroke:#000000;stroke-width:.5px\" d=\"M "+str(l/2)+",1 L "+str(l-1)+","+str(h/3)+" L "+str(l/2)+","+str(h-1)+", L 1,"+str(h/3)+", L "+str(l/2)+",1 z\" />"
        m = get_symb(symbole, l/2, h/3, 3)
    if contour == "L": # légende
        h = 12
        l = h
        c = "<path style=\"fill:" + couleur + ";stroke:#000000;stroke-width:.5px\" d=\"M 0,0 L 0,"+str(h)+" L "+str(l)+","+str(h)+" L "+str(l)+",0 L 0,0 z\" />"
        m = get_symb(symbole, l/2, h/2, 3)
    if contour == "B": # bubble
        h = 32.
        l = 16.
        c  = "<path style=\"fill:" + couleur + ";stroke:#000000;stroke-width:.5px\" d=\""
        c += "M "+str(l/2)+","+str(h)+" C "
        c += str(5*l/8)+","+str(5*h/8)+" "+str(7*l/8)+","+str(h/2)+" "+str(l)+","+str(h/4)+" "
        c += str(l)+","+str(h/8)+" "+str(3*l/4)+","+str(0)+" "+str(l/2)+","+str(0)+" "
        c += str(l/4)+","+str(0)+" "+str(0)+","+str(h/8)+" "+str(0)+","+str(h/4)+" "
        c += str(l/8)+","+str(h/2)+" "+str(3*l/8)+","+str(5*h/8)+" "+str(l/2)+","+str(h)+" "
        c += "z\" />"
        m = get_symb(symbole, l/2, h/4, 3)
    head  = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>"
    head += "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\""+str(l+1)+"\" height=\""+str(h+1)+"\">\n"
    tail = "</svg>"
    return head + c + m + tail

################################################################################
    
marker_folder = os.path.join(utils.root_folder, "map/markers")
commands.getstatusoutput("rm %s"%os.path.join(marker_folder,"*.png"))
for i in all_items + [{'item': 0, 'marker_flag': 'O', 'marker_color': '#CCCCCC'}]:
    print i
    for m in "MLB":
        file_svg = os.path.join(marker_folder, "marker-%s-%d.svg"%(m.lower(), i["item"]))
        file_png = os.path.join(marker_folder, "marker-%s-%d.png"%(m.lower(), i["item"]))
        open(file_svg,"w").write(get_marker(m, i["marker_flag"], i["marker_color"]))
        commands.getstatusoutput("inkscape --without-gui --file=%s --export-png=%s"%(file_svg, file_png))
commands.getstatusoutput("rm %s"%os.path.join(marker_folder,"*.svg"))
