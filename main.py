import os
from datetime import datetime, timezone

import requests
import twitter
from igdb.wrapper import IGDBWrapper

DATE_NOW = datetime.utcnow()
TWITTER_CHAR_LIMIT = 280


def get_access_token(client_id, client_secret):
    token_url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    response = requests.post(token_url).json()
    return response["access_token"]


def get_dates_to_request(min_year, max_year, month=DATE_NOW.month, day=DATE_NOW.day):
    years = range(min_year, max_year + 1)
    request_dates = [
        datetime(year, month, day, 0, 0, tzinfo=timezone.utc).timestamp()
        for year in years
    ]

    return request_dates  # <--- list of floats


def create_date_query(dates_posix_list):
    dates_str_list = [str(int(x)) for x in dates_posix_list]
    filter_string = " | ".join([f"first_release_date={d}" for d in dates_str_list])
    return filter_string


def get_games_list(igdb_wrapper, dates):
    game_byte_array = igdb_wrapper.api_request(
        "games",
        f"fields id, name, aggregated_rating, follows, first_release_date; where aggregated_rating > 60 & {create_date_query(dates)}; limit 250; sort follows desc;",
    )

    return eval(game_byte_array)


def filter_games_list(games_list):
    return [
        dict((key, value) for key, value in game.items())
        for game in games_list
        if "aggregated_rating" and "follows" in game.keys()
    ]


def sort_games_by_date(games_list):
    return sorted(games_list, key=lambda k: k["first_release_date"])


def count_games_under_char_limit(games_list, extra_chars=0):
    char_count = 0
    games_count = 0

    for game in games_list:
        char_count += len(
            f"({datetime.fromtimestamp(game['first_release_date']).year}) {game['name']}"
        )
        if char_count > TWITTER_CHAR_LIMIT - extra_chars:
            break
        games_count += 1

    return games_count


def create_tweet_message(games_list):
    message = f"[{DATE_NOW.strftime('%d/%m/%Y')}]\n"
    some_games = "Some games that were released on that day throughout history:\n\n"

    games_count = count_games_under_char_limit(games_list, len(message + some_games))
    if games_count > 0:
        message += some_games
        for game in sort_games_by_date(games_list[:games_count]):
            message += f"({datetime.fromtimestamp(game['first_release_date']).year}) {game['name']}\n"
    else:
        message += "No game has ever been released on this day."

    return message


def get_game_cover_url(igdb_wrapper, game_id):
    cover_byte_array = igdb_wrapper.api_request(
        "covers",
        f"fields url; where game = {game_id};",
    )
    url = eval(cover_byte_array)[0]["url"]
    return url.lstrip("//").replace("t_thumb", "t_cover_big")


def download_game_cover(igdb_wrapper, game_id):
    cover_url = get_game_cover_url(igdb_wrapper, game_id)
    os.system(f"wget {cover_url}")
    file_name = cover_url.split("/")[-1]

    return file_name


if __name__ == "__main__":
    igdb_access_token = get_access_token(
        os.environ["IGDB_ID"], os.environ["IGDB_SECRET"]
    )
    igdb_wrapper = IGDBWrapper(os.environ["IGDB_ID"], igdb_access_token)

    dates = get_dates_to_request(1970, DATE_NOW.year)

    games_list = get_games_list(igdb_wrapper, dates)
    games_list = filter_games_list(games_list)
    game_cover_file = download_game_cover(igdb_wrapper, games_list[0]["id"])

    tweet_message = create_tweet_message(games_list)
    twitter_api = twitter.Api(
        consumer_key=os.environ["TWITTER_KEY"],
        consumer_secret=os.environ["TWITTER_SECRET"],
        access_token_key=os.environ["TWITTER_ACESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_SECRET_TOKEN"],
    )
    status = twitter_api.PostUpdate(tweet_message, game_cover_file)

    os.system("rm *.jpg")
