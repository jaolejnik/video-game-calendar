import logging
import os
from datetime import datetime
from time import sleep

from app.vgc import VideoGameCalendar

DATE_NOW = datetime.utcnow()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"debug_{DATE_NOW.strftime('%d_%m_%Y')}.log"),
        logging.StreamHandler(),
    ],
)


igdb_credentials = {
    "client_id": os.environ["IGDB_ID"],
    "client_secret": os.environ["IGDB_SECRET"],
}
twitter_credentials = {
    "consumer_key": os.environ["TWITTER_KEY"],
    "consumer_secret": os.environ["TWITTER_SECRET"],
    "access_token_key": os.environ["TWITTER_ACESS_TOKEN"],
    "access_token_secret": os.environ["TWITTER_SECRET_TOKEN"],
}

vgc = VideoGameCalendar(igdb_credentials, twitter_credentials)
vgc.post_past_releases()

if DATE_NOW.weekday() == 0:
    sleep(30 * 60)
    vgc.post_this_week_releases()
elif DATE_NOW.day == 1:
    sleep(60 * 60)
    vgc.post_this_month_releases()
