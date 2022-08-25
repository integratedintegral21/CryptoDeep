import datetime
import logging
import os
import psycopg2
import pytz
import urllib3
import pandas as pd
from abc import ABC, abstractmethod
from configparser import ConfigParser

from logic.model import crypto_record


def config(filename=os.path.dirname(__file__) + '/db_config/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


class WebScraperDB(ABC):
    @abstractmethod
    def update_db(self):
        pass

    @abstractmethod
    def get_record_by_date(self, timestamp):
        pass

    @abstractmethod
    def get_latest_record(self):
        pass

    @abstractmethod
    def get_records_between_dates(self, first_timestamp, last_timestamp):
        pass


class CryptodatadownloadScraperDB(WebScraperDB):
    def __init__(self, crypto, currency, hostname, database, user, password, cache_dir):
        cur = None
        self.__latest_timestamp = None
        try:
            self.__conn = psycopg2.connect(host=hostname, database=database, user=user, password=password)
            cur = self.__conn.cursor()
            cur.execute("SELECT version()")
            logging.debug("Postgresql version: {0}".format(cur.fetchone()))
            logging.debug("Database connection: {0}".format(self.__conn))

            # Create table(s)
            table_name = crypto + '_' + currency + '_records'
            create_table_sql = "CREATE TABLE IF NOT EXISTS " + table_name \
                               + " ( record_id SERIAL PRIMARY KEY," \
                               + 'timestamp TIMESTAMP NOT NULL,' \
                               + 'open DOUBLE PRECISION NOT NULL,' \
                               + 'high DOUBLE PRECISION NOT NULL,' \
                               + 'low DOUBLE PRECISION NOT NULL,' \
                               + 'close DOUBLE PRECISION NOT NULL)'
            cur.execute(create_table_sql)
            self.__conn.commit()

            # Get the latest record if the table is not empty
            cur.execute("SELECT MAX(timestamp) from {0}".format(table_name))
            (self.__latest_timestamp,) = cur.fetchone()
            if self.__latest_timestamp is not None:
                self.__latest_timestamp = pytz.timezone('UTC').localize(self.__latest_timestamp)
        except psycopg2.DatabaseError as e:
            logging.error(e)
        finally:
            if cur is not None:
                cur.close()

        self.__cache_dir = cache_dir
        os.makedirs(self.__cache_dir, exist_ok=True)
        self.crypto = crypto
        self.currency = currency

    def __del__(self):
        if self.__conn is not None:
            self.__conn.close()

    def __insert_latest_records(self, df):
        latest_records = []
        latest_df_timestamp = max(df['date'])
        if self.__latest_timestamp is None:
            latest_records = df.to_numpy()[:, [1, 3, 4, 5, 6]]
            self.__latest_timestamp = latest_df_timestamp
        elif self.__latest_timestamp < latest_df_timestamp:
            latest_records = df.loc[df['date'] > self.__latest_timestamp].to_numpy()[:, [1, 3, 4, 5, 6]]
            self.__latest_timestamp = latest_df_timestamp
        table_name = self.crypto + '_' + self.currency + '_records'
        cur = None
        logging.info("Found {0} new records".format(len(latest_records)))
        try:
            cur = self.__conn.cursor()
            for date, opening, high, low, closing in latest_records:
                insert_sql = "INSERT INTO " + table_name + "(timestamp, open, high, low, close) VALUES(%s, %s, %s, " \
                                                           "%s, %s) "
                cur.execute(insert_sql, (date.strftime("%Y-%m-%d %H:%M:%S"), opening, high, low, closing))
            self.__conn.commit()
        except psycopg2.DatabaseError as e:
            logging.error(e)
        finally:
            if cur is not None:
                cur.close()

    def update_db(self):
        download_link = 'https://www.cryptodatadownload.com/cdd/Bitstamp_{0}{1}_1h.csv'.format(self.crypto,
                                                                                               self.currency)
        logging.info("Downloading {0}".format(download_link))
        http = urllib3.PoolManager()
        r = http.request('GET', download_link, preload_content=False)
        if r.status != 200:
            return False
        chunk_size = 512
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        download_file_path = os.path.join(self.__cache_dir, 'download_'
                                          + self.crypto
                                          + self.currency
                                          + '_'
                                          + now.strftime("%Y-%m-%d-%H-%M-%S")
                                          + '.csv')
        data_file_path = os.path.join(self.__cache_dir, 'data_'
                                      + self.crypto
                                      + self.currency
                                      + '_'
                                      + now.strftime("%Y-%m-%d-%H-%M-%S")
                                      + '.csv')
        with open(download_file_path, 'wb') as out:
            while True:
                data = r.read(chunk_size)
                if not data:
                    break
                out.write(data)
        with open(download_file_path, 'rt') as downloaded_f, open(data_file_path, 'wt') as data_f:
            # drop first line
            _ = downloaded_f.readline()
            for line in iter(downloaded_f):
                data_f.write(line)
        os.remove(download_file_path)
        df = pd.read_csv(data_file_path)
        df['date'] = df['date'].apply(lambda dt: pytz.timezone('UTC').localize(
            datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')))
        self.__insert_latest_records(df)
        os.remove(data_file_path)
        logging.info("Database updated successfully.")

    def get_record_by_date(self, timestamp):
        return self.get_records_between_dates(timestamp, timestamp).get(timestamp)

    def get_latest_record(self):
        return self.get_record_by_date(self.__latest_timestamp)

    def get_records_between_dates(self, first_timestamp, last_timestamp):
        cur = None
        records = dict()
        try:
            cur = self.__conn.cursor()
            table_name = self.crypto + '_' + self.currency + '_records'
            first_timestamp_str = first_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            last_timestamp_str = last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("SELECT * FROM {0} WHERE timestamp BETWEEN %s AND %s".format(table_name),
                        (first_timestamp_str, last_timestamp_str))
            result = cur.fetchall()
            if result is not None:
                for r in result:
                    timestamp = pytz.timezone('UTC').localize(r[1])
                    record = crypto_record.CryptoRecord(timestamp, r[2], r[3], r[4], r[5], self.crypto, self.currency)
                    records.update({timestamp: record})
        except psycopg2.DatabaseError as e:
            logging.error(e)
        finally:
            if cur is not None:
                cur.close()
        return records
