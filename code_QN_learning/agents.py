#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 12:22:24 2020

@author: is18902
RUN in py3env using python3
"""

import gym
import random
import numpy as np
import time
from gym.envs.registration import register
import os
clear = lambda: os.system('clear') #on Linux System
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.pyplot import draw, show, plot
import tensorflow as tf
import keras
# import tensorflow.compat.v1 as tf
# tf.disable_v2_behavior()
print("Tensorflow version: {}".format(tf.__version__))


# np.random.seed(50)

try:
    register(id='FrozenLake-v0',
        entry_point='gym.envs.toy_text:FrozenLakeEnv',
        kwargs={'map_name' : '4x4','is_slippery':False},
        max_episode_steps=100,
        reward_threshold=0.78, # optimum = .8196)
        )
except:
    pass


env_name = "CartPole-v1"
env_name = "MountainCar-v0"
env_name = "MountainCarContinuous-v0"
env_name = "Acrobot-v1"
env_name = "Pendulum-v0"
env_name = "FrozenLake-v0"

env = gym.make(env_name)

class Agent():
    def __init__(self, env):

        discrete = type(env.action_space)
        print("Discrete:", discrete)
        self.is_discrete = \
            type(env.action_space) == gym.spaces.discrete.Discrete

        if self.is_discrete:
            self.action_size = env.action_space.n
            print("Action size:", self.action_size)
        else:
            self.action_low = env.action_space.low
            self.action_high = env.action_space.high
            self.action_shape = env.action_space.shape 
            print("Action range:", self.action_low, self.action_high)
        
    def get_action(self, state):
        if self.is_discrete:
            action = random.choice(range(self.action_size))
        else:
            action = np.random.uniform(self.action_low,
                                       self.action_high,
                                       self.action_shape)
        return action

class QNAgent(Agent):
    def __init__(self, env, discount_rate=0.97, learning_rate=0.01, epsilon=1):
        super().__init__(env) #super() inherits from the superclass (Agent)
        self.state_size = env.observation_space.n
        print("State size:", self.state_size)

        self.epsilon = epsilon
        self.discount_rate = discount_rate
        self.learning_rate = learning_rate
        self.build_model()

        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer()) 

    def build_model(self):
        # tf.reset_default_graph()
        tf.compat.v1.reset_default_graph()
        # self.state_in = tf.placeholder(tf.int32, shape=[])
        self.state_in = tf.compat.v1.placeholder(tf.int32, shape=[1])

        # self.action_in = tf.placeholder(tf.int32, shape=[])
        self.action_in = tf.compat.v1.placeholder(tf.int32, shape=[1])
        # self.target_in = tf.placeholder(tf.float32, shape=[])
        self.target_in = tf.compat.v1.placeholder(tf.float32, shape=[])

        self.state = tf.one_hot(self.state_in, depth=self.state_size)
        self.action = tf.one_hot(self.action_in, depth=self.action_size)

        self.q_state = tf.layers.dense(self.state, units=self.action_size, name='q_table')
        # self.q_state = keras.layers.dense(self.state, units=self.action_size, name='q_table')
        self.q_action = tf.reduce_sum(tf.multiply(self.q_state, self.action), axis=1)

        self.loss = tf.reduce_sum(tf.square(self.target_in - self.q_action))
        self.optimizer = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)

    def get_action(self, state):
        # q_state = self.q_table[state]
        q_state = self.sess.run(self.q_state, feed_dict={self.state_in: [state]})
        action_greedy = np.argmax(q_state)
        action_random = super().get_action(state)
        return action_random if random.random() < self.epsilon else action_greedy

    def train(self, experience):
        state, action, next_state, reward, done = ([exp] for exp in experience)

        q_next = self.sess.run(self.q_state, feed_dict={self.state_in: next_state})
        q_next[done] = np.zeros([self.action_size]) 
        print("done {} state {} action {}".format(done, state, action))
        print("reward {} discount {} q_next {}".format(reward, self.discount_rate, np.max(q_next)))
        q_target = reward[0] + self.discount_rate + np.max(q_next)

        feed = {self.state_in: state, self.action_in: action, self.target_in: q_target}
        print("feed size: {}".format(len(feed)))
        # print("optimizer: {}".format(self.optimizer))
        # feed = np.reshape(feed, [1,])
        # self.sess.run(self.optimizer, feed_dict=feed)
        self.sess.run(self.optimizer, feed_dict=feed)

        if experience[4]:
        # if experience[4] and reward[0]==1:
            self.epsilon = self.epsilon * 0.99
    
    def __del__(self):
        self.sess.close() #closes TF session


def plot_q_table(data):
    # data = np.random.rand(10, 10) * 20
    length = data.shape[1]
    width = data.shape[0]

    # create discrete colormap
    cmap = colors.ListedColormap(['red', 'blue'])
    bounds = [-.01,-.1,0,.1,.01]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    # ax.imshow(data, cmap=cmap, norm=norm)
    ax.imshow(data, cmap='rainbow', norm=norm)

    # draw gridlines
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, length, 1));
    ax.set_yticks(np.arange(-.5, width, 1));

    plt.draw()
    plt.show()


# agent = Agent(env)
agent = QNAgent(env)

total_reward = 0
for ep in range(200):
    state = env.reset()
    done = False
    while not done:
        action = agent.get_action(state)
        next_state, reward, done, info = env.step(action)
        agent.train((state,action,next_state,reward,done))
        state = next_state
        total_reward += reward 

        print("state:",state," Action:",action)
        print("Eps: {} TotRew: {} epsilon: {:.2f}".format(ep, total_reward, agent.epsilon))
        env.render()
        with tf.compat.v1.variable_scope("q_table",reuse=True):
            weights = agent.sess.run(tf.get_variable("kernel"))
            print(weights)
        time.sleep(0.01)
        clear()
    
env.close()            
print("Eps: {} TotRew: {} epsilon: {:.2f}".format(ep, total_reward, agent.epsilon))
print(weights)
# plot_q_table(weights)
# print(agent.q_table)
