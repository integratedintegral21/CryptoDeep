import datetime
import logging
import os.path

from web_scraper import CryptodatadownloadScraperDB


def main():
    logging.basicConfig(level=logging.DEBUG)
    scraper = CryptodatadownloadScraperDB('ETH', 'GBP', 'localhost', 'cryptodb', 'cryptodb', 'cryptodb',
                                          os.path.dirname(__file__) + '/cache')
    scraper.update_db()
    timestamp = datetime.datetime(2022, 8, 19, 7)
    print(scraper.get_record_by_date(timestamp))
    print(scraper.get_latest_record())
    first_timestamp = datetime.datetime(2022, 8, 1)
    print(scraper.get_records_between_dates(first_timestamp, timestamp))


if __name__ == "__main__":
    main()
