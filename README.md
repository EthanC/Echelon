# Echelon

Echelon is a utility for Reddit Moderators to keep track of Modqueue and Unmoderated queue sizes by notifying via Discord Webhook.

## Requirements

-   [Python 3.7](https://www.python.org/downloads/release/python-370/)
-   [praw](https://praw.readthedocs.io/en/latest/getting_started/installation.html)
-   [requests](https://pypi.org/project/requests/)
-   [coloredlogs](https://pypi.org/project/coloredlogs/)

## Usage

Open `configuration_example.json` in your preferred text editor and fill in the configurable values. Once finished, save and rename the file to `configuration.json`.

Echelon is designed to be ran using a scheduler, such as [cron](https://en.wikipedia.org/wiki/Cron).

```
python echelon.py
```
