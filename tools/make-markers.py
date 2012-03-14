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
## F croix
## = signe égal
## | trait vertical
## || double trait vertical
## :: quatre points
## .:. quatre points en losange
## T tiangle haut
## t tiangle bas
## X sablier
## >< sablier couche
## L'
## .l
## [] carré vide
## . point

def get_symb(symbole):
    if symbole == "O":
        return "<circle cx='8' cy='8' r='3' />"
    if symbole == "L":
        return "<path d='M 8,12 L 4,8 L 8,4 L 12,8 L 8,12 z' />"
    if symbole == "K":
        return "<path d='M 11,11 L 5,11 L 5,5 L 11,5 L 11,11 z' />"
    if symbole == "P":
        l1 = "<path d='M 9,11 L 7,11 L 7,5 L 9,5 L 9,11 z' />"
        l2 = "<path d='M 11,9 L 5,9 L 5,7 L 11,7 L 11,9 z' />"
        return l1+l2
    if symbole == "F":
        l1 = "<path transform='rotate(45 8 8)' d='M 9,12 L 7,12 L 7,4 L 9,4 L 9,12 z' />"
        l2 = "<path transform='rotate(45 8 8)' d='M 12,9 L 4,9 L 4,7 L 12,7 L 12,9 z' />"
        return l1+l2
    if symbole == "M":
        return "<path d='M 11,9 L 5,9 L 5,7 L 11,7 L 11,9 z' />"
    if symbole == "=":
        l1 = "<path d='M 11,9 L 5,9 L 5,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 5,7 L 5,5 L 11,5 L 11,7 z' />"
        return l1+l2
    if symbole == "|":
        return "<path d='M 9,11 L 7,11 L 7,5 L 9,5 L 9,11 z' />"
    if symbole == "||":
        l1 = "<path transform='rotate(90 8 8)' d='M 11,9 L 5,9 L 5,11 L 11,11 L 11,9 z' />"
        l2 = "<path transform='rotate(90 8 8)' d='M 11,7 L 5,7 L 5,5 L 11,5 L 11,7 z' />"
        return l1+l2
    if symbole == "::":
        l1 = "<path d='M 11,9 L 9,9 L 9,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 9,7 L 9,5 L 11,5 L 11,7 z' />"
        l3 = "<path d='M 7,9 L 5,9 L 5,11 L 7,11 L 7,9 z' />"
        l4 = "<path d='M 7,7 L 5,7 L 5,5 L 7,5 L 7,7 z' />"
        return l1+l2+l3+l4
    if symbole == ".:.":
        l1 = "<path d='M 11,9 L 9,9 L 9,11 L 11,11 L 11,9 z' />"
        l2 = "<path d='M 11,7 L 9,7 L 9,5 L 11,5 L 11,7 z' />"
        l3 = "<path d='M 7,9 L 5,9 L 5,11 L 7,11 L 7,9 z' />"
        l4 = "<path d='M 7,7 L 5,7 L 5,5 L 7,5 L 7,7 z' />"
        return "<g transform='rotate(45 8 8)'>"+l1+l2+l3+l4+"</g>"
    if symbole == "T":
        return "<path d='M 5,11 L 5,5 L 11,5 L 5,11 z' />"
    if symbole == "t":
        return "<path d='M 11,11 L 5,11 L 11,5 L 11,11 z' />"
    if symbole == "X":
        return "<path d='M 11,11 L 5,11 L 11,5 L 5,5 L 11,11 z' />"
    if symbole == "><":
        return "<path d='M 11,11 L 11,5 L 5,11 L 5,5 L 11,11 z' />"
    if symbole == "L'":
        l1 = "<path d='M 5,5 L 11,5 L 11,7 L 7,7 L 7,11 L 5,11 z' />"
        l2 = "<path d='M 11,11 L 9,11 L 9,9 L 11,9 z' />"
        return l1+l2
    if symbole == ".l":
        l1 = "<path d='M 11,11 L 11,5 L 9,5 L 9,9 L 5,9 L 5,11 z' />"
        l2 = "<path d='M 5,5 L 7,5 L 7,7 L 5,7 z' />"
        return l1+l2
    if symbole == "[]":
        return "<path d='M 5,5 L 11,5 L 11,11 L 5,11 z M 7,7 L 7,9 L 9,9 L 9,7 z' />"
    if symbole == ".":
        return "<path d='M 7,7 L 7,9 L 9,9 L 9,7 z' />"

################################################################################
## marqueurs

## M marqueur
## L légende

def get_marker(contour, symbole, couleur):
    if contour == "M": # marqueur
        h = 32
        l = 20
        g = "translate(2,3) scale(1,1)"
        c = "<path style='fill:" + couleur + ";stroke:#000000;stroke-width:.5px' d='M 10,1 L 19,10 L 10,31, L 1,10, L 10,1 z' />"
        m = get_symb(symbole)
    if contour == "L": # légende
        h = 12
        l = h
        g = "translate(-2,-2) scale(1,1)"
        c = "<path style='fill:" + couleur + ";stroke:#000000;stroke-width:1px' d='M 0.5,0.5 L 0.5,11.5 L 11.5,11.5 L 11.5,0.5 L 0.5,0.5 z' />"
        m = get_symb(symbole)
    if contour == "B": # bubble
        h = 32
        l = 16
        g = "translate(0,1) scale(1,1)"
        c = "<path style='fill:" + couleur + ";stroke:#000000;stroke-width:.5px' d='m 8,31.75 c 2,-12 7.75,-18 7.75,-23.5 0,-4 -3.5,-8 -7.75,-8 -4.25,0 -7.75,4 -7.75,8 0,5.5 5.75,11.5 7.75,23.5 z' />"
        m = get_symb(symbole)
    head  = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
    head += "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\""+str(l)+"\" height=\""+str(h)+"\">\n"
    tail = "</svg>"
    return head + c + "\n<g transform='" + g + "' style='fill:#000000;'>\n" + m + "</g>\n" + tail

################################################################################

marker_folder = os.path.join(utils.root_folder, "website", "map", "markers")
commands.getstatusoutput("rm %s"%os.path.join(marker_folder,"*.png"))
for i in all_items:
    print i
    for m in "MLB":
        file_svg = os.path.join(marker_folder, "marker-%s-%d.svg"%(m.lower(), i["item"]))
        file_png = os.path.join(marker_folder, "marker-%s-%d.png"%(m.lower(), i["item"]))
        open(file_svg,"w").write(get_marker(m, i["marker_flag"], i["marker_color"]))
        commands.getstatusoutput("rsvg %s %s"%(file_svg, file_png))
commands.getstatusoutput("rm %s"%os.path.join(marker_folder,"*.svg"))
