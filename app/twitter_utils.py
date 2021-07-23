from datetime import datetime

TWITTER_CHAR_LIMIT = 280


def sort_games_by_first_release_date(games, reverse=False):
    return sorted(games, reverse=reverse, key=lambda k: k["first_release_date"])


def sort_games_by_release_date(games, reverse=False):
    return sorted(games, reverse=reverse, key=lambda k: k["release_dates"][0]["date"])


def count_games_under_char_limit(games, extra_chars_count, date_format):
    char_count = 0
    games_count = 0

    for game in games:
        char_count += len(
            f"({datetime.fromtimestamp(game['first_release_date']).strftime(date_format)}) {game['name']}\n"
        )
        if char_count >= TWITTER_CHAR_LIMIT - extra_chars_count:
            break
        games_count += 1

    return games_count


def create_past_releases_message(games):
    message = f"[{datetime.utcnow().strftime('%d.%m.%Y')}]\n"

    if len(games) == 0:
        return message + "No game has ever been released on this day."

    some_games = "Some games that were released on that day throughout the years:\n\n"
    games_count = count_games_under_char_limit(games, len(message + some_games), "%Y")
    message += some_games

    for game in sort_games_by_first_release_date(games[:games_count]):
        message += f"({datetime.fromtimestamp(game['first_release_date']).year}) {game['name']}\n"
    print("Total char count:", len(message))

    return message


def create_platform_tag_string(game_release_dates):
    platforms = [
        platform["platform"]["abbreviation"] for platform in game_release_dates
    ]
    platforms = list(set(platforms))
    platforms.sort()

    return f"[{'|'.join(platforms)}]"


def create_upcoming_releases_message(games, week=False):
    if len(games) == 0:
        return ["I have not found any releases worth mentioning this week :("]

    base = (
        f"Upcoming releases for this week of {datetime.utcnow().strftime('%B %Y')}\n\n"
        if week
        else f"{datetime.utcnow().strftime('%B %Y')} upcoming releases:\n\n"
    )
    messages = [base]
    date_format = "%d.%m"
    releases = sort_games_by_release_date(games)
    main_post = True
    replies_count = 0

    while releases:
        if replies_count > len(messages) - 1:
            messages.append("")

        while releases and len(messages[replies_count]) < TWITTER_CHAR_LIMIT:
            game = releases.pop(0)
            messages[
                replies_count
            ] += f"({datetime.fromtimestamp(game['release_dates'][0]['date']).strftime(date_format)}) {game['name']} {create_platform_tag_string(game['release_dates'])}\n"

        replies_count += 1

    if len(messages) > 1:
        for i in range(len(messages)):
            messages[i] += f"{i+1}/{len(messages)}"

    return messages


if __name__ == "__main__":
    import os

    from another_igdb_wrapper import AnotherIGDBWrapper

    igdb = AnotherIGDBWrapper(os.getenv("IGDB_ID"), os.getenv("IGDB_SECRET"))
    test = igdb.get_this_month_releases()
    # print(test)
    # create_upcoming_releases_message(test)
    print("\n".join(create_upcoming_releases_message(test, week=True)))
