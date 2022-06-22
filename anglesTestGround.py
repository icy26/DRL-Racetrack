import random
import numpy as np
import pygame
from shapely.geometry import LineString

#p1, p2 = (100,150), (300, 500)
p1 = np.array([100, 150])
p2 = np.array([350, 200])

#Find gradient - Not used for this method
#def find_gradient(a,b):
#    changeY = b[1] - a[1]
#    changeX = b[0] - a[0]
#    grad = changeY/changeX
#    print(grad)

#Point A - directly above intersection (length undecided)
#Intersection - Mid Point of startingline
#Perpendicular point away from midpoint - outside
#def get_angle(intersection):
#    generateA(intersection)
#    generateB(intersection)

#generates a line from midpoint to top of screen, directly vertically
def generateA(origin):
    a = (origin[0], 0)
    return a

#chooses one of two perpendicular lines at random
def generateB(origin, outerPoint):
    c, d = gen_perp(origin, outerPoint)
    dup = (c, d)
    choose = random.randint(0,1)
    return dup[choose]

#gets midpoint of line a->b
def gen_midpoint(a, b):
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

#Perpendicular line - drawn at 'a' for line a->b
#drawn at midpoint
#I dont like this method at all - Deprecated methods and importing a whole library for use. Try find a way to use vectors
def gen_perp(a, b):
    cd_length = 60

    ab = LineString([a, b])
    left = ab.parallel_offset(cd_length / 2, 'left')
    right = ab.parallel_offset(cd_length / 2, 'right')
    c = left.boundary[1]
    d = right.boundary[0]  # note the different orientation for right offset
    c = (c.x, c.y)
    d = (d.x, d.y)

    return c, d

def main():
    pygame.init()

    (width, height) = (900, 720)
    background_colour = (245, 225, 169)
    name = 'The Screen'

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    screen.fill(background_colour)

    midPoint = gen_midpoint(p1, p2)
    basePoint = generateA(midPoint)
    perpPoint = generateB(p1, midPoint)


    running = True

    while running:

        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.QUIT:
                running = False

        #random line to mimic the start line
        pygame.draw.line(screen, (0, 255, 0), p1, p2)

        #vertical line to act as angle zero. Used to get steering angle in real program
        pygame.draw.line(screen, (0, 0, 255), midPoint, basePoint)

        #second line for getting steering angle. Perpendicular to start line will mimic direction car is facing
        pygame.draw.line(screen, (0, 0, 0), midPoint, perpPoint)

        pygame.display.update()


if __name__ == '__main__':
    main()