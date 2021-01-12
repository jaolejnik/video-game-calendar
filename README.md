# Video Game Calendar :video_game:

### A Twitter bot that posts daily list of the most popular video games that were released on the same day throughout the years.

## [Follow **Video Game Calendar :video_game:** on Twitter!](https://twitter.com/vg_calendar)

## How does it work?

The script sends request to [IGBD](https://www.igdb.com/discover) to get a list of every game that
has been ever released on this day of the month since 1970. It's sorted by the amount of people
following the game, so in other words popularity. Then a message is being crafted with the most
popular titles until it exceeds Twitter's character limit. Afterwards everythings sorted by release
date and published to Twitter by TwitterAPI.

## Used packages

- [requests](https://pypi.org/project/requests/)
- [TwitterAPI](https://github.com/geduldig/TwitterAPI)
- [IGDB Python API](https://github.com/twitchtv/igdb-api-python)
