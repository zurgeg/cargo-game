import numpy as np


import cargo_game
import gymnasium as gym
from gymnasium import spaces


class CargoEnv(gym.Env):
    metadata = {"render_modes": [], "render_fps": 4}

    def __init__(self, render_mode=None):
        self._game = cargo_game.Game()
        self.size = 9  # The size of the square grid

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(0, 8, shape=(2,), dtype=int),
                "dests_locs": spaces.Box(0, 8, shape=(2,2,), dtype=int),
                "sources_locs": spaces.Box(0, 8, shape=(3,2,), dtype=int),
                "points_locs": spaces.Box(0, 8, shape=(3,2,), dtype=int),
                "cargo": spaces.Box(-1, 8, shape=(2,), dtype=int) # (-1, -1) == No cargo
            }
        )

        # We have 4 actions, corresponding to "right", "up", "left", "down"
        self.action_space = spaces.Discrete(4)

        """
        The following dictionary maps abstract actions from `self.action_space` to
        the direction we will walk in if that action is taken.
        I.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            0: self._game.truck.move_up,
            1: self._game.truck.move_down,
            2: self._game.truck.move_left,
            3: self._game.truck.move_right
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
    def _get_obs(self):
        return {"agent": self._game.truck.pos, "dests_locs": cargo_game.dests_locs, "sources_locs": cargo_game.sources_locs, "points_locs": cargo_game.points_loc, "cargo": (-1, -1) if not self._game.truck._cargo else self._game.truck._cargo._left_to_go}
    def _get_info(self):
        return {}
    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Choose the agent's location uniformly at random
        #self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        # We will sample the target's location randomly until it does not coincide with the agent's location
        #self._target_location = self._agent_location
        #while np.array_equal(self._target_location, self._agent_location):
        #    self._target_location = self.np_random.integers(
        #        0, self.size, size=2, dtype=int
        #    )

        observation = self._get_obs()
        info = self._get_info()

        #if self.render_mode == "human":
       #     self._render_frame()

        return observation, info
    def step(self, action):
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        can_move_there = self._action_to_direction[action]()
        # An episode is done iff the agent has reached the target
        reward = 1 if self._game.on_node else 0  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()
        self._game.update_board()
        cargo_game.log_board(self._game.board)

        return observation, reward, self._game.truck.make_new, self._game.truck.fuel_out, info
    def render(self):
        pass # ???
    def close(self):
        cargo_game.board_log.close()