import logging
import os

import twitter

from .another_igdb_wrapper import AnotherIGDBWrapper
from .twitter_utils import (
    create_past_releases_message,
    create_upcoming_releases_message,
)


class VideoGameCalendar:
    def __init__(self, igdb_credentials, twitter_credentials):
        self.igdb = AnotherIGDBWrapper(**igdb_credentials)
        self.twitter = twitter.Api(**twitter_credentials)

    def __post_thread(self, messages):
        tweet_id = None

        for i, message in enumerate(messages, 1):
            logging.info(
                f"Posting message {i} of {len(messages)}. Posting in response to tweet with id {tweet_id}..."
            )
            post_status = self.twitter.PostUpdate(
                message, in_reply_to_status_id=tweet_id
            )
            tweet_id = post_status.id

    def post_past_releases(self):
        logging.info("Posting today's past releases...")
        games = self.igdb.get_todays_past_releases()
        message = create_past_releases_message(games)
        game_cover_file = self.igdb.download_game_cover(games[0]["cover"]["url"])
        self.twitter.PostUpdate(message, game_cover_file)
        logging.info("Successfully posted to Twitter!")
        os.system("rm *.jpg")

    def post_this_week_releases(self):
        logging.info("Posting this week's upcoming releases...")
        games = self.igdb.get_this_week_releases()
        messages = create_upcoming_releases_message(games, week=True)
        self.__post_thread(messages)
        logging.info("Successfully posted to Twitter!")

    def post_this_month_releases(self):
        logging.info("Posting this month's upcoming releases...")
        games = self.igdb.get_this_month_releases()
        messages = create_upcoming_releases_message(games)
        self.__post_thread(messages)
        logging.info("Successfully posted to Twitter!")
