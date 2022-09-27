import sys

import numpy as np
import tensorflow.keras
import pandas as pd
import sklearn as sk

import tensorflow as tf
from tensorflow import keras

from collections import deque
import pygame
import time
import random

import world

EPISODES = 1_000
REPLAY_MEMORY_SIZE = 10_000
MIN_REPLAY_SIZE = 512
BATCH_SIZE = 32


def startup():
    print(f"Tensor Flow Version: {tf.__version__}")
    print(f"Keras Version: {tensorflow.keras.__version__}")
    print()
    print(f"Python {sys.version}")
    print(f"Pandas {pd.__version__}")
    print(f"Scikit-Learn {sk.__version__}")
    gpu = len(tf.config.list_physical_devices('GPU')) > 0
    print("GPU is", "available" if gpu else "NOT AVAILABLE")
    print("Successful startup!" if gpu else "ERROR!")


class DQNAgent:
    def __init__(self, state_shape, action_shape, file=None):
        # Main model
        if file:
            self.model = keras.models.load_model(file)
        else:
            self.model = self.create_model(state_shape, action_shape)

        # Target network
        self.target_model = self.create_model(state_shape, action_shape)
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

    def create_model(self, state_shape, action_shape):
        """ The agent maps X-states to Y-actions
        e.g. The neural network output is [.1, .7, .1, .3]
        The highest value 0.7 is the Q-Value.
        The index of the highest action (0.7) is action #1.
        """
        learning_rate = 0.001
        init = tf.keras.initializers.HeUniform()
        model = keras.Sequential()

        model.add(keras.layers.Dense(6, input_shape=state_shape, activation='relu', kernel_initializer=init))
        model.add(keras.layers.Dense(6, activation='relu', kernel_initializer=init))
        model.add(keras.layers.Dense(action_shape, activation='linear', kernel_initializer=init))

        model.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                      metrics=['accuracy'])
        return model


def get_qs(model, state, step):
    return model.predict(state.reshape([1, state.shape[0]]))[0]


def train(replay_memory, modely, target_model, done):
    learning_rate = 0.5  # Learning rate
    discount_factor = 0.618  # What does this mean

    if len(replay_memory) < MIN_REPLAY_SIZE:
        return
    if len(replay_memory) == MIN_REPLAY_SIZE:
        print("reached min_replay")

    mini_batch = random.sample(replay_memory, BATCH_SIZE)

    current_states = np.array([transition[0] for transition in mini_batch])
    current_qs_list = modely.predict(current_states)

    new_current_states = np.array([transition[3] for transition in mini_batch])
    future_qs_list = target_model.predict(new_current_states)

    X = []
    Y = []

    for index, (observation, action, reward, new_observation, done) in enumerate(mini_batch):
        if not done:
            max_future_q = reward + discount_factor * np.max(future_qs_list[index])
        else:
            max_future_q = reward

        current_qs = current_qs_list[index]
        # print("action {} , cqs: {}".format(action, current_qs[action]))
        current_qs[action] = (1 - learning_rate) * current_qs[action] + learning_rate * max_future_q

        X.append(observation)
        Y.append(current_qs)

    modely.fit(np.array(X), np.array(Y), batch_size=BATCH_SIZE, verbose=0, shuffle=True)


def main():

    # DQN Variables
    epsilon = 1  # Epsilon-greedy algorithm in initialized at 1 meaning every step is random at the start
    max_epsilon = 1  # You can't explore more than 100% of the time
    min_epsilon = 0.01  # At a minimum, we'll always explore 1% of the time
    decay = 0.01
    steps_to_update_target_model = 0

    # 1. Initialize DQNAgent  (includes creating Main & Target models
    #load = 'Archive/Models/'

    one = (12,)
    two = 9
    agent_dqn = DQNAgent(one, two)

    for episode in range(EPISODES):
        # screen = world.buildScreen()
        #
        # # Converting to less nested array - faster execution
        # borders = world.get_borders("stage3.png")
        # outsideBorder = borders[0]
        # insideBorder = borders[1]

        # # Initialise start, finish & deadzone coords line coordinates
        # startCoords, finishCoords, deadzoneCoords = world.generate_start_finish(outsideBorder, insideBorder)
        #
        # # Get Spawn location for agent based on midpoint of startCoords
        # spawn = world.get_spawn(startCoords)

        # # Initialise steeringangle
        # spawn = np.array(spawn)
        # point2 = np.array(startCoords)
        # steering_angle = int(world.initialise_steering_angle(spawn, point2[0], startCoords, deadzoneCoords))

        env = world.Env()
        spawn, init_steering_angle = env.reset()
        ag1 = world.Agent(spawn, init_steering_angle)

        detectedVectors = world.radar((ag1.x, ag1.y), ag1.steeringAngle, env.outsideBorder, env.insideBorder)
        observation = ag1.get_observation_state(detectedVectors)

        # DQN per episode
        start_time = time.time()
        total_training_rewards = 0

        done = False
        while not done:

            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    done = True

            # Render
            env.render(ag1, True)

            ######## RUN DQN ALGO #############
            steps_to_update_target_model += 1

            random_number = np.random.rand()
            # 2. Explore using the Epsilon Greedy Exploration Strategy
            if random_number <= epsilon:
                # Explore
                action = np.random.randint(0, 9)
            else:
                # Exploit best known action
                # model dims are (batch, env.observation_space.n)
                print("*****EXPLOIT*****")
                encoded = observation
                encoded_reshaped = encoded.reshape([1, encoded.shape[0]])
                predicted = agent_dqn.model.predict(encoded_reshaped).flatten()
                action = np.argmax(predicted)

            detectedVectors = world.radar((ag1.x, ag1.y), ag1.steeringAngle, env.outsideBorder, env.insideBorder)

            new_observation, reward, done = env.step(ag1, action, detectedVectors)

            total_reward = env.total_reward
            print("Action: {} , step reward: {} , done: {}, total reward: {}".format(action, reward, done, total_reward))

            agent_dqn.replay_memory.append([observation, action, reward, new_observation, done])

            # 3. Train the Main Network using the Bellman Equation
            train(agent_dqn.replay_memory, agent_dqn.model, agent_dqn.target_model, done)

            observation = new_observation
            total_training_rewards += reward

            if done:
                duration = time.time() - start_time

                print('Episode: {} Lasted: {} Total training rewards: {}'.format(episode, duration,
                                                                                 total_training_rewards))

                if steps_to_update_target_model >= 100:
                    print('Copying main network weights to the target network weights')
                    agent_dqn.target_model.set_weights(agent_dqn.model.get_weights())
                    steps_to_update_target_model = 0

                break

            # Epsilon decay per episode
            epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay * episode)

            # Save model every 50 episodes
            if episode % 50 == 0:
                agent_dqn.target_model.save('Models/')


if __name__ == '__main__':
    startup()
    main()




