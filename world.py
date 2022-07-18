import cv2
import numpy as np
import math
import pygame
import random as rand
from scipy.spatial import distance
from shapely.geometry import LineString, Point, Polygon

def get_pos():
    pos = pygame.mouse.get_pos()
    print(pos)
    return (pos)

#region track intialisation
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

def generate_start_finish(out_ctr, in_ctr):
    #Picks random point from outside border
    rng = out_ctr.shape[0]
    index = rand.randint(0, rng)
    coord = out_ctr[index]
    sx1, sy1 = coord[0], coord[1]

    #Finds closest point from inside border
    node = np.array([sx1, sy1])
    closest_index = distance.cdist([node], in_ctr).argmin()
    sx2, sy2 = in_ctr[closest_index][0], in_ctr[closest_index][1]

    startCoordsTemp = [(sx1, sy1), (sx2, sy2)]
    finishCoordsTemp = generate_finish(out_ctr, in_ctr, index-60)
    deadZoneCoordsTemp = generate_sf_dead_zone(out_ctr, in_ctr, index-30)

    return startCoordsTemp, finishCoordsTemp, deadZoneCoordsTemp

def generate_finish(out_ctr, in_ctr, index):
    coord = out_ctr[index]
    fx1, fy1 = coord[0], coord[1]

    node = np.array([fx1, fy1])
    closest_index = distance.cdist([node], in_ctr).argmin()
    fx2, fy2 = in_ctr[closest_index][0], in_ctr[closest_index][1]

    return [(fx1, fy1), (fx2, fy2)]

def generate_sf_dead_zone(out_ctr, in_ctr, index):
    coord = out_ctr[index]
    dzx1, dzy1 = coord[0], coord[1]

    node = np.array([dzx1, dzy1])
    closest_index = distance.cdist([node], in_ctr).argmin()
    dzx2, dzy2 = in_ctr[closest_index][0], in_ctr[closest_index][1]

    return [(dzx1, dzy1), (dzx2, dzy2)]

def get_spawn(coords):
    p1 = coords[0]
    p2 = coords[1]

    sx = (p1[0] + p2[0]) / 2
    sy = (p1[1] + p2[1]) / 2

    return (sx, sy)
#endregion

#region angles+quadrants
def convert_steeringangle_to_quadrantangle(steerangle):
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

#initialise steering angle
def initialise_steering_angle(intersection, point2, startCoords, deadzoneCoords):
    aTemp = (intersection[0], 0)
    bTemp = generate_perpendicular(intersection, point2, startCoords, deadzoneCoords)

    a = np.array(aTemp)
    b = np.array(bTemp)
    i = np.array(intersection)

    ia = a - i
    ib = b - i

    cosine_angle = np.dot(ia, ib) / (np.linalg.norm(ia) * np.linalg.norm(ib))
    angleTemp = np.arccos(cosine_angle)

    angle = np.degrees(angleTemp)

    #Determine reflex angle
    if b[0] < i[0]:
        #reflex TRUE
        angle = 360 - angle

    return angle

# Perpendicular point
def generate_perpendicular(point1, point2, startCoords, deadzoneCoords):
    # Get point1 -> point2 Vector
    pVec = point1 - point2

    # Normalize pVec to unit vector
    norm = pVec / np.linalg.norm(pVec)

    # Perpendicular unit vector
    b = np.empty_like(norm)
    b[0] = -norm[1]
    b[1] = norm[0]

    # get point from origin to perp
    # choose point not in deadzone
    perp = point1 + (10 * b)

    if check_dead_zone(perp, startCoords, deadzoneCoords):
        perp = point1 - (10 * b)

    return perp
#endregion

#region environment checks
#Check finish
def check_finish(checkPoint, finishCoords, deadzoneCoords):
    coords = [finishCoords[0], finishCoords[1], deadzoneCoords[1], deadzoneCoords[0]]
    finishZone = Polygon(coords)
    return Point(checkPoint).within(finishZone)

def check_dead_zone(checkPoint, deadzoneCoords, startCoords):
    coords = [deadzoneCoords[0], deadzoneCoords[1], startCoords[1], startCoords[0]]
    deadZone = Polygon(coords)
    return Point(checkPoint).within(deadZone)

def check_outer_collision(outsideBorder, point):
    dist = cv2.pointPolygonTest(outsideBorder, point, True)

    radius = 8

    if dist > radius:
        #no collision
        return 0
    elif dist <= 0:
        #hard collision - midpoint collision (terminates game)
        return 1
    else:
        #slight collision - body collision (reduces points)
        return 2

def check_inner_collision(insideBorder, point):
    dist = cv2.pointPolygonTest(insideBorder, point, True)

    radius = -8

    if dist <= radius:
        # no collision
        return 0
    elif dist >= 0:
        # hard collision - midpoint collision (terminates game)
        return 1
    else:
        # slight collision - body collision (reduces points)
        return 2
#endregion

#region movement
def accelerate(vel):
    vel += 0.05
    return vel

def deccelerate(vel):
    if vel > 0.025:
        vel -= 0.025
    else:
        vel = 0
    return vel

def brake(vel):
    if vel > 0.05:
        vel -= 0.05
    else:
        vel = 0
    return vel

def steer_left(steeringangle):
    if steeringangle == 0:
        steeringangle = 359
    else:
        steeringangle -= 2
    return steeringangle

def steer_right(steeringangle):
    if steeringangle == 359:
        steeringangle = 0
    else:
        steeringangle += 2
    return steeringangle

def move(x, y, velocity, quadrantangle, quadrant):
    angleRad = math.radians(quadrantangle)

    #Top right quad (moving north east)
    if quadrant == 0:
        hypo = velocity
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x += adj
    # Bottom right quad (moving south east)
    elif quadrant == 1:
        hypo = velocity
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x += adj
    # Bottom left quad (moving south west)
    elif quadrant == 2:
        hypo = velocity
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x -= adj
    #Top left quad (moving north west)
    else:
        hypo = velocity
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x -= adj

    return x, y
#endregion

#region radar
def radar_pulse(surf, agentpos, steerangle):
    radarlength = 120

    #point1 @ 0 degree from steering angle
    quadangle, quad = convert_steeringangle_to_quadrantangle(steerangle)
    endpos1 = get_angled_line(agentpos, quadangle, quad, radarlength)
    #pygame.draw.line(surf, (255,0,0), agentpos, endpos1)

    #point2 @ -45 degrees from steering angle
    if steerangle < 45:
        point2angle = (360 + steerangle) - 45
    else:
        point2angle = steerangle - 45
    quadangle, quad = convert_steeringangle_to_quadrantangle(point2angle)
    endpos2 = get_angled_line(agentpos, quadangle, quad, radarlength)
    #pygame.draw.line(surf, (255, 0, 0), agentpos, endpos2)

    #point3 @ +45 degrees from steering angle
    if steerangle >= 315:
        point3angle = (steerangle - 360) + 45
    else:
        point3angle = steerangle + 45
    quadangle, quad = convert_steeringangle_to_quadrantangle(point3angle)
    endpos3 = get_angled_line(agentpos, quadangle, quad, radarlength)
    #pygame.draw.line(surf, (255, 0, 0), agentpos, endpos3)

    #point 4 @ -90 degrees from steering angle
    if steerangle < 90:
        point4angle = (360 + steerangle) - 90
    else:
        point4angle = steerangle - 90
    quadangle, quad = convert_steeringangle_to_quadrantangle(point4angle)
    endpos4 = get_angled_line(agentpos, quadangle, quad, radarlength)
    #pygame.draw.line(surf, (255, 0, 0), agentpos, endpos4)

    # point 5 @ +90 degrees from steering angle
    if steerangle >= 250:
        point5angle = (steerangle - 360) + 90
    else:
        point5angle = steerangle + 90
    quadangle, quad = convert_steeringangle_to_quadrantangle(point5angle)
    endpos5 = get_angled_line(agentpos, quadangle, quad, radarlength)
    #pygame.draw.line(surf, (255, 0, 0), agentpos, endpos5)

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

def convert_detected_points_to_vector(agentpos, dectectedpoints):
    detectedVectors = np.zeros((5,2), dtype=int)

    i = 0
    for dPoint in dectectedpoints:
        if dPoint != None:
            dNPoint = np.array(dPoint)
            dVector = agentpos - dNPoint
            detectedVectors[i] = dVector
        i+=1

    return detectedVectors
#endregion

# region agent
class Agent:
    def __init__(self, spawn, steeringAngle):
        self.x = spawn[0]
        self.y = spawn[1]
        self.velocity = 0
        self.steeringAngle = steeringAngle
        self.observationSpace = None

    def get_observation_state(self, detectedVectors):
        self.observationSpace = np.array([
            [self.velocity, self.steeringAngle],  # velocity  ,  steeringangle
            [detectedVectors[0][0], detectedVectors[0][1]],  # 0degree vector
            [detectedVectors[1][0], detectedVectors[1][1]],  # -45degree vector
            [detectedVectors[2][0], detectedVectors[2][1]],  # 45degree vector
            [detectedVectors[3][0], detectedVectors[3][1]],  # -90degree vector
            [detectedVectors[4][0], detectedVectors[4][1]],  # 90degree vector
        ])

        return self.observationSpace

    def action(self, q):
        # 9 Actions
        if q == 0:
            self.deccelerate()
        elif q == 1:
            self.deccelerate()
            self.steer_left()
        elif q == 2:
            self.deccelerate()
            self.steer_right()

        elif q == 3:
            self. accelerate()
        elif q == 4:
            self. accelerate()
            self.steer_left()
        elif q == 5:
            self. accelerate()
            self.steer_right()

        elif q == 6:
            self. brake()
        elif q == 7:
            self. brake()
            self.steer_left()
        elif q == 8:
            self. brake()
            self.steer_right()

    def accelerate(self):
        self.velocity += 0.05

    def deccelerate(self):
        if self.velocity > 0.025:
            self.velocity -= 0.025
        else:
            self.velocity = 0

    def brake(self):
        if self.velocity > 0.05:
            self.velocity -= 0.05
        else:
            self.velocity = 0

    def steer_left(self):
        if self.steeringAngle == 0:
            self.steeringAngle = 359
        else:
            self.steeringAngle -= 2

    def steer_right(self):
        if self.steeringAngle == 359:
            self.steeringAngle = 0
        else:
            self.steeringAngle += 2

    def move(self, quadrantangle, quadrant):
        #quadrantangle, quadrant = convert_steeringangle_to_quadrantangle(self.steeringAngle)

        angleRad = math.radians(quadrantangle)

        # Top right quad (moving north east)
        if quadrant == 0:
            hypo = self.velocity
            oppo = math.sin(angleRad) * hypo
            adj = math.cos(angleRad) * hypo

            self.y -= oppo
            self.x += adj
        # Bottom right quad (moving south east)
        elif quadrant == 1:
            hypo = self.velocity
            oppo = math.sin(angleRad) * hypo
            adj = math.cos(angleRad) * hypo

            self.y += oppo
            self.x += adj
        # Bottom left quad (moving south west)
        elif quadrant == 2:
            hypo = self.velocity
            oppo = math.sin(angleRad) * hypo
            adj = math.cos(angleRad) * hypo

            self.y += oppo
            self.x -= adj
        # Top left quad (moving north west)
        else:
            hypo = self.velocity
            oppo = math.sin(angleRad) * hypo
            adj = math.cos(angleRad) * hypo

            self.y -= oppo
            self.x -= adj

# end region



















