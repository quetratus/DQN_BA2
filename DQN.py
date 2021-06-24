import random
import sys
import os

import collections

import numpy as np
import pandas as pd
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import to_categorial
from pygame import *

from parameters import *
from setup import *
from characters import *


def draw_window(scrollingBg, penguin, fishes, enemies, score):
    # define elements on screen
    scrollingBg.draw()
    penguin.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)
        enemy.move()
    for fish in fishes:
        fish.draw(screen)
        fish.move()

    show_score(score)
    pygame.display.update()


class DQNAgent(object):
    def __init__(self, params):
        self.reward = 0
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = params['learning_rate']
        self.epsilon = 1
        self.actual = []
        self.first_layer = params['first_layer_size']
        self.second_layer = params['second_layer_size']
        self.third_layer = params['third_layer_size']
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.weights = params['weights_path']
        self.load_weights = params['load_weights']
        self.model = self.network()

    def network(self):
        model = Sequential()
        model.add(Dense(units=self.first_layer, activation='relu', input_dim=6))
        model.add(Dense(units=self.second_layer, activation='relu'))
        model.add(Dense(units=self.third_layer, activation='relu'))
        model.add(Dense(units=3, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if self.load_weights:
            model.load_weights(self.weights)
        return model

    def get_state(self, penguin, enemies, fishes):
        closest_enemy = None
        closest_fish = None
        distance_min = 1000
        for enemy in enemies:
            if distance_min > enemy.rect.left > penguin.rect.right:
                closest_enemy = enemy
        for fish in fishes:
            if distance_min > fish.rect.left > penguin.rect.right:
                closest_fish = fish
        state = [
            (closest_enemy is not None and closest_enemy.rect.left <= 852 and closest_enemy.rect.bottom >= 130) or
            (closest_fish is not None and closest_fish.rect.left <= 852 and closest_fish.bottom >= 130), # need to jump
            closest_enemy is not None and closest_enemy.rect.left <= 852 and closest_enemy.rect.bottom < 130,
            # need to duck
            closest_enemy is not None and closest_enemy.rect.left <= 200,  # imminent danger
            not penguin.isJumping and not penguin.isDucking,  # penguin is running
            penguin.isJumping,
            penguin.isDucking
        ]

        for i in range(len(state)):
            if state[i]:
                state[i] = 1
            else:
                state[i] = 0

        return np.asarray(state)

    def set_reward(self, penguin, enemies, fishes):
        self.reward = 0
        if penguin.isDead:  # punishment if penguin dies
            self.reward = -1
            return self.reward
        for enemy in enemies:
            if enemy.rect.left <= penguin.rect.left:  # Reward for bypassing the enemy
                self.reward = 5
        for fish in fishes:
            if fish.rect.left <= penguin.rect.right:
                self.reward = 50  # Reward for catching the fish
        return self.reward

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory, batch_size):
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 6)))[0])
        target_f = self.model.predict(state.reshape((1, 6)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, 6)), target_f, epochs=1, verbose=0)


def init_AI():
    # start up pygame and global variables
    pygame.init()

    # create AI-agent with the defined parameters
    params = define_parameters()
    agent = DQNAgent(params)

    display_game = sys.argv.pop()

    # check if the are weights
    weights_filepath = params['weights_path']
    if params['load_weights']:
        agent.model.load_weights(weights_filepath)
        print("weight loaded")

    no_of_trials = 0
    score_plot = []
    counter_plot = []
    record = 0

    # play the game for the number of episodes defined
    while no_of_trials < params['episodes']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # initialise global variables
        global highscore
        gamespeed = 4
        gameOver = False
        gameQuit = False
        bg_speed = 4
        # scrolling of background to the left
        scrollingBg = Background(-1 * bg_speed)
        frame = 0
        score = 0

        penguin = (Penguin(72, 64))
        # Create list of obstacle class objects
        enemies = [Enemy(gamespeed)]
        fishes = [Fish(45, 25)]

        # start game
        if not gameQuit:
            while not gameOver:
                if pygame.display.get_surface() is None:
                    print("Couldn't load display surface 2")
                    gameQuit = True
                    gameOver = True
                else:
                    # calculate epsilon
                    if not params['train']:
                        agent.epsilon = 0
                    else:
                        agent.epsilon = 1 - (no_of_trials * params['epsilon_decay_linear'])

                    # agent state
                    state_old = agent.get_state(penguin, enemies, fishes)

                    if randint(0, 1) < agent.epsilon:
                        move = to_categorical(randint(0, 2), num_classes=3)
                    else:
                        # decide on the action based on previous state
                        prediction = agent.model.predict(state_old.reshape((1, 6)))
                        move = to_categorical(np.argmax(prediction[0]), num_classes=3)

                    # execute action
                    if np.array_equal(move, [1, 0, 0]):
                        penguin.isDucking = False
                    elif np.array_equal(move, [0, 1, 0]):
                        # penguin jumping
                        if penguin.rect.bottom == GROUND_LEVEL:
                            penguin.jump()
                            penguin.isJumping = True
                            penguin.movement[1] = -1 * penguin.jumpSpeed
                    elif np.array_equal(move, [0, 0, 1]):
                        # penguin ducking
                        if not (penguin.isJumping and penguin.isDead):
                            penguin.duck()
                            penguin.isDucking = True

                    # Movement of enemies and collision
                    for enemy in enemies:
                        enemy.move()
                        if enemy.collide(penguin):
                       # enemy.movement[0] = -1 * gamespeed
                       # if pygame.sprite.collide_mask(penguin, enemy):
                            penguin.isDead = True
                        if enemy.rect.x <= 0:
                            for enemy in enemies:
                                enemies.remove(enemy)
                                enemies.append(Enemy(gamespeed))

                    for fish in fishes:
                        if fish.collide(penguin):
                       # fish.movement[0] = -1 * gamespeed
                     #   if pygame.sprite.collide_mask(penguin, fish):
                            penguin.score += 50
                            fishes.remove(fish)
                            fishes.append(Fish(45,25))
                        elif fish.rect.right <= 0:
                            fishes.remove(fish)
                            fishes.append(Fish(45, 25))

                    # Calculate reward and new state
                    state_new = agent.get_state(penguin, enemies, fishes)
                    reward = agent.set_reward(penguin, enemies, fishes)

                    # replay memory
                    if params['train']:
                        # short-term memory
                        agent.train_short_memory(state_old, move, reward, state_new, penguin.isDead)
                        # long-term memory
                        agent.remember(state_old, move, reward, state_new, penguin.isDead)

                    # score increases every 1/4 second
                    if frame % 10 == 0:
                        score += 1

                    # speed increases by time
                    if frame % 800 == 799:
                        bg_speed -= 1
                        gamespeed += 1

                    # Update screen
                    draw_window(scrollingBg, penguin, fishes, enemies, score)
                    scrollingBg.update()
                    frame += 1

                    pygame.display.update()

                    # Penguin game over, save the new highscore
                    if penguin.isDead:
                        gameOver = True
                        if penguin.score > highscore:
                            highscore = penguin.score
                            #record = penguin

                if gameQuit:
                    break

            # Gameover
            if gameOver:
                gameQuit = True
                gameOver = False
                # game over, save results
                agent.replay_new(agent.memory, params['batch_size'])

                # at the end of each episode, update the highscore
                if highscore != 0:
                    no_of_trials += 1
                    print("**************************************************************")
                    print(f'Trial number {no_of_trials}      Score: {penguin.score}')
                    score_plot.append(highscore)
                    counter_plot.append(no_of_trials)

                pygame.display.update()
            clock.tick(FPS)

    if params['train']:
        agent.model.save_weights(params['weights_path'])
    print("***************************************************")
    print("End of training")
    print("List of scores: ")
    print(*score_plot)
    print("Record : " + str(record))
    print("Entraînée sur " + str(params["episodes"]) + " épisodes")
    print("***************************************************")


init_AI()

