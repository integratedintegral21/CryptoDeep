import datetime
import os.path
import sys
import logging
import argparse

import numpy as np

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
    logging.info("Predicting for {0}".format(now))
    scraper = CryptodatadownloadScraper(current_dir + '/cache')

    latest_record = scraper.get_latest_record(crypto, currency)
    current_timestamp = latest_record.timestamp
    sequence = []
    for i in range(30):
        record = scraper.get_record_by_date(current_timestamp, crypto, currency)
        previous_timestamp = current_timestamp - datetime.timedelta(days=1)
        daily_records = scraper.get_records_between_dates(previous_timestamp, current_timestamp, crypto, currency)
        daily_max = max([rec.high for _, rec in daily_records.items()])
        daily_min = min([rec.low for _, rec in daily_records.items()])
        previous_record = list(daily_records.values())[-1]
        daily_open = previous_record.open
        daily_close = record.close
        logging.debug("Data for {0}: Open: {1}, High: {2}, Low: {3}, Close: {4}".format(current_timestamp,
                                                                                        daily_open,
                                                                                        daily_max,
                                                                                        daily_min,
                                                                                        daily_close))
        sequence.insert(0, [daily_open, daily_max, daily_min, daily_close])
        current_timestamp = previous_timestamp
    sequence = np.asarray(sequence).astype(float)
    logging.debug("Neural network input: {0}".format(sequence))
    logging.info("Predicting...")
    return inference.main([sequence],
                          os.path.dirname(__file__) + '/../NN/scaler.joblib',
                          os.path.dirname(__file__) + '/../NN/logs/checkpoint-1d-30-back')


if __name__ == "__main__":
    args = parse_args()
    main(args.crypto, args.currency)
