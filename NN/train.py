from tensorflow.python.keras.layers import LSTM, Dense
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import datetime
import os
import argparse
import logging

from logic.scraper.web_scraper import CryptodatadownloadScraperDB, config

SEQUENCE_LEN = 50
FORWARD_PREDICTION = 24


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--crypto', required=True, help='Cryptocurrency symbol.')
    parser.add_argument('--currency', required=True, help='Currency symbol.')
    return parser.parse_args()


def get_sequences(data: np.array, backward_records, forward_step):
    X = []
    y = []
    i = 0
    while i + forward_step + backward_records < data.shape[0]:
        X.append(data[i:(i + backward_records), :])
        y.append(data[i + backward_records + forward_step, -1])
        i += 1
    return np.asarray(X).astype(float), np.asarray(y).astype(float)


def create_model():
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LEN, 4)),
        LSTM(64),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae', 'msle'])
    return model


def load_data(crypto, currency, host, db, user, password, backward_records=SEQUENCE_LEN,
              forward_prediction=FORWARD_PREDICTION, validation_split=0.3):
    scraper = CryptodatadownloadScraperDB(crypto, currency, host, db, user,
                                          password, os.path.dirname(__file__) + '/cache')
    scraper.update_db()
    records = np.asarray(sorted(scraper.get_all_records().items()))[:, 1]
    records_arr = np.asarray([[r.open, r.high, r.low, r.close] for r in records]).astype(float)
    scaler = StandardScaler()
    normalized_records_arr = scaler.fit_transform(records_arr)
    train_records = normalized_records_arr[:(1 - int(validation_split * normalized_records_arr.shape[0]))]
    validation_records = normalized_records_arr[(1 - int(validation_split * normalized_records_arr.shape[0])):]

    X_train, y_train = get_sequences(train_records, backward_records, forward_prediction)
    X_val, y_val = get_sequences(validation_records, backward_records, forward_prediction)

    # Shuffle train data
    perm = np.random.permutation(X_train.shape[0])
    X_train = X_train[perm, :, :]
    y_train = y_train[perm]
    return X_train, y_train, X_val, y_val, scaler


def main(crypto, currency):
    logging.basicConfig(level=logging.INFO)

    db_params = config()
    X_train, y_train, X_val, y_val, scaler = load_data(crypto, currency, db_params['host'], db_params['database'],
                                                       db_params['user'], db_params['password'])
    joblib.dump(scaler, os.path.dirname(__file__) + '/' + crypto + currency + '_scaler.joblib')

    model = create_model()
    model.summary()
    log_dir = os.path.dirname(__file__) + "/logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    ckpt_path = os.path.dirname(__file__) + '/logs/checkpoint_' \
                + crypto + currency + '_1h_' + str(SEQUENCE_LEN) \
                + '_back_' + str(FORWARD_PREDICTION) + '_forward'
    model.fit(X_train, y_train, epochs=2000, shuffle=True, validation_data=(X_val, y_val),
              callbacks=[
                  TensorBoard(log_dir, histogram_freq=1),
                  EarlyStopping(patience=10),
                  ModelCheckpoint(ckpt_path),
              ])


if __name__ == '__main__':
    args = parse_args()
    main(args.crypto, args.currency)
