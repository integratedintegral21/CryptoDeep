import datetime
import os.path
import sys
import logging
import argparse

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.abspath(parent_dir))

from NN import inference
from logic.scraper.web_scraper import CryptodatadownloadScraper


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--crypto', required=True, help='Cryptocurrency symbol')
    parser.add_argument('--currency', required=True, help='Currency symbol')
    return parser.parse_args()


def main(crypto, currency):
    logging.basicConfig(level=logging.INFO)

    # Retrieve last 30 days
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    earliest_record = now - datetime.timedelta(days=30)
    logging.info("Predicting for {0}".format(now))
    scraper = CryptodatadownloadScraper(current_dir + '/cache')
    # preceding_data = scraper.get_records_between_dates(earliest_record, now, crypto, currency)

    # Get latest record
    latest_record = scraper.get_latest_record(crypto, currency)


if __name__ == "__main__":
    args = parse_args()
    main(args.crypto, args.currency)
