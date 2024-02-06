from ngym_foraging.wrappers.monitor import Monitor
from ngym_foraging.wrappers.noise import Noise
from ngym_foraging.wrappers.pass_reward import PassReward
from ngym_foraging.wrappers.pass_action import PassAction
from ngym_foraging.wrappers.reaction_time import ReactionTime
from ngym_foraging.wrappers.side_bias import SideBias
from ngym_foraging.wrappers.block import RandomGroundTruth
from ngym_foraging.wrappers.block import ScheduleAttr
from ngym_foraging.wrappers.block import ScheduleEnvs
from ngym_foraging.wrappers.block import TrialHistoryV2

ALL_WRAPPERS = {'Monitor-v0': 'ngym_foraging.wrappers.monitor:Monitor',
                'Noise-v0': 'ngym_foraging.wrappers.noise:Noise',
                'PassReward-v0': 'ngym_foraging.wrappers.pass_reward:PassReward',
                'PassAction-v0': 'ngym_foraging.wrappers.pass_action:PassAction',
                'ReactionTime-v0':
                    'ngym_foraging.wrappers.reaction_time:ReactionTime',
                'SideBias-v0': 'ngym_foraging.wrappers.side_bias:SideBias',
                }

def all_wrappers():
    return sorted(list(ALL_WRAPPERS.keys()))
