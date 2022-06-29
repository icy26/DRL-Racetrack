#Aim - This DevGround is to mimic the agent border detection system in the main project
#Goal - To obtain 8 points of a border found around an agent.
    #To then obtain the vectors (distance and direction) midpoint -> borderpoint for all 8 points
#Provisional method of execution for DevGround - 5 point radar (only 180 degrees field of view)
    #1. Use OpenCV to get borders of a circle to mimic a race track
    #2. Create mimic agent at any point in borders
    #3. Draw 5 lines from midpoint every 45 degrees of radar_dist as length. Check if any points of border
        #3.1. If one point is detected : Use that point as input
        #3.2. If no points are detected : initialise vector as 0
        #3.2. If more than one is detected : use closest point
    #4. Midpoint -> Detected point converted to vector
    #5. Vector injected to input matrix
        #Where at 0, 45, 90, 135, 180 degrees maps to inputmatrix[0], [1], [2], [3], [4] respectively

import pygame
from pygame import gfxdraw
import world
import time

BLACK = (0,0,0)
BLUE = (0,0,255)

agentPos = (70, 310)

steeringangle = 0

def main():

        # Build Screen
        pygame.init()

        (width, height) = (600, 600)
        background_colour = (245, 225, 169)
        name = 'The Screen'

        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        screen.fill(background_colour)

        outsideBorder, insideBorder = world.get_borders("Images/circle.png")

        quadrantangle, quadrant = world.convert_steeringangle_to_quadrantangle(steeringangle)

        running = True
        while running:

            #screen.fill(background_colour)

            ev = pygame.event.get()

            for event in ev:
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONUP:
                    world.get_pos()


            # Draw Borders
            for pair in outsideBorder:
                gfxdraw.pixel(screen, pair[0], pair[1], BLACK)

            for pair in insideBorder:
                gfxdraw.pixel(screen, pair[0], pair[1], BLACK)

            pygame.draw.circle(screen, BLUE, agentPos, 8)
            world.draw_direction_line(screen, agentPos, quadrantangle, quadrant)

            radarEndPoints = world.radar_pulse(agentPos, steeringangle)
            world.radar_detect(agentPos, radarEndPoints, outsideBorder, insideBorder)

            pygame.display.update()


if __name__ == '__main__':
    main()
