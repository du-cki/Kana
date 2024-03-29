# Kanapy

This is a multi-purpose personal [Discord](https://discord.com) bot written in Python.

### Tech

- [discord.py](https://github.com/Rapptz/discord.py) - An API wrapper for Discord written in Python.

### Installation & Setup

This project requires [Python](https://www.python.org/) 3.11+, [Poetry](https://python-poetry.org/) and a valid [Rust](https://www.rust-lang.org/) compiler installed. [ffmpeg](https://ffmpeg.org) is also recommended to be installed for the [`Download Cog`](cogs/download.py).

1. **Installing Packages**
   `python3.11 -m poetry install --no-root`

2. **Setup Configurations**
   Rename the `Config-example.toml` file to `Config.toml` and fill in the variables. (don't change the config values prefixed with `_`)

3. **Run The Bot**
   `python3.11 -m poetry run python bot.py`

### Running Your Instance in the background 

You could use a Process Manager like [PM2](https://pm2.keymetrics.io/), [Docker](https://www.docker.com/) or even [systemd](https://systemd.io/).
There are examples of each in the [examples](examples/) folder.

### License

This project is licensed under MIT.
