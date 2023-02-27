from gymnasium.envs.registration import register

register(
     id="CargoGame/Cargo-v0",
     entry_point="cargo_env.CargoEnv",
     max_episode_steps=300,
)