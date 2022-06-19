import cv2
import numpy as np
import pygame
from pygame import gfxdraw
import time
import math

RED = (255,0,0)
BLUE = (0, 0, 255)

x = 125
y = 200
vel = 2

def get_contour():
    #img = cv2.imread('silverstone fill.png')
    img = cv2.imread('thicc silverstone unfilled.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    return contours

def check_point(contour, point):
    dist = cv2.pointPolygonTest(contour, point, True)

    #print(dist)
    radius = 8

    if dist > radius:
        return False
    else:
        return True

def get_pos():
    pos = pygame.mouse.get_pos()
    print(pos)
    return (pos)

def main():

    global x, y, vel

    pygame.init()

    (width, height) = (900, 720)
    background_colour = (245, 225, 169)
    name = 'The Screen'

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    screen.fill(background_colour)

    cnt = get_contour()
    cntOuter = cnt[1]
    cntInner = cnt[2]

    arrSize = math.floor(cntOuter.size/2)
    cntOuter2 = np.zeros(shape=(arrSize, 2), dtype=int)

    arrSize = math.floor(cntInner.size / 2)
    cntInner2 = np.zeros(shape=(arrSize, 2), dtype=int)

    #Converting to less nested array - faster execution
    i = 0
    for coor in cntOuter:
        for pair in coor:
            cntOuter2[i] = pair
        i=i+1

    j = 0
    for coor in cntInner:
        for pair in coor:
            cntInner2[j] = pair
        j=j+1

    running = True

    while running:
        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                pnt = get_pos()
                check_point(cnt, pnt)

            keys = pygame.key.get_pressed()

            # if left arrow key is pressed
            if keys[pygame.K_LEFT] and x > 0:
                # decrement in x co-ordinate
                x -= vel

            # if left arrow key is pressed
            if keys[pygame.K_RIGHT] and x < width:
                # increment in x co-ordinate
                x += vel

            # if left arrow key is pressed
            if keys[pygame.K_UP] and y > 0:
                # decrement in y co-ordinate
                y -= vel

                # if left arrow key is pressed
            if keys[pygame.K_DOWN] and y < height:
                # increment in y co-ordinate
                y += vel

        screen.fill(background_colour)

        for pair in cntOuter2:
            gfxdraw.pixel(screen, pair[0], pair[1], RED)

        for pair in cntInner2:
            gfxdraw.pixel(screen, pair[0], pair[1], RED)


        carPos = (x, y)
        pygame.draw.circle(screen, BLUE, carPos, 8)

        if check_point(cntOuter, carPos) == True:
            print("collision")

        pygame.display.update()


if __name__ == '__main__':
    main()
