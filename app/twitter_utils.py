from datetime import datetime

TWITTER_CHAR_LIMIT = 280


def sort_games_by_date(games_list, reverse=False):
    return sorted(games_list, reverse=reverse, key=lambda k: k["first_release_date"])


def count_games_under_char_limit(games_list, extra_chars_count, date_format):
    char_count = 0
    games_count = 0

    for game in games_list:
        char_count += len(
            f"({datetime.fromtimestamp(game['first_release_date']).strftime(date_format)}) {game['name']}\n"
        )
        if char_count >= TWITTER_CHAR_LIMIT - extra_chars_count:
            break
        games_count += 1

    return games_count


def create_past_releases_message(games_list):
    message = f"[{datetime.utcnow().strftime('%d/%m/%Y')}]\n"

    if len(games_list) == 0:
        return message + "No game has ever been released on this day."

    some_games = "Some games that were released on that day throughout the years:\n\n"
    games_count = count_games_under_char_limit(
        games_list, len(message + some_games), "%Y"
    )
    message += some_games

    for game in sort_games_by_date(games_list[:games_count]):
        message += f"({datetime.fromtimestamp(game['first_release_date']).year}) {game['name']}\n"
    print("Total char count:", len(message))

    return message


def create_upcoming_releases_week_message(games_list):
    if len(games_list) == 0:
        return ["I have not found any releases worth mentioning this week :("]

    messages_list = [f"{datetime.utcnow().strftime('%B %Y')} upcoming releases:\n\n"]
    date_format = "%d.%m"
    releases = sort_games_by_date(games_list)
    main_post = True
    replies_count = 0

    while releases:
        if replies_count > len(messages_list) - 1:
            messages_list.append("")

        games_count = count_games_under_char_limit(
            releases, len(messages_list[replies_count] + "1/1"), date_format
        )

        for i in range(games_count):
            game = releases.pop(0)
            messages_list[
                replies_count
            ] += f"({datetime.fromtimestamp(game['first_release_date']).strftime(date_format)}) {game['name']}\n"

        replies_count += 1

    if len(messages_list) > 1:
        for i in range(len(messages_list)):
            messages_list[i] += f"{i+1}/{len(messages_list)}"

    return messages_list


def create_upcoming_releases_month_message(games_list):

    return message


if __name__ == "__main__":
    import os

    from another_igdb_wrapper import AnotherIGDBWrapper

    igdb = AnotherIGDBWrapper(os.getenv("IGDB_ID"), os.getenv("IGDB_SECRET"))
    test = igdb.get_this_month_releases()
    print("\n".join(create_upcoming_releases_week_message(test)))
