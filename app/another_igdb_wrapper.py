import logging
import os
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from functools import wraps

import requests
from igdb.wrapper import IGDBWrapper


class AnotherIGDBWrapper:
    def __init__(self, client_id, client_secret):
        logging.info("Initializing IGDB wrapper...")
        igdb_access_token = self.__get_access_token(client_id, client_secret)
        self.wrapper = igdb_wrapper = IGDBWrapper(client_id, igdb_access_token)
        logging.info("Wrapper successfuly initialized!")

    @staticmethod
    def __get_access_token(client_id, client_secret):
        logging.info("Obtaining IGDB access token...")
        token_url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
        response = requests.post(token_url).json()

        return response["access_token"]

    @staticmethod
    def __get_date_range(min_date, max_date):
        logging.info("Creating date list...")
        date_range = []
        date = min_date

        while date < max_date:
            date_range.append(
                datetime(
                    date.year, date.month, date.day, 0, 0, tzinfo=timezone.utc
                ).timestamp()
            )
            date += timedelta(days=1)

        return date_range  # list of floats

    @staticmethod
    def __get_date_year_range(
        min_year, max_year, month=datetime.utcnow().month, day=datetime.utcnow().day
    ):
        logging.info("Creating date year list...")
        years = range(min_year, max_year + 1)
        date_range = [
            datetime(year, month, day, 0, 0, tzinfo=timezone.utc).timestamp()
            for year in years
        ]

        return date_range  # list of floats

    @staticmethod
    def __create_date_query_string(dates, only_first=False):
        logging.info("Creating date query...")
        dates_str_list = [str(int(x)) for x in dates]
        release_date_key = "first_release_date" if only_first else "release_dates.date"
        filter_string = " | ".join([f"{release_date_key}={d}" for d in dates_str_list])

        return filter_string

    def __get_games(self, filter_string):
        logging.info("Sending request to IGDB 'games' endpoint...")
        game_byte_array = self.wrapper.api_request(
            "games",
            f"fields id, name, follows, release_dates.date, release_dates.platform.abbreviation, first_release_date, cover.url; where {filter_string}; sort follows desc; limit 500;",
        )

        return eval(game_byte_array)

    def get_games_released_on(self, date):
        logging.info(
            f"Creating a request to get games released on {date.strftime('%d/%m/%Y')}..."
        )
        dates = self.__get_date_year_range(1970, date.year, date.month, date.day)
        filter_queries = [
            "follows != null",
            "version_parent = null",
            f"({self.__create_date_query_string(dates, only_first=True)})",
        ]
        filter_string = " & ".join(filter_queries)

        return self.__get_games(filter_string)

    def get_games_released_in_range(self, min_date, max_date):
        logging.info(
            f"Creating a request to get games released between {min_date.strftime('%d/%m/%Y')}-{max_date.strftime('%d/%m/%Y')}..."
        )
        dates = self.__get_date_range(min_date, max_date)
        filter_queries = [
            "follows != null",
            "version_parent = null",
            "release_dates.platform != (34,39,55,82)",
            f"({self.__create_date_query_string(dates, only_first=True)})",
        ]
        filter_string = " & ".join(filter_queries)
        games = self.__get_games(filter_string)

        for game in games:
            game["release_dates"] = list(
                filter(
                    lambda rd: "date" in rd.keys() and rd["date"] in dates,
                    game["release_dates"],
                )
            )

        return games

    def get_upcoming_game_releases(self, start_date, days_forward):
        logging.info(
            f"Getting upcoming releases for the next {days_forward} days from {start_date.strftime('%d/%m/%Y')}..."
        )
        return self.get_games_released_in_range(
            start_date, start_date + timedelta(days=days_forward)
        )

    def get_this_week_releases(self):
        logging.info("Getting this week releases...")
        now = datetime.utcnow()
        month_days_left = monthrange(now.year, now.month)[1] - now.day
        days_forward = min(7, month_days_left)

        return self.get_upcoming_game_releases(datetime.utcnow(), days_forward)

    def get_this_month_releases(self):
        logging.info("Getting this month releases...")
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, 1, 0, 0, tzinfo=timezone.utc)
        days_forward = monthrange(now.year, now.month)[1]

        return self.get_upcoming_game_releases(start_date, days_forward - 1)

    def download_game_cover(self, url):
        logging.info("Downloading game cover...")
        cover_url = url.lstrip("//").replace("t_thumb", "t_cover_big")
        os.system(f"wget {cover_url}")
        file_name = cover_url.split("/")[-1]

        return file_name
