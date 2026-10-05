import gym
from gym import spaces
import numpy as np


class s57aisEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, render_mode=None):
        super().__init__()
        self.action_space = spaces.Box()