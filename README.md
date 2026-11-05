Hello everyone!

Here's a discord bot I've coded to manage the La Garderie discord server for the year 2024.

## Development

`main.py` uses `discord.py`, including application commands, and stores notes in JSON. It contains moderation/event handlers and the `warn`, `initialise`, `moyenne`, `clearnote` and `supprnote` functions.

Use a local Python virtual environment and install `discord.py` before working on the bot. There is no dependency lockfile or environment-variable loader in this repository. Review the bot startup configuration and Discord intents in `main.py`, and supply your own credentials locally; never publish a bot token.

Starting `python main.py` connects to Discord. Neither startup nor Discord commands were executed during this documentation check.
