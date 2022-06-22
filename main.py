import cv2
import numpy as np
import pygame
from pygame import gfxdraw
import math
import random
from pygame.draw_py import Point
from scipy.spatial import distance

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

def get_borders():
    img = cv2.imread('thicc silverstone unfilled.png')
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
        return False
    else:
        return True

def check_inner_collision(border, point):
    dist = cv2.pointPolygonTest(border, point, True)

    radius = -8

    if dist <= radius:
        return False
    else:
        return True

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
        steeringangle -= 1

def steer_right():
    global steeringangle
    if steeringangle == 359:
        steeringangle = 0
    else:
        steeringangle += 1

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

def generate_start(out_ctr, in_ctr):
    #Picks random point from outside border
    rng = out_ctr.shape[0]
    index = random.randint(0, rng)
    coord = out_ctr[index]
    xa, ya = coord[0], coord[1]
    #print('xa: '+ str(xa) +' ya: '+ str(ya))

    #Finds closest point from inside border
    node = np.array([xa, ya])
    closest_index = distance.cdist([node], in_ctr).argmin()
    xb, yb = in_ctr[closest_index][0], in_ctr[closest_index][1]
    #print('xb: ' + str(xb) + ' yb: ' + str(yb))

    return [(xa, ya), (xb, yb)]

def spawn(coords):
    global x, y
    p1 = coords[0]
    p2 = coords[1]

    #return Point((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    x = (p1[0] + p2[0]) / 2
    y = (p1[1] + p2[1]) / 2

#initialise steering angle
def face_forward(coords):
    global x, y, steeringangle

def find_gradient(a,b):
    changeY = b[1] - a[1]
    changeX = b[0] - a[0]

    grad = changeY/changeX
    print(grad)


def main():
    #global x, y, vel, score

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
    startCoords = generate_start(outsideBorder, insideBorder)

    #Get Spawn location for agent based on midpoint of startCoords
    spawn(startCoords)

    find_gradient(startCoords[0], startCoords[1])

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
                get_pos()

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

        carPos = (x, y)
        pygame.draw.circle(screen, BLUE, carPos, 8)

        draw_direction_line(screen, (x,y), quadrant, quadrantangle)

        if check_outer_collision(outsideBorder, carPos) == True:
            update_score(5)
            #print("outside collision")

        elif check_inner_collision(insideBorder, carPos) == True:
            update_score(5)
            #print("insidecollision")

        else:
            update_score(0.1)

        #Terminate when zeroed
        #if score <= 0:
        #    running = False

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
