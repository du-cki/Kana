# Kanapy

Kana is a multi-purpose personal Discord bot written in Python.

### Tech

- [discord.py](https://github.com/Rapptz/discord.py) - An API wrapper for Discord written in Python!

### Installation

Kanapy requires [Python](https://www.python.org/) 3.8+ to run, to know your version run this following command `python --version`

1. **Set up venv** [ Optional ]
   `python -m venv venv`

2. **Install dependencies**
   `pip install -U -r requirements.txt`

3. **Create a `.env` file with the following template**:

```
- TOKEN=" " # Your Discord Bot Token
- USER_MONGO=" " # Your MongoDB connection URI
- PSQL_URI=" " # Your PSQL connection URI

- YOUTUBE_KEY=" " # Your YouTube Data API key, this is for the search cog, unload it if you don't have one.
```
