from __future__ import division

from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np


def to_map(*args):
    "produces ordered dict from given inputs"
    if isinstance(args[0], list):
        var_list = args[0]
    else:
        var_list = args
    od = OrderedDict()
    for i, v in enumerate(var_list):
        od[v] = i

    return od


def get_idx(t, start_end):
    """
    auxiliary function for defining task epochs
    """
    start, end = start_end
    return list(np.where((start <= t) & (t < end))[0])


def get_epochs_idx(dt, epochs):
    """
    function for defining task epochs
    """
    t = np.linspace(0, epochs['tmax'], int(epochs['tmax']/dt)+1)

    return t, {k: get_idx(t, v) for k, v in epochs.items() if k != 'tmax'}


def uniform(rng, dt, xmin, xmax):
    if xmin >= xmax:  # the > is to avoid issues when making xmin as big as dt
        return (xmax//dt)*dt
    else:
        return (rng.uniform(xmin, xmax)//dt)*dt


def trunc_exp(rng, dt, mean, xmin=0, xmax=np.inf):
    """
    function for generating epoch durations that are multiples of the time step
    """
    if xmin >= xmax:  # the > is to avoid issues when making xmin as big as dt
        return (xmax//dt)*dt
    else:
        while True:
            x = rng.expovariate(1/mean)
            if xmin <= x < xmax:
                return (x//dt)*dt


def divide(x, y):
    try:
        z = x/y
        if np.isnan(z):
            raise ZeroDivisionError
        return z
    except ZeroDivisionError:
        return 0


def correct_2AFC(perf):
    """
    computes performance
    """
    p_decision = perf.n_decision/perf.n_trials
    p_correct = divide(perf.n_correct, perf.n_decision)

    return p_decision, p_correct


def new_trial(t, tmax, dt, new_trial, miss, reward):
    """
    check whether a new trial should be started
    """
    # new trial?
    # tmax should the current tmax and not the general one
    if t >= tmax-dt and not new_trial:
        reward = miss
        new_trial = True

    return reward, new_trial


def compute_perf(perf, reward, num_tr_perf, tr_perf):
    if tr_perf:
        num_tr_perf += 1
        perf += (reward - perf)/num_tr_perf

    return perf, num_tr_perf


def plot_struct(env, num_steps_env=200, n_stps_plt=200,
                def_act=None, model=None, name=''):
    observations = []
    rewards = []
    actions = []
    actions_end_of_trial = []
    gt = []
    config_mat = []
    perf = []
    if model is not None:
        obs = env.reset()
    for stp in range(int(num_steps_env)):
        if model is not None:
            action, _states = model.predict(obs)
            action = [action]
        elif def_act is not None:
            action = def_act
        else:
            action = env.action_space.sample()
        obs, rew, done, info = env.step(action)
        if isinstance(info, list):
            info = info[0]
            obs = obs[0]
            rew = rew[0]
            done = done[0]
        if done:
            env.reset()
        observations.append(obs)
        if info['new_trial']:
            actions_end_of_trial.append(action)
            perf.append(rew)
        else:
            actions_end_of_trial.append(-1)
        rewards.append(rew)
        actions.append(action)
        gt.append(info['gt'])
        if 'config' in info.keys():
            config_mat.append(info['config'])
        else:
            config_mat.append([0, 0])

    rows = 3
    obs = np.array(observations)
    plt.figure()
    plt.subplot(rows, 1, 1)
    plt.imshow(obs[:n_stps_plt, :].T, aspect='auto')
    plt.title('observations')
    plt.subplot(rows, 1, 2)
    plt.plot(actions[:n_stps_plt], marker='+')
    gt = np.array(gt)
    plt.plot(np.argmax(gt[:n_stps_plt], axis=1), 'r')
    plt.title('actions')
    plt.xlim([-0.5, n_stps_plt+0.5])
    plt.subplot(rows, 1, 3)
    plt.plot(rewards[:n_stps_plt], 'r')
    plt.title('reward')
    plt.xlim([-0.5, n_stps_plt+0.5])
    plt.title(name + '  ' + str(np.mean(perf)))
    plt.show()
    return np.mean(perf)
