import logging
import os.path
import asyncio

from web_scraper import CryptodatadownloadScraperDB, config


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
