import cv2
import numpy as np
import pygame
from pygame import gfxdraw
import math
import random
from scipy.spatial import distance
from shapely.geometry import Point, Polygon

#Static Variables
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (60, 255, 0)

#Mutable Variables
x = 0
y = 0
vel = 0
steeringangle = 0
quadrantangle = 0
quadrant = 0
score = 1000

startCoords = (0,0)
finishCoords = (0,0)
deadzoneCoords = (0,0)

def get_borders():
    img = cv2.imread('Images/racetrack silverstone.png')
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

    return (cntOuter2, cntInner2)

def check_outer_collision(border, point):
    dist = cv2.pointPolygonTest(border, point, True)

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

def check_inner_collision(border, point):
    dist = cv2.pointPolygonTest(border, point, True)

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

def get_pos():
    pos = pygame.mouse.get_pos()
    print(pos)
    return (pos)

#Movement Mechanics
def accelerate():
    global vel
    vel += 0.05

def deccelerate():
    global vel
    if vel > 0.025:
        vel -= 0.025
    else:
        vel = 0

def brake():
    global vel
    if vel > 0.05:
        vel -= 0.05
    else:
        vel = 0

def steer_left():
    global steeringangle
    if steeringangle == 0:
        steeringangle = 359
    else:
        steeringangle -= 2

def steer_right():
    global steeringangle
    if steeringangle == 359:
        steeringangle = 0
    else:
        steeringangle += 2

def convert_steeringangle_to_quadrantangle(steerangle):
    global quadrantangle, quadrant
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

def movement(quad, angle):
    global x, y, vel

    angleRad = math.radians(angle)

    #Top right quad (moving north east)
    if quad == 0:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x += adj
    # Bottom right quad (moving south east)
    elif quad == 1:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x += adj
    # Bottom left quad (moving south west)
    elif quad == 2:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x -= adj
    #Top left quad (moving north west)
    else:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x -= adj

def draw_direction_line(surf, start_pos, quad, angle):

    angleRad = math.radians(angle)
    linelength = 60
    x1, y1 = start_pos
    x2, y2 = 0, 0
    dl = 5

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
    #Top left quad
    else:
        hypo = linelength
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y2 = y1 - oppo
        x2 = x1 - adj

    #Draw
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

#Subtracts 'val' from the current score
def update_score(val):
    global score
    score -= val
    return score

def generate_start_finish(out_ctr, in_ctr):
    #Picks random point from outside border
    rng = out_ctr.shape[0]
    index = random.randint(0, rng)
    print(index)

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

#prevents agent getting to finish by going backwards
def generate_sf_dead_zone(out_ctr, in_ctr, index):
    coord = out_ctr[index]
    dzx1, dzy1 = coord[0], coord[1]

    node = np.array([dzx1, dzy1])
    closest_index = distance.cdist([node], in_ctr).argmin()
    dzx2, dzy2 = in_ctr[closest_index][0], in_ctr[closest_index][1]

    return [(dzx1, dzy1), (dzx2, dzy2)]

def get_spawn(coords):
    #global x, y
    p1 = coords[0]
    p2 = coords[1]

    #return Point((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    sx = (p1[0] + p2[0]) / 2
    sy = (p1[1] + p2[1]) / 2

    return (sx, sy)

#initialise steering angle
def get_angle(intersection, point2):
    aTemp = generateA(intersection)
    bTemp = generate_perpendicular(intersection, point2)

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

# Base point
def generateA(origin):
    a = (origin[0], 0)
    return a

# Perpendicular point
def generate_perpendicular(point1, point2):
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

    if check_dead_zone(perp):
        perp = point1 - (10 * b)

    return perp

#Check finish
def check_finish(checkPoint):
    coords = [finishCoords[0], finishCoords[1], deadzoneCoords[1], deadzoneCoords[0]]
    finishZone = Polygon(coords)
    return Point(checkPoint).within(finishZone)

#Check deadzone
def check_dead_zone(checkPoint):
    coords = [deadzoneCoords[0], deadzoneCoords[1], startCoords[1], startCoords[0]]
    deadZone = Polygon(coords)
    return Point(checkPoint).within(deadZone)

def main():
    global x, y, steeringangle, startCoords, finishCoords, deadzoneCoords

    #Build Screen
    pygame.init()

    (width, height) = (900, 720)
    background_colour = (245, 225, 169)
    name = 'The Screen'

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    screen.fill(background_colour)

    # Converting to less nested array - faster execution
    borders = get_borders()
    outsideBorder = borders[0]
    insideBorder = borders[1]

    #Get start line coordinates
    startCoords, finishCoords, deadzoneCoords = generate_start_finish(outsideBorder, insideBorder)

    #Get Spawn location for agent based on midpoint of startCoords
    spawn = get_spawn(startCoords)
    x, y = spawn[0], spawn[1]

    #Initialises steeringangle
    spawn = np.array(spawn)
    point2 = np.array(startCoords)
    steeringangle = int(get_angle(spawn, point2[0]))

    font = pygame.font.SysFont('Comic Sans', 15)

    running = True
    while running:

        velText = font.render('vel: ' + str(vel), False, (0, 0, 0))
        steerText = font.render('steeringangle: ' + str(steeringangle), False, (0, 0, 0))
        quadangleText = font.render('quadrantangle: ' + str(quadrantangle), False, (0, 0, 0))
        quadText = font.render('quadrant: ' + str(quadrant), False, (0, 0, 0))
        xcoord = font.render('x: ' + str(x), False, (0, 0, 0))
        ycoord = font.render('y: ' + str(y), False, (0, 0, 0))
        scoreCard = font.render('score: ' + str(score), False, (0, 0, 0))

        # move
        convert_steeringangle_to_quadrantangle(steeringangle)
        movement(quadrant, quadrantangle)

        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                #check_finish(get_pos())
                check_dead_zone(get_pos())

        keys = pygame.key.get_pressed()

        # if left arrow key is pressed
        if keys[pygame.K_LEFT]:
            # decrease steeringangle
            steer_left()

        # if left arrow key is pressed
        if keys[pygame.K_RIGHT]:
            # increase steeringangle
            steer_right()

        # if left arrow key is pressed
        if keys[pygame.K_UP]:
            # increase velocity
            accelerate()
        else:
            deccelerate()

        # if left arrow key is pressed
        if keys[pygame.K_DOWN]:
            # decrease velocity
            brake()

        screen.fill(background_colour)

        #Draw Borders
        for pair in outsideBorder:
            gfxdraw.pixel(screen, pair[0], pair[1], RED)

        for pair in insideBorder:
            gfxdraw.pixel(screen, pair[0], pair[1], RED)

        #Draw Start Line
        pygame.draw.line(screen, GREEN, startCoords[0], startCoords[1])
        #Draw Finish Line
        pygame.draw.line(screen, BLUE, finishCoords[0], finishCoords[1])
        pygame.draw.polygon(screen, BLUE, [finishCoords[0], finishCoords[1], deadzoneCoords[1],deadzoneCoords[0]], 0)
        #Draw Dead Zone Line
        pygame.draw.line(screen, RED, deadzoneCoords[0], deadzoneCoords[1])
        pygame.draw.polygon(screen, RED, [deadzoneCoords[0], deadzoneCoords[1], startCoords[1], startCoords[0]], 0)


        agentPos = (x, y)
        pygame.draw.circle(screen, BLUE, agentPos, 8)

        draw_direction_line(screen, (x,y), quadrant, quadrantangle)

        outsideCollisionVal = check_outer_collision(outsideBorder, agentPos)
        insideCollisionVal = check_inner_collision(insideBorder, agentPos)

        if outsideCollisionVal == 1:
            print("out of bounds")
            running = False
        elif outsideCollisionVal == 2:
            update_score(5)
        else:
            update_score(0.1)

        if insideCollisionVal == 1:
            #Terminate when agent leaves track
            print("Out of Bounds")
            #running = False
        elif insideCollisionVal == 2:
            update_score(5)
        else:
            update_score(0.1)

        if check_finish(agentPos):
            print("Finish")
            running = False

        if check_dead_zone(agentPos):
            print("Dead")
            running = False

        #Terminate when zeroed
        if score <= 0:
            running = False

        #Env info
        screen.blit(velText, (30, 415))
        screen.blit(steerText, (30, 430))
        screen.blit(quadangleText, (30, 445))
        screen.blit(quadText, (30, 460))
        screen.blit(xcoord, (30, 475))
        screen.blit(ycoord, (30, 490))
        screen.blit(scoreCard, (30, 505))

        pygame.display.update()


if __name__ == '__main__':
    main()
