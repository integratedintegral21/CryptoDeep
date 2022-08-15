import datetime
import os
import glob

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


class CoinmarketcapScraper(WebScraper):
    def __init__(self, driver_path):
        self.driver_ = webdriver.Chrome(driver_path)

    def get_record_by_date(self, timestamp, crypto, currency):
        self.driver_.get('https://coinmarketcap.com')

    def get_records_between_dates(self, start_timestamp, end_timestamp, crypto, currency):
        self.driver_.get('https://coinmarketcap.com')


class CryptodatadownloadScraper(WebScraper):
    def __try_create_cache(self):
        if not os.path.isdir(self.cache_path):
            os.mkdir(self.cache_path)

    def __get_latest_cache_file(self, crypto, currency) -> str:
        latest_file = None
        # Get the latest file
        latest_timestamp = datetime.datetime(1900, 1, 1, 0, 0, 0)
        for filepath in glob.glob(os.path.join(self.cache_path, 'data_' + crypto + currency + '*.csv')):
            timestamp_str = filepath.split('_')[-1].split('.')[0]
            data_timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S')
            if data_timestamp > latest_timestamp:
                latest_timestamp = data_timestamp
                latest_file = filepath
        return latest_file

    def __lookup_cache(self, timestamp, crypto, currency) -> crypto_record.CryptoRecord:
        latest_file = self.__get_latest_cache_file(crypto, currency)
        # No files found, return a miss
        if latest_file is None:
            return None

        # Retrieve the record by timestamp
        df = pd.read_csv(latest_file)
        record = df.loc[df['date'] == timestamp.strftime("%Y-%m-%d %H:%M:%S")]
        # A miss
        if len(record) == 0:
            return None
        result = crypto_record.CryptoRecord(datetime.datetime.strptime(record.iloc[0]['date'], '%Y-%m-%d %H:%M:%S'),
                                            record.iloc[0]['open'],
                                            record.iloc[0]['high'],
                                            record.iloc[0]['low'],
                                            record.iloc[0]['close'],
                                            crypto,
                                            currency)
        return result

    def __update_cache(self, crypto, currency):
        download_link = 'https://www.cryptodatadownload.com/cdd/Binance_{0}{1}_d.csv'.format(crypto, currency)
        # Get the current latest file
        latest_file = self.__get_latest_cache_file(crypto, currency)
        print(download_link)
        http = urllib3.PoolManager()
        r = http.request('GET', download_link, preload_content=False)
        if r.status != 200:
            return None
        chunk_size = 512
        download_file_path = os.path.join(self.cache_path, 'download_'
                                          + crypto
                                          + currency
                                          + '_'
                                          + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                                          + '.csv')
        data_file_path = os.path.join(self.cache_path, 'data_'
                                      + crypto
                                      + currency
                                      + '_'
                                      + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
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
        # Remove the previous latest file
        if latest_file is not None:
            os.remove(latest_file)

    def __init__(self, cache_dir):
        self.cache_path = cache_dir
        self.__try_create_cache()

    def get_record_by_date(self, timestamp, crypto, currency) -> crypto_record.CryptoRecord:
        result = self.__lookup_cache(timestamp, crypto, currency)
        if result is not None:
            return result
        self.__update_cache(crypto, currency)
        return self.__lookup_cache(timestamp, crypto, currency)

    def get_records_between_dates(self, start_timestamp, end_timestamp, crypto, currency) \
            -> [crypto_record.CryptoRecord]:
        results = dict()
        while start_timestamp <= end_timestamp:
            results.update({start_timestamp: self.get_record_by_date(start_timestamp, crypto, currency)})
            start_timestamp += datetime.timedelta(days=1)
        return results

