import datetime
import os.path

from logic.scraper.web_scraper import CryptodatadownloadScraper


def main():
    scraper = CryptodatadownloadScraper(os.path.dirname(__file__) + '/cache')
    # timestamp = datetime.datetime(2022, 8, 15, 0, 0, 0)
    # print(scraper.get_record_by_date(timestamp, 'ETH', 'GBP'))
    first_timestamp = datetime.datetime(2022, 8, 5, 0, 0, 0)
    last_timestamp = datetime.datetime(2022, 8, 15, 0, 0, 0)
    print(scraper.get_records_between_dates(first_timestamp, last_timestamp, 'BTC', 'GBP'))


if __name__ == "__main__":
    main()
