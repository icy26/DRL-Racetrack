import pygame
import numpy as np
from pygame import gfxdraw
import math
import tensorflow

import world

class Network:
    def __init__(self, shape):
        self.weights1 = np.random.rand(shape[1], 6)
        self.weights2 = np.random.rand(self.weights1.shape[1], 6)
        self.weights3 = np.random.rand(self.weights2.shape[1], 9)

def forward_step(input, weights, activation):
    output = np.dot(input, weights)

    if activation == 'relu':
        return np.maximum(0.0, output)

    elif activation == 'sigmoid':
        return 1 / (1 + math.exp(-output))

    elif activation == 'linear':
        if output > 0:
            return 1
        else:
            return 0
    else:
        print("No activation")
        pass

def normalise(tensor):
    return tensor * 0.01

def main():
    #Static Env Variables
    BLACK = (0,0,0)
    RED = (255,0,0)
    BLUE = (0,0,255)
    GREEN = (0,255,0)
    (WIDTH, HEIGHT) = (900, 720)
    BACKGROUND_COLOUR = (245, 225, 169)
    NAME = 'The Screen'

    #Static DQN Variables
    EPISODES = 1

    # Action State
    actionspace = { }

    for episode in range(EPISODES):

        # Build Screen
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        screen.fill(BACKGROUND_COLOUR)
        FONT = pygame.font.SysFont('Comic Sans', 15)

        # Converting to less nested array - faster execution
        borders = world.get_borders("stage3.png")
        outsideBorder = borders[0]
        insideBorder = borders[1]

        # Initialise start, finish & deadzone coords line coordinates
        startCoords, finishCoords, deadzoneCoords = world.generate_start_finish(outsideBorder, insideBorder)

        # Get Spawn location for agent based on midpoint of startCoords
        spawn = world.get_spawn(startCoords)

        # Initialise steeringangle
        spawn = np.array(spawn)
        point2 = np.array(startCoords)
        steeringAngle = int(world.initialise_steering_angle(spawn, point2[0], startCoords, deadzoneCoords))

        ag1 = world.Agent(spawn, steeringAngle)

        running = True
        while running:
            screen.fill(BACKGROUND_COLOUR)

            agentPos = (ag1.x, ag1.y)
            quadrantangle, quadrant = world.convert_steeringangle_to_quadrantangle(steeringAngle)

            q = np.random.randint(0, 9)
            print(q)
            ag1.action(q)

            ag1.move(quadrantangle, quadrant)

            ev = pygame.event.get()

            for event in ev:
                if event.type == pygame.QUIT:
                    running = False

            # Draw Borders
            for pair in outsideBorder:
                gfxdraw.pixel(screen, pair[0], pair[1], RED)

            for pair in insideBorder:
                gfxdraw.pixel(screen, pair[0], pair[1], RED)

            # Draw Start Line
            pygame.draw.line(screen, GREEN, startCoords[0], startCoords[1])
            # Draw Finish Line
            pygame.draw.line(screen, BLUE, finishCoords[0], finishCoords[1])
            pygame.draw.polygon(screen, BLUE, [finishCoords[0], finishCoords[1], deadzoneCoords[1], deadzoneCoords[0]], 0)
            # Draw Dead Zone Line
            pygame.draw.line(screen, RED, deadzoneCoords[0], deadzoneCoords[1])
            pygame.draw.polygon(screen, RED, [deadzoneCoords[0], deadzoneCoords[1], startCoords[1], startCoords[0]], 0)
            # Draw Agent
            pygame.draw.circle(screen, BLUE, agentPos, 8)
            # Draw Direction line (Visual Only)
            world.draw_direction_line(screen, agentPos, quadrantangle, quadrant)

            pygame.display.update()

            ######## RUN DQN ALGO #############


if __name__ == '__main__':
    x = np.array([[0, 99],
                  [29, -53],
                  [-5, -20],
                  [23, -6],
                  [-14, -7],
                  [14, 8]])

    inputs = normalise(x)

    model = Network(inputs.shape)
    output1 = forward_step(inputs, model.weights1, 'relu')
    output2 = forward_step(output1, model.weights2, 'relu')
    output3 = forward_step(output2, model.weights3, 'relu')
    print(model.weights1)
    print("###########")
    print(output2)
    print("###########")
    print(output3)

    #main()



