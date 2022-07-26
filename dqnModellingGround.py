import sys

import pygame
from pygame import gfxdraw

import numpy as np
import tensorflow.keras
import pandas as pd
import sklearn as sk
import tensorflow as tf

import world

# class DQNAgent:
#     def create_model(self):
#         # Define Sequential model with 3 layers
#         model = keras.Sequential(
#             [
#                 layers.Dense(2, activation="relu", name="layer1"),
#                 layers.Dense(3, activation="relu", name="layer2"),
#                 layers.Dense(4, name="layer3"),
#             ]
#         )
#         # Call model on a test input
#         x = tf.ones((3, 3))
#         y = model(x)

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
    print(f"Tensor Flow Version: {tf.__version__}")
    print(f"Keras Version: {tensorflow.keras.__version__}")
    print()
    print(f"Python {sys.version}")
    print(f"Pandas {pd.__version__}")
    print(f"Scikit-Learn {sk.__version__}")
    gpu = len(tf.config.list_physical_devices('GPU')) > 0
    print("GPU is", "available" if gpu else "NOT AVAILABLE")

    print("working")

    main()



