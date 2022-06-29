import cv2
import numpy as np
import math
import pygame
from shapely.geometry import LineString


def get_borders(image):
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    return contours_to_array(contours)

def contours_to_array(contours):
    # Converting to less nested array - faster execution
    cnt = contours
    cntOuter = cnt[1]
    cntInner = cnt[2]

    arrSize = math.floor(cntOuter.size / 2)
    cntOuter2 = np.zeros(shape=(arrSize, 2), dtype=int)

    arrSize = math.floor(cntInner.size / 2)
    cntInner2 = np.zeros(shape=(arrSize, 2), dtype=int)

    i = 0
    for coor in cntOuter:
        for pair in coor:
            cntOuter2[i] = pair
        i = i + 1

    j = 0
    for coor in cntInner:
        for pair in coor:
            cntInner2[j] = pair
        j = j + 1

    return cntOuter2, cntInner2

def get_pos():
    pos = pygame.mouse.get_pos()
    print(pos)
    return (pos)

def convert_steeringangle_to_quadrantangle(steerangle):
    #global quadrantangle, quadrant
    if 0 <= steerangle < 90:
        quadrant = 0
        quadrantangle = 90 - steerangle
    elif 90 <= steerangle < 180:
        quadrant = 1
        quadrantangle = steerangle - 90
    elif 180 <= steerangle < 270:
        quadrant = 2
        quadrantangle = 270 - steerangle
    else:
        quadrant = 3
        quadrantangle = steerangle - 270

    return quadrantangle, quadrant

def get_angled_line(startpos, quadangle, quad, linelength):
    angleRad = math.radians(quadangle)
    x1, y1 = startpos
    x2, y2 = 0, 0

    # Top right quad
    if quad == 0:
        hypo = linelength
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y2 = y1 - oppo
        x2 = x1 + adj
    # Bottom right quad
    elif quad == 1:
        hypo = linelength
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y2 = y1 + oppo
        x2 = x1 + adj
    # Bottom left quad
    elif quad == 2:
        hypo = linelength
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y2 = y1 + oppo
        x2 = x1 - adj
    # Top left quad
    else:
        hypo = linelength
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y2 = y1 - oppo
        x2 = x1 - adj

    endpos = (int(x2), int(y2))

    return endpos

def draw_direction_line(surf, startpos, quadangle, quad):

    x1, y1 = startpos
    x2, y2 = get_angled_line(startpos, quadangle, quad, 60)

    #Draw
    dl = 5

    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

    if (x1 == x2):
        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        xcoords = [x1] * len(ycoords)
    elif (y1 == y2):
        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        ycoords = [y1] * len(xcoords)
    else:
        a = abs(x2 - x1)
        b = abs(y2 - y1)
        c = round(math.sqrt(a ** 2 + b ** 2))
        dx = dl * a / c
        dy = dl * b / c

        xcoords = [x for x in np.arange(x1, x2, dx if x1 < x2 else -dx)]
        ycoords = [y for y in np.arange(y1, y2, dy if y1 < y2 else -dy)]

    next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
    last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
    for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
        start = (round(x1), round(y1))
        end = (round(x2), round(y2))
        pygame.draw.line(surf, (0, 0, 0), start, end, 1)

def radar_pulse(surf, agentpos, steerangle):
    radarlength = 120

    #point1 @ 0 degree from steering angle
    quadangle, quad = convert_steeringangle_to_quadrantangle(steerangle)
    endpos1 = get_angled_line(agentpos, quadangle, quad, radarlength)
    pygame.draw.line(surf, (255,0,0), agentpos, endpos1)

    #point2 @ -45 degrees from steering angle
    if steerangle < 45:
        point2angle = (360 + steerangle) - 45
    else:
        point2angle = steerangle - 45
    quadangle, quad = convert_steeringangle_to_quadrantangle(point2angle)
    endpos2 = get_angled_line(agentpos, quadangle, quad, radarlength)
    pygame.draw.line(surf, (255, 0, 0), agentpos, endpos2)

    #point3 @ +45 degrees from steering angle
    if steerangle >= 315:
        point3angle = (steerangle - 360) + 45
    else:
        point3angle = steerangle + 45
    quadangle, quad = convert_steeringangle_to_quadrantangle(point3angle)
    endpos3 = get_angled_line(agentpos, quadangle, quad, radarlength)
    pygame.draw.line(surf, (255, 0, 0), agentpos, endpos3)

    #point 4 @ -90 degrees from steering angle
    if steerangle < 90:
        point4angle = (360 + steerangle) - 90
    else:
        point4angle = steerangle - 90
    quadangle, quad = convert_steeringangle_to_quadrantangle(point4angle)
    endpos4 = get_angled_line(agentpos, quadangle, quad, radarlength)
    pygame.draw.line(surf, (255, 0, 0), agentpos, endpos4)

    # point 5 @ +90 degrees from steering angle
    if steerangle >= 250:
        point5angle = (steerangle - 360) + 90
    else:
        point5angle = steerangle + 90
    quadangle, quad = convert_steeringangle_to_quadrantangle(point5angle)
    endpos5 = get_angled_line(agentpos, quadangle, quad, radarlength)
    pygame.draw.line(surf, (255, 0, 0), agentpos, endpos5)

    radarEndPoints = (endpos1, endpos2, endpos3, endpos4, endpos5)

    return radarEndPoints

def radar_detect(agentpos, radarEndPoints, outsideBorder, insideBorder):

    point1 = radarEndPoints[0]
    point2 = radarEndPoints[1]
    point3 = radarEndPoints[2]
    point4 = radarEndPoints[3]
    point5 = radarEndPoints[4]

    # Detection point1
    point1Detection = get_points_on_line(agentpos, point1, outsideBorder, insideBorder)
    point2Detection = get_points_on_line(agentpos, point2, outsideBorder, insideBorder)
    point3Detection = get_points_on_line(agentpos, point3, outsideBorder, insideBorder)
    point4Detection = get_points_on_line(agentpos, point4, outsideBorder, insideBorder)
    point5Detection = get_points_on_line(agentpos, point5, outsideBorder, insideBorder)


    detectionTemp = (point1Detection, point2Detection, point3Detection, point4Detection, point5Detection)
    return detectionTemp

def get_points_on_line(startpos, endpos, outsideBorder, insideBorder):
    ls = LineString([startpos, endpos])

    for f in range(0, int(ls.length) + 1):
        p = ls.interpolate(f).coords[0]
        pArr = (int(p[0]), int(p[1]))

        #Old Algorithm
        # if any(np.equal(outsideBorder, pArr).all(1)):
        #     return pArr
        # elif any(np.equal(insideBorder, pArr).all(1)):
        #     return pArr

        #New Algorithm
        if -1.0 < cv2.pointPolygonTest(outsideBorder, pArr, True) < 1.0:
            return pArr
        elif -1.0 < cv2.pointPolygonTest(insideBorder, pArr, True) < 1.0:
            return pArr

    return None














