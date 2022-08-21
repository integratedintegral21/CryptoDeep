import logging
import os.path
import asyncio
from configparser import ConfigParser

from web_scraper import CryptodatadownloadScraperDB


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


async def update_scraper(db_params):
    scraper = CryptodatadownloadScraperDB('ETH', 'GBP', db_params['host'], db_params['database'], db_params['user'],
                                          db_params['password'], os.path.dirname(__file__) + '/cache')
    scraper.update_db()
    await asyncio.sleep(3600)


async def main():
    logging.basicConfig(level=logging.INFO)
    db_params = config()
    while True:
        await update_scraper(db_params)


if __name__ == "__main__":
    asyncio.run(main())
