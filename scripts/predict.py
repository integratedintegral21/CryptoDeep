import datetime
import os.path
import sys
import logging
import argparse
import time

import psycopg2
import pytz

import numpy as np

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.abspath(parent_dir))

SEQUENCE_LEN = 50
FORWARD = 12

from NN import inference
from logic.scraper.web_scraper import CryptodatadownloadScraperDB, config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--crypto', required=True, help='Cryptocurrency symbol.')
    parser.add_argument('--currency', required=True, help='Currency symbol.')
    return parser.parse_args()


def create_pred_table_if_exists(crypto, currency, db_conn):
    table_name = crypto + '_' + currency + '_predictions'
    cur = None
    result = False
    try:
        create_table_sql = "CREATE TABLE IF NOT EXISTS " + table_name \
                           + " ( prediction_id SERIAL PRIMARY KEY," \
                           + 'timestamp TIMESTAMP NOT NULL,' \
                           + 'close DOUBLE PRECISION NOT NULL )'
        cur = db_conn.cursor()
        cur.execute(create_table_sql)
        db_conn.commit()
        result = True
    except psycopg2.DatabaseError as e:
        logging.error(e)
    finally:
        if cur is not None:
            cur.close()
        return result


def get_latest_prediction_timestamp(crypto, currency, conn):
    table_name = crypto + '_' + currency + '_predictions'
    cur = None
    latest_timestamp = None
    try:
        cur = conn.cursor()
        latest_date_sql = 'SELECT MAX(timestamp) FROM ' + table_name
        cur.execute(latest_date_sql)
        latest_timestamp = cur.fetchone()
    except psycopg2.DatabaseError as e:
        logging.error(e)
    finally:
        if cur is not None:
            cur.close()
        if latest_timestamp != (None,):
            return pytz.timezone('UTC').localize(latest_timestamp[0])
        return latest_timestamp[0]


def insert_prediction(crypto, currency, conn, prediction_date, close):
    table_name = crypto + '_' + currency + '_predictions'
    cur = None
    result = False
    try:
        cur = conn.cursor()
        insert_sql = 'INSERT INTO ' + table_name + ' (timestamp, close) VALUES (%s, %s)'
        cur.execute(insert_sql, (prediction_date.strftime("%Y-%m-%d %H:%M:%S"), close))
        conn.commit()
        logging.info("Prediction for {0} inserted.".format(prediction_date))
        result = True
    except psycopg2.DatabaseError as e:
        logging.error(e)
    finally:
        if cur is not None:
            cur.close()
        return result


def predict_from(latest_record, scraper, crypto, currency):
    # Retrieve last 30 days
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    logging.info("Predicting at {0}".format(now))
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
    ckpt_path = os.path.dirname(__file__) + '/../NN/logs/checkpoint_' \
                + crypto + currency + '_1h_' + str(SEQUENCE_LEN) + '_back_' + str(FORWARD) + '_forward'
    scaler_path = os.path.dirname(__file__) + '/../NN/' + crypto + currency + '_scaler.joblib'
    prediction = inference.main([sequence],
                                scaler_path,
                                ckpt_path)
    return prediction


def main(crypto, currency):
    logging.basicConfig(level=logging.INFO)
    db_params = config()
    db_conn = psycopg2.connect(host=db_params['host'], database=db_params['database'], user=db_params['user'],
                               password=db_params['password'])
    if not create_pred_table_if_exists(crypto, currency, db_conn):
        return

    scraper = CryptodatadownloadScraperDB(crypto, currency, db_params['host'], db_params['database'], db_params['user'],
                                          db_params['password'], os.path.dirname(__file__) + '/cache')

    while True:
        logging.info("Updating predictions table...")
        scraper.update_db()
        latest_record = scraper.get_latest_record()
        prediction_date = latest_record.timestamp + datetime.timedelta(hours=FORWARD)
        latest_prediction = get_latest_prediction_timestamp(crypto, currency, db_conn)

        if latest_prediction is not None and latest_prediction >= prediction_date:
            logging.info("Predictions are up-to-date")
            time.sleep(1)
            continue

        pred = predict_from(latest_record, scraper, crypto, currency)
        insert_prediction(crypto, currency, db_conn, prediction_date, pred[0][0].astype(float))
        time.sleep(1)
    db_conn.close()


if __name__ == "__main__":
    args = parse_args()
    main(args.crypto, args.currency)
