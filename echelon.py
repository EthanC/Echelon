import json
import logging
from datetime import datetime
from sys import exit

import coloredlogs
import praw

from util import Utility

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")


class Echelon:
    """ToDo"""

    def init(self):
        print("Echelon - Reddit Moderator Queues Watcher")
        print("https://github.com/EthanC/Echelon\n")

        initialized = Echelon.LoadConfiguration(self)

        if initialized is True:
            try:
                self.reddit = praw.Reddit(
                    username=self.username,
                    password=self.password,
                    client_id=self.clientId,
                    client_secret=self.clientSecret,
                    user_agent="Echelon by /u/LackingAGoodName (https://github.com/EthanC/Echelon)",
                )
            except Exception as e:
                log.critical(f"Failed to login to Reddit, {e}")

            if self.reddit.read_only == False:
                embed = {
                    "color": int(self.webhookColor, base=16),
                    "fields": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {
                        "text": "Lacking#0001",
                        "icon_url": "https://avatars1.githubusercontent.com/u/16727756",
                    },
                }
                fields = []

                for subreddit in self.subreddits:
                    field = Echelon.main(self, subreddit)

                    if field is not None:
                        fields.append(field)

                embed["fields"] = fields

                Echelon.Notify(self, embed)

    def main(self, subreddit: str):
        subredditName = subreddit["name"]

        if (subreddit["modqueue"] is True) or (subreddit["unmoderated"] is True):
            field = {
                "name": f"/r/{subredditName}",
                "value": "",
                "inline": self.webhookInline,
            }

            if subreddit["modqueue"] is True:
                modqueue = Echelon.GetModqueue(self, subredditName)
                modqueueURL = f"https://www.reddit.com/r/{subredditName}/about/modqueue"

                field["value"] += f"Modqueue: [{modqueue:,d}]({modqueueURL})"

            # If both Modqueue and Unmoderated are enabled, add newline seperator.
            if (subreddit["modqueue"] is True) and (subreddit["unmoderated"] is True):
                field["value"] += "\n"

            if subreddit["unmoderated"] is True:
                unmoderated = Echelon.GetUnmoderated(self, subredditName)
                unmoderatedURL = (
                    f"https://www.reddit.com/r/{subredditName}/about/unmoderated"
                )

                field["value"] += f"Unmoderated: [{unmoderated:,d}]({unmoderatedURL})"

            log.info(
                f"/r/{subredditName} - Modqueue: {modqueue:,d}, Unmoderated: {unmoderated:,d}"
            )

            return field
        else:
            log.warning(
                f"/r/{subredditName} Modqueue and Unmoderated are disabled, skipping..."
            )

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            self.username = configuration["credentials"]["username"]
            self.password = configuration["credentials"]["password"]
            self.clientId = configuration["credentials"]["clientId"]
            self.clientSecret = configuration["credentials"]["clientSecret"]
            self.subreddits = configuration["subreddits"]
            self.webhookAvatar = configuration["webhook"]["avatarURL"]
            self.webhookColor = configuration["webhook"]["embedColor"]
            self.webhookURL = configuration["webhook"]["url"]
            self.webhookUsername = configuration["webhook"]["username"]
            self.webhookInline = configuration["webhook"]["inline"]

            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")

    def GetModqueue(self, subreddit: str):
        """ToDo"""

        count = 0

        try:
            for _ in self.reddit.subreddit(subreddit).mod.modqueue(limit=None):
                count += 1
        except Exception as e:
            log.error(f"Failed to get Modqueue for /r/{subreddit}, {e}")

        # Reddit Queues are hard-limited to 1024 Submissions.
        # However, when the Queue is full (1024), the API
        # tends to fluctuate in the 990's despite being at 1024.
        if count >= 990:
            count = 1000

        return count

    def GetUnmoderated(self, subreddit: str):
        """ToDo"""

        count = 0

        try:
            for _ in self.reddit.subreddit(subreddit).mod.unmoderated(limit=None):
                count += 1
        except Exception as e:
            log.error(f"Failed to get Unmoderated for /r/{subreddit}, {e}")

        # Reddit Queues are hard-limited to 1024 Submissions.
        # However, when the Queue is full (1024), the API
        # tends to fluctuate in the 990's despite being at 1024.
        if count >= 990:
            count = 1000

        return count

    def Notify(self, embed):
        """ToDo"""

        data = {
            "username": self.webhookUsername,
            "avatar_url": self.webhookAvatar,
            "embeds": [embed],
        }

        status = Utility.Webhook(self, self.webhookURL, data)

        if status is True:
            log.info("Notified webhook of Moderator Queues")


if __name__ == "__main__":
    try:
        Echelon.init(Echelon)
    except KeyboardInterrupt:
        logging.info("Stopping...")
        exit()
