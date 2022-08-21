import datetime
import os.path
import sys
import logging
import argparse
import pickle

import numpy as np

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.abspath(parent_dir))

SEQUENCE_LEN = 30

from NN import inference
from logic.scraper.web_scraper import CryptodatadownloadScraperDB, config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--crypto', required=True, help='Cryptocurrency symbol.')
    parser.add_argument('--currency', required=True, help='Currency symbol.')
    parser.add_argument('--save_dir', required=True, help='Directory where the results are saved.')
    return parser.parse_args()


def main(crypto, currency, save_dir):
    logging.basicConfig(level=logging.INFO)

    # Retrieve last 30 days
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    logging.info("Predicting at {0}".format(now))
    db_config = config(filename=os.path.dirname(__file__) + '/../logic/scraper/db_config/database.ini')
    scraper = CryptodatadownloadScraperDB('ETH', 'GBP', 'localhost', 'cryptodb', 'cryptodb', 'cryptodb',
                                          os.path.dirname(__file__) + '/cache')

    latest_record = scraper.get_latest_record()
    logging.debug("Latest record available at {0}".format(latest_record.timestamp))
    current_timestamp = latest_record.timestamp
    sequence = []
    for i in range(SEQUENCE_LEN):
        record = scraper.get_record_by_date(current_timestamp)
        previous_timestamp = current_timestamp - datetime.timedelta(days=1)
        daily_records = scraper.get_records_between_dates(previous_timestamp, current_timestamp)
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
    [prediction] = inference.main([sequence],
                                  os.path.dirname(__file__) + '/../NN/scaler.joblib',
                                  os.path.dirname(__file__) + '/../NN/logs/checkpoint-1d-'
                                  + str(SEQUENCE_LEN) + '-back')
    prediction_date = latest_record.timestamp + datetime.timedelta(days=1)
    filename = 'prediction_' + crypto + currency + now.strftime('%Y-%m-%d-%H-%M-%S') + '.pkl'
    save_path = os.path.join(save_dir, filename)
    with open(save_path, 'wb') as f:
        pickle.dump({prediction_date: prediction}, f)


if __name__ == "__main__":
    args = parse_args()
    main(args.crypto, args.currency, args.save_dir)
