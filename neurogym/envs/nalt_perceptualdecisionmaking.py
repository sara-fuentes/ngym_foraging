#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 17:39:17 2019

@author: molano


Perceptual decision-making task, based on

  Bounded integration in parietal cortex underlies decisions even when viewing
  duration is dictated by the environment.
  R Kiani, TD Hanks, & MN Shadlen, JNS 2008.

  http://dx.doi.org/10.1523/JNEUROSCI.4761-07.2008

  But allowing for more than 2 choices.

"""

import numpy as np
from gym import spaces
import neurogym as ngym


class nalt_PerceptualDecisionMaking(ngym.PeriodEnv):
    metadata = {
        'description': '''N-alternative forced choice task in which the subject
         has to integrate N stimuli to decide which one is higher
          on average.''',
        'paper_link': None,
        'paper_name': None,
        'timing': {
            'fixation': ('constant', 500),
            'stimulus': ('truncated_exponential', [330, 80, 1500]),
            'decision': ('constant', 500)},
        'tags': ['perceptual', 'n-alternative', 'supervised']
    }

    def __init__(self, dt=100, rewards=None, timing=None, stimEv=1., n_ch=3):
        """
        N-alternative forced choice task in which the subject has
        to integrate N stimuli to decide which one is higher on average.
        dt: Timestep duration. (def: 100 (ms), int)
        rewards:
            R_ABORTED: given when breaking fixation. (def: -0.1, float)
            R_CORRECT: given when correct. (def: +1., float)
            R_FAIL: given when incorrect. (def: 0., float)
        timing: Description and duration of periods forming a trial.
        stimEv: Controls the difficulty of the experiment. (def: 1., float)
        n_ch: Number of choices. (def: 3, int)
        """
        super().__init__(dt=dt, timing=timing)
        self.n = n_ch
        self.choices = np.arange(n_ch) + 1
        # cohs specifies the amount of evidence (which is modulated by stimEv)
        self.cohs = np.array([0, 6.4, 12.8, 25.6, 51.2])*stimEv
        # Input noise
        sigma = np.sqrt(2*100*0.01)
        self.sigma_dt = sigma / np.sqrt(self.dt)

        # Rewards
        reward_default = {'R_ABORTED': -0.1, 'R_CORRECT': +1.,
                          'R_FAIL': 0.}
        if rewards is not None:
            reward_default.update(rewards)
        self.R_ABORTED = reward_default['R_ABORTED']
        self.R_CORRECT = reward_default['R_CORRECT']
        self.R_FAIL = reward_default['R_FAIL']

        self.abort = False
        # action and observation spaces
        self.action_space = spaces.Discrete(n_ch+1)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(n_ch+1,),
                                            dtype=np.float32)

    def new_trial(self, **kwargs):
        """
        new_trial() is called when a trial ends to generate the next trial.
        The following variables are created:
            durations, which stores the duration of the different periods (in
            the case of perceptualDecisionMaking: fixation, stimulus and decision periods)
            ground truth: correct response for the trial
            coh: stimulus coherence (evidence) for the trial
            obs: observation
        """
        # ---------------------------------------------------------------------
        # Trial
        # ---------------------------------------------------------------------
        self.trial = {
            'ground_truth': self.rng.choice(self.choices),
            'coh': self.rng.choice(self.cohs),
        }
        self.trial.update(kwargs)
        # ---------------------------------------------------------------------
        # Periods
        # ---------------------------------------------------------------------
        self.add_period('fixation', after=0)
        self.add_period('stimulus', after='fixation')
        self.add_period('decision', after='stimulus', last_period=True)

        self.set_ob('fixation', [1] + [0]*self.n)
        ob = self.view_ob('stimulus')
        ob[:, 0] = 1
        ob[:, 1:] = (1 - self.trial['coh']/100)/2
        ob[:, self.trial['ground_truth']] = (1 + self.trial['coh']/100)/2
        ob[:, 1:] += np.random.randn(ob.shape[0], self.n) * self.sigma_dt

        self.set_groundtruth('fixation', 0)
        self.set_groundtruth('stimulus', 0)
        self.set_groundtruth('decision', self.trial['ground_truth'])

    def _step(self, action, **kwargs):
        """
        _step receives an action and returns:
            a new observation, obs
            reward associated with the action, reward
            a boolean variable indicating whether the experiment has end, done
            a dictionary with extra information:
                ground truth correct response, info['gt']
                boolean indicating the end of the trial, info['new_trial']
        """
        # ---------------------------------------------------------------------
        # Reward and observations
        # ---------------------------------------------------------------------
        new_trial = False

        obs = self.obs_now
        gt = self.gt_now

        reward = 0
        if self.in_period('fixation'):
            if action != 0:
                new_trial = self.abort
                reward = self.R_ABORTED
        elif self.in_period('decision'):
            if action != 0:
                new_trial = True
                if action == gt:
                    reward = self.R_CORRECT
                else:
                    reward = self.R_FAIL

        return obs, reward, False, {'new_trial': new_trial, 'gt': gt}


if __name__ == '__main__':
    env = nalt_PerceptualDecisionMaking()
    ngym.utils.plot_env(env)
