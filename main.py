import logging
import os
from datetime import datetime

from app.another_igdb_wrapper import AnotherIGDBWrapper
from app.twitter_utils import create_upcoming_releases_message

DATE_NOW = datetime.utcnow()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"debug_{DATE_NOW.strftime('%d_%m_%Y')}.log"),
        logging.StreamHandler(),
    ],
)

igdb = AnotherIGDBWrapper(os.getenv("IGDB_ID"), os.getenv("IGDB_SECRET"))
test = igdb.get_this_week_releases()
# print(test)
# create_upcoming_releases_message(test)
print("\n".join(create_upcoming_releases_message(test, week=True)))
