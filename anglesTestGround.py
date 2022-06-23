import random
import numpy as np
import pygame
from shapely.geometry import LineString
import matplotlib.pyplot as plt

p1 = np.array([200, 200])
#p2 = np.array([400, 200])
p2 = np.array([random.randint(250,600), random.randint(250,600)])

#Find gradient - Not used for this method
def find_gradient(a,b):
    changeY = b[1] - a[1]
    changeX = b[0] - a[0]
    grad = changeY/changeX
    print(grad)
    return grad

#gets midpoint of line a->b
def gen_midpoint(a, b):
    return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

#Point A - directly above intersection (length undecided)
#Intersection - Mid Point of startingline
#Perpendicular point away from midpoint - outside
def get_angle(intersection, point2):
    aTemp = generateA(intersection)
    bTemp= generate_perpendicular(intersection, point2)

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

    print(angle)

    return a, b, angle

#generates a line from midpoint to top of screen, directly vertically
def generateA(origin):
    a = (origin[0], 0)
    return a

# New Perpendicular method using vectors (numpy). No need for extra library. More legibile
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
    # randomise direction of perpendicular point
    if random.randint(0, 1) == 0:
        perp = point1 + (20 * b)
    else:
        perp = point1 - (20 * b)

    return perp

#Perpendicular line - drawn at 'a' for line a->b
#drawn at midpoint
#I dont like this method at all (long & unintelligible) - Deprecated methods and importing a whole library for use. Try find a way to use vectors
def gen_perp_old(origin, point2):
    cd_length = 60

    ab = LineString([point2, origin])
    left = ab.parallel_offset(cd_length / 2, 'left')
    right = ab.parallel_offset(cd_length / 2, 'right')
    c = left.boundary[1]
    d = right.boundary[0]  # note the different orientation for right offset
    c = (c.x, c.y)
    d = (d.x, d.y)

    return c, d

#chooses one of two perpendicular lines at random
#Unecessary method
def generateB_old(origin, point2 ):
    c, d = gen_perp_old(origin, point2)
    dup = (c, d)
    choose = random.randint(0,1)
    return dup[choose]

def main():
    pygame.init()

    (width, height) = (900, 720)
    background_colour = (245, 225, 169)
    name = 'The Screen'

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    screen.fill(background_colour)

    midPoint = gen_midpoint(p1, p2)
    basePoint, perpPoint, steeringangle = get_angle(midPoint, p2)

    #perpPoint2 = generate_perpendicular(midPoint, p2)

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
        #pygame.draw.line(screen, (0, 0, 0), midPoint, perpPoint)
        pygame.draw.line(screen, (255, 0, 0), midPoint, perpPoint)



        pygame.display.update()


if __name__ == '__main__':
    main()