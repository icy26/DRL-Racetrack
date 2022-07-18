import pygame
import numpy as np
from pygame import gfxdraw

import trackGenerator
import world

#Static Variables
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
(WIDTH, HEIGHT) = (900, 720)
BACKGROUND_COLOUR = (245, 225, 169)
NAME = 'The Screen'

#Mutable Variables
score = 1000

def main():
    global score

    #Build Screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(NAME)
    screen.fill(BACKGROUND_COLOUR)
    FONT = pygame.font.SysFont('Comic Sans', 15)

    # Converting to less nested array - faster execution
    borders = world.get_borders("stage3.png")
    outsideBorder = borders[0]
    insideBorder = borders[1]

    #Initialise start, finish & deadzone coords line coordinates
    startCoords, finishCoords, deadzoneCoords = world.generate_start_finish(outsideBorder, insideBorder)

    #Get Spawn location for agent based on midpoint of startCoords
    spawn = world.get_spawn(startCoords)
    x, y = spawn[0], spawn[1]

    #Initialise steeringangle
    spawn = np.array(spawn)
    point2 = np.array(startCoords)
    steeringangle = int(world.initialise_steering_angle(spawn, point2[0], startCoords, deadzoneCoords))

    #Initialise velocity
    vel = 0

    running = True
    while running:

        screen.fill(BACKGROUND_COLOUR)

        # Agent Updates _____________

        agentPos = (x, y)

        # Initialise quadrantangle & quadrant (@ each state)
        quadrantangle, quadrant = world.convert_steeringangle_to_quadrantangle(steeringangle)

        x, y = world.move(x, y, vel, quadrantangle, quadrant)

        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                #world.get_pos()
                radarEndPoints = world.radar_pulse(screen, agentPos, steeringangle)
                detectedPoints = world.radar_detect(agentPos, radarEndPoints, outsideBorder, insideBorder)
                detectedVectors = world.convert_detected_points_to_vector(agentPos, detectedPoints)
                print(detectedVectors)

        keys = pygame.key.get_pressed()

        # if left arrow key is pressed
        if keys[pygame.K_LEFT]:
            # decrease steeringangle
            steeringangle = world.steer_left(steeringangle)

        # if left arrow key is pressed
        if keys[pygame.K_RIGHT]:
            # increase steeringangle
            steeringangle = world.steer_right(steeringangle)

        # if left arrow key is pressed
        if keys[pygame.K_UP]:
            # increase velocity
            vel = world.accelerate(vel)
        else:
            vel = world.deccelerate(vel)

        # if left arrow key is pressed
        if keys[pygame.K_DOWN]:
            # decrease velocity
            vel = world.brake(vel)

        # Screen Updates _____________

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
        # Draw Agent
        pygame.draw.circle(screen, BLUE, agentPos, 8)
        #Draw Direction Line (visual only)
        world.draw_direction_line(screen, agentPos, quadrantangle, quadrant)

        #Env Check _____________

        outsideCollisionVal = world.check_outer_collision(outsideBorder, agentPos)
        insideCollisionVal = world.check_inner_collision(insideBorder, agentPos)

        if outsideCollisionVal == 1:
            print("Out of Bounds")
            #running = False
        elif outsideCollisionVal == 2:
            score -= 5
        else:
            score -= 0.1

        if insideCollisionVal == 1:
            #Terminate when agent leaves track
            print("Out of Bounds")
            #running = False
        elif insideCollisionVal == 2:
            score -= 5
        else:
            score -= 0.1

        if world.check_finish(agentPos, finishCoords, deadzoneCoords):
            print("Finish")
            running = False

        if world.check_dead_zone(agentPos, deadzoneCoords, startCoords):
            print("Dead")
            running = False

        #Terminate when zeroed
        if score <= 0:
            print("Zeroed")
            #running = False

        #Env info _____________

        # velText = FONT.render('vel: ' + str(vel), False, (0, 0, 0))
        # steerText = FONT.render('steeringangle: ' + str(steeringangle), False, (0, 0, 0))
        # quadangleText = FONT.render('quadrantangle: ' + str(quadrantangle), False, (0, 0, 0))
        # quadText = FONT.render('quadrant: ' + str(quadrant), False, (0, 0, 0))
        # xcoord = FONT.render('x: ' + str(x), False, (0, 0, 0))
        # ycoord = FONT.render('y: ' + str(y), False, (0, 0, 0))
        # scoreCard = FONT.render('score: ' + str(score), False, (0, 0, 0))
        # screen.blit(velText, (30, 415))
        # screen.blit(steerText, (30, 430))
        # screen.blit(quadangleText, (30, 445))
        # screen.blit(quadText, (30, 460))
        # screen.blit(xcoord, (30, 475))
        # screen.blit(ycoord, (30, 490))
        # screen.blit(scoreCard, (30, 505))

        pygame.display.update()

if __name__ == '__main__':
    #trackGenerator.execute()
    main()