# Crypto Deep
Tools for training and using recurrent neural networks for predicting cryptocurrencies prices.
## Table of contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
## General Information
- Project structure:<br/>
  - **logic/** - Provides data models and implements data scraping
  - **NN/** - Neural network training and inference
  - **scripts/** - Python scripts meant to be run directly by users
  - **web/** - Node.js API for accessing historical data and predictions
## Technologies Used
- Tensorflow
- Pandas
- Scikit-Learn
- Numpy
- PostgreSQL
- Node.js
- Express.js
- Web Scraping
## Features
- Downloading and saving historical cryptocurrency data in a database
- Inference of future cryptocurrencies prices based on historical data
- Web API for retrieving predicted and historical cryptocurrencies prices
## Setup
### PostgreSQL database
Create a database for storing the data. Put the database name with user's credentials in logic/scraper/db_config/database.ini.
Make sure the user has privileges to create tables in the database.
### Training the model
Open a terminal in the project's root and run the following command:<br/>
`python3 -m NN.train --crypto ETH --currency GBP`<br/>
The script will train a model for predicting Ethereum prices in Pound sterling. By default, the model uses last 50 
price records (hourly) and predicts the price 24 hours ahead of the last record. Take a look at create_model() in NN/train.py
for the network's architecture details.
### Web API
The application was developed with Node.js 16.17.0 and Express.js 4.0.0. Go to web/cryptodeep_api/ and run<br/>
`npm install` <br/>
To install the dependencies.
## Usage
### Training
Train your models by running `python3 -m NN.train --crypto <crypto_symbol> --currency <currency_symbol>`. Checkpoints and data 
scalers should be saved in respectively NN/logs and NN/ directories. 
### Continuous inference
Go to scripts/ and run `python3 -m predict.py --crypto <crypto_symbol> --currency <currency_symbol>`. The script will check
if new data is available in 1s intervals, save it in the database, and predict future prices.
### Example database structure
```
<db_name>
|
├── eth_gbp_records
├── eth_gbp_predictions
.
├── <crypto_symbol>_<currency_symbol>_records     // Historical data
├── <crypto_symbol>_<currency_symbol>_predictions // Predictions
```
### Web API
Go to web/cryptodeep_api and run <br/>
`npm start`<br/>
The web server will be launched on port 3000. API details:<br/>

| Endpoint                                                         | Return format | Description                                                                                                   |
|------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------------------------|
| crypto/<crypto_symbol>/<currency_symbol>/all                     | JSON          | All available historical data for given cryptocurrency                                                        |
| crypto/<crypto_symbol>/<currency_symbol>/<start_date>/<end_date> | JSON          | Historical data between start_date and end_date inclusive. Date format: yyyymmddHHMMSS. UTC timezone assumed. |
| crypto/<crypto_symbol>/<currency_symbol>/<n_records>             | JSON          | Last n_records records for given cryptocurrency                                                               |
| pred/<crypto_symbol>/<currency_symbol>/all                       | JSON          | All predictions available for given cryptocurrency                                                            |
| pred/<crypto_symbol>/<currency_symbol>/<start_date>/<end_date>   | JSON          | Predictions between start_date and end_date. Date format: yyyymmddHHMMSS. UTC timezone assumed.               |
| pred/<crypto_symbol>/<currency_symbol>/<n>                       | JSON          | Last n predictions for given cryptocurrency                                                                   |
