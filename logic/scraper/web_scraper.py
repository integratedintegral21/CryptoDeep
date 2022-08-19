import datetime
import logging
import os
import glob

import numpy as np
from selenium import webdriver
import urllib3
import pandas as pd
from abc import ABC, abstractmethod
from logic.model import crypto_record


class WebScraper(ABC):
    @abstractmethod
    def get_record_by_date(self, timestamp, crypto, currency) -> crypto_record.CryptoRecord:
        pass

    @abstractmethod
    def get_records_between_dates(self, start_timestamp, end_timestamp, crypto, currency) \
            -> [crypto_record.CryptoRecord]:
        pass

    @abstractmethod
    def get_n_records_until(self, end_timestamp, crypto, currency, n_records) -> [crypto_record.CryptoRecord]:
        pass


class CoinmarketcapScraper(WebScraper):
    def __init__(self, driver_path):
        self.driver_ = webdriver.Chrome(driver_path)

    def get_record_by_date(self, timestamp, crypto, currency):
        self.driver_.get('https://coinmarketcap.com')

    def get_records_between_dates(self, start_timestamp, end_timestamp, crypto, currency):
        self.driver_.get('https://coinmarketcap.com')


class CryptodatadownloadCache:
    def __init__(self, cache_path, crypto, currency, update_period=datetime.timedelta(seconds=0)):
        self.__cache_dir_path = cache_path
        self.__update_period = update_period
        self.__cache_file = None
        self.__last_update = None
        self.crypto = crypto
        self.currency = currency
        if not os.path.isdir(self.__cache_dir_path):
            os.mkdir(self.__cache_dir_path)
        if not self.__update_cache():
            raise Exception('Unable to update cache')
        logging.debug("Created cache at {0}. Symbols: {1}/{2}. Update period:{3}. Last update: {4}.".format(
            self.__cache_dir_path,
            self.crypto,
            self.currency,
            self.__update_period,
            self.__last_update))

    def __update_cache(self):
        logging.info("Updating cache at {0}. Symbols: {1}/{2}".format(self.__cache_dir_path,
                                                                      self.crypto,
                                                                      self.currency))
        download_link = 'https://www.cryptodatadownload.com/cdd/Binance_{0}{1}_1h.csv'.format(self.crypto,
                                                                                              self.currency)
        http = urllib3.PoolManager()
        r = http.request('GET', download_link, preload_content=False)
        if r.status != 200:
            return False
        chunk_size = 512
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        download_file_path = os.path.join(self.__cache_dir_path, 'download_'
                                          + self.crypto
                                          + self.currency
                                          + '_'
                                          + now.strftime("%Y-%m-%d-%H-%M-%S")
                                          + '.csv')
        data_file_path = os.path.join(self.__cache_dir_path, 'data_'
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
        if self.__cache_file is not None:
            os.remove(self.__cache_file)
        self.__cache_file = data_file_path
        self.__last_update = now
        return True

    def __is_expired(self):
        return self.__last_update is None or self.__last_update + self.__update_period < datetime.datetime.now(
            tz=datetime.timezone.utc)

    def lookup(self, timestamp) -> crypto_record.CryptoRecord:
        # Update cache if necessary
        if timestamp > self.__last_update and self.__is_expired():
            update_res = self.__update_cache()
            if not update_res:
                return None
        df = pd.read_csv(self.__cache_file)
        result = df.loc[df['date'] == timestamp.strftime("%Y-%m-%d %H:%M:%S")]
        # A miss
        if len(result) == 0:
            logging.debug("Miss for {0}.".format(timestamp))
            return None
        record = crypto_record.CryptoRecord(
            datetime.datetime.strptime(result.iloc[0]['date'], '%Y-%m-%d %H:%M:%S'),
            result.iloc[0]['open'],
            result.iloc[0]['high'],
            result.iloc[0]['low'],
            result.iloc[0]['close'],
            self.crypto,
            self.currency)
        logging.debug('Hit for {0}: {1}'.format(timestamp, record))
        return record

    def get_records_between_dates(self, start_timestamp, end_timestamp):
        # Update cache if necessary
        if end_timestamp > self.__last_update and self.__is_expired():
            update_res = self.__update_cache()
            if not update_res:
                return None
        df = pd.read_csv(self.__cache_file)
        df['date'] = df['date'].apply(lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                                      .astimezone(datetime.timezone.utc))
        records = dict()
        for _, row in df.iterrows():
            if start_timestamp <= row['date'] <= end_timestamp:
                records.update({row['date']: crypto_record.CryptoRecord(row['date'],
                                                                        row['open'],
                                                                        row['high'],
                                                                        row['low'],
                                                                        row['close'],
                                                                        self.crypto,
                                                                        self.currency)})
        logging.debug('Found {0} records between {1} and {2}'.format(len(records), start_timestamp, end_timestamp))
        return records

    def get_latest_record(self):
        if self.__is_expired():
            update_res = self.__update_cache()
            if not update_res:
                return None
        df = pd.read_csv(self.__cache_file)
        df['date'] = df['date'].apply(lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                                      .astimezone(datetime.timezone.utc))
        record = df.iloc[np.argmax(df['date'])]
        return crypto_record.CryptoRecord(record['date'],
                                          record['open'],
                                          record['high'],
                                          record['low'],
                                          record['close'],
                                          self.crypto,
                                          self.currency)

    def get_n_records_until(self, end_timestamp, n_records):
        # Update cache if necessary
        if end_timestamp > self.__last_update and self.__is_expired():
            update_res = self.__update_cache()
            if not update_res:
                return None
        df = pd.read_csv(self.__cache_file)
        df['date'] = df['date'].apply(lambda dt: datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                                      .astimezone(datetime.timezone.utc))
        df.sort_values(by='unix', inplace=True, ascending=False)
        first_earlier_i = 0
        for _, row in df.iterrows():
            if row['date'] <= end_timestamp:
                break
            first_earlier_i += 1
        i = 0
        results = dict()
        while i < n_records:
            record = df.iloc[first_earlier_i + i]
            result = crypto_record.CryptoRecord(record['date'],
                                                record['open'],
                                                record['high'],
                                                record['low'],
                                                record['close'],
                                                self.crypto,
                                                self.currency)
            results.update({record['date']: result})
            i += 1
        return results

    def __del__(self):
        os.remove(self.__cache_file)


class CryptodatadownloadScraper(WebScraper):
    def __init__(self, cache_dir):
        self.__caches = dict()
        self.__caches_dir = cache_dir

    def get_record_by_date(self, timestamp, crypto, currency) -> crypto_record.CryptoRecord:
        """
        Returns a record for a given timestamp
        :param timestamp:
        :param crypto:
        :param currency:
        :return:
        """
        cache = self.__caches.get((crypto, currency))
        if cache is None:
            cache = CryptodatadownloadCache(self.__caches_dir, crypto, currency)
            self.__caches.update({(crypto, currency): cache})
        return cache.lookup(timestamp)

    def get_latest_record(self, crypto, currency) -> crypto_record.CryptoRecord:
        cache = self.__caches.get((crypto, currency))
        if cache is None:
            cache = CryptodatadownloadCache(self.__caches_dir, crypto, currency)
            self.__caches.update({(crypto, currency): cache})
        return cache.get_latest_record()

    def get_records_between_dates(self, start_timestamp, end_timestamp, crypto, currency) \
            -> [crypto_record.CryptoRecord]:
        """
        Returns sorted (descending order) records between given dates
        :param start_timestamp:
        :param end_timestamp:
        :param crypto:
        :param currency:
        :return:
        """
        cache = self.__caches.get((crypto, currency))
        if cache is None:
            cache = CryptodatadownloadCache(self.__caches_dir, crypto, currency)
            self.__caches.update({(crypto, currency): cache})
        return cache.get_records_between_dates(start_timestamp, end_timestamp)

    def get_n_records_until(self, end_timestamp, crypto, currency, n_records):
        """
        Returns sorted (descending order) records until a given date
        :param end_timestamp:
        :param crypto:
        :param currency:
        :param n_records:
        :return:
        """
        cache = self.__caches.get((crypto, currency))
        if cache is None:
            cache = CryptodatadownloadCache(self.__caches_dir, crypto, currency)
            self.__caches.update({(crypto, currency): cache})
        return cache.get_n_records_until(end_timestamp, n_records)
