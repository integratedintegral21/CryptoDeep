import logging
import os.path
import asyncio

from web_scraper import CryptodatadownloadScraperDB


async def update_scraper():
    scraper = CryptodatadownloadScraperDB('ETH', 'GBP', 'localhost', 'cryptodb', 'cryptodb', 'cryptodb',
                                          os.path.dirname(__file__) + '/cache')
    scraper.update_db()
    await asyncio.sleep(3600)


async def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        await update_scraper()


if __name__ == "__main__":
    asyncio.run(main())
