#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import ngym_foraging as ngym
from ngym_foraging import spaces

# TODO: change docstrings and comments
class Foraging(ngym.TrialEnv):
    """

    Args:
        cohs: list of float, coherence levels controlling the difficulty of
            the task
        sigma: float, input noise level
        dim_ring: int, dimension of ring input and output
    """
    metadata = {
        'paper_link': 'https://www.jneurosci.org/content/12/12/4745',
        'paper_name': '''The analysis of visual motion: a comparison of
        neuronal and psychophysical performance''',
        'tags': ['perceptual', 'two-alternative', 'supervised']
    }

    def __init__(self, dt=100, rewards=None, timing=None, probs=None,
                 sigma=1.0, dim_ring=2):
        # Initialize parent class with decision time step
        super().__init__(dt=dt)
        # noise
        self.sigma = sigma / np.sqrt(self.dt)  # Input noise

        self.abort = False
        # Rewards
        self.rewards = {'abort': -0.1, 'fixation': 0.1, 'correct': +1.}
        if rewards:  # Allow custom rewards
            self.rewards.update(rewards)

        # Define trial timing, with default and customizable options
        self.timing = {
            'ITI': ngym.random.TruncExp(600, 300, 3000),
            'fixation': 200,
            'decision': 200}  # Decision period
        if timing:  # Allow custom timing
            self.timing.update(timing)

        # Initialize choices
        self.choices = np.arange(dim_ring)  # possible choices
        # Initialize probs (default: uniform probability across choices)
        self.probs = probs or np.ones(dim_ring)/dim_ring

        # Define observations
        name = {'ITI': 0}
        self.observation_space = spaces.Discrete(2, name=name)
        # define action spaces
        name = {'no_action': 0, 'fixation': 1, 'choice': range(2, dim_ring+2)}
        self.action_space = spaces.Discrete(2+dim_ring, name=name)

    def _new_trial(self, **kwargs):
        """
        new_trial() is called when a trial ends to generate the next trial.
        The following variables are created:
            durations, which stores the duration of the different periods (in
            the case of perceptualDecisionMaking: fixation, stimulus and
            decision periods)
            ground truth: correct response for the trial
            coh: stimulus coherence (evidence) for the trial
            obs: observation
        """
        # TODO: allow modifying probs with kwargs
        # Trial info
        trial = {'probs': self.probs}

        trial.update(kwargs)  # Update trial with any additional parameters

        ground_truth =\
            self.choices[np.where(np.max(trial['probs']) == trial['probs'])[0][0]]

        # Define trial periods
        self.add_period(['ITI', 'fixation', 'decision'])

        # Generate observations for each period
        self.add_ob(0, period=['ITI'], where='ITI')
        self.add_ob(1, period=['fixation'], where='ITI')
        self.add_ob(1, period=['decision'], where='ITI')
        # Set the correct response for the decision period
        self.set_groundtruth(0, period='ITI')
        self.set_groundtruth(1, period='fixation')
        self.set_groundtruth(ground_truth, period='decision', where='choice')

        return trial

    def _step(self, action):  # processes agent's action and updates env's state
        """
        _step receives an action and returns:
            a new observation, obs
            reward associated with the action, reward
            a boolean variable indicating whether the experiment has end, done
            a dictionary with extra information:
                ground truth correct response, info['gt']
                boolean indicating the end of the trial, info['new_trial']
        """
        new_trial = False
        # rewards
        reward = 0
        gt = self.gt_now
        # observations
        if self.in_period('ITI'):
            if action != 0:  # action = 0 means fixating
                new_trial = self.abort
                reward += self.rewards['abort']
        elif self.in_period('fixation'):
            if action == 1:
                reward += self.rewards['fixation']
        elif self.in_period('decision'):
            if action > 1:
                new_trial = True
                if action == gt:
                    self.performance = 1
                rw_idx = np.where(self.action_space.name['choice'] == action)[0][0]
                prob = self.trial['probs'][rw_idx]
                reward += (self.rng.random() < prob) * self.rewards['correct']

        return self.ob_now, reward, False, {'new_trial': new_trial, 'gt': gt}


