#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from gym import Wrapper
from gym import spaces


class PassReward(Wrapper):
    metadata = {
        'description': 'Modifies observation by adding the previous reward.',
        'paper_link': None,
        'paper_name': None,
    }

    def __init__(self, env):
        """
        Modifies observation by adding the previous reward.
        """
        super().__init__(env)
        # check if observation space is discrete
        if isinstance(env.observation_space, spaces.Discrete):
            num_inputs = env.observation_space.n
        else:
            num_inputs = env.observation_space.shape[0]
        env_oss = num_inputs
        self.observation_space = spaces.Box(-np.inf, np.inf,
                                            shape=(env_oss+1,),
                                            dtype=np.float32)
    def reset(self, step_fn=None):
        if step_fn is None:
            step_fn = self.step
        return self.env.reset(step_fn=step_fn)

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        # check if obs is not a list or a numpy array
        if not isinstance(obs, (list, np.ndarray)):
            obs = np.array([obs])
        if not isinstance(reward, (list, np.ndarray)):
            reward = np.array([reward])
        obs = np.concatenate((obs, reward))
        return obs, reward, done, info
