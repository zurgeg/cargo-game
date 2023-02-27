from gymnasium.envs.registration import register
from gymnasium import make
import cargo_game

register(
     id="CargoGame/Cargo-v0",
     entry_point="cargo_ai:CargoEnv",
     max_episode_steps=300,
)

env = make(
    id="CargoGame/Cargo-v0"
)
observation, info = env.reset()
for _ in range(10):
    action = env.action_space.sample()  # agent policy that uses the observation and info
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()
cargo_game.board_log.close()