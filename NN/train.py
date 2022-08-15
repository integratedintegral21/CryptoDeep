from tensorflow.python.keras.layers import LSTM, Dense
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import datetime
import os


SEQUENCE_LEN = 50


def load_data(path: str):
    df = pd.read_csv(path)
    df = df[['unix', 'date', 'open', 'high', 'low', 'close']]
    df.sort_values(by='unix', inplace=True)
    return df


def get_normalized_sequences(df, sequence_len, step=1, scaler=None):
    data = df.to_numpy()
    numerical_features = data[:, 2:]
    if scaler is None:
        scaler = StandardScaler()
        data[:, 2:] = scaler.fit_transform(numerical_features)
    else:
        data[:, 2:] = scaler.transform(numerical_features)
    sequences = []
    i = 0
    while i + sequence_len + 1 <= data.shape[0]:
        sequences.append(data[i:(i + sequence_len + 1), :])
        i += step
    sequences = np.asarray(sequences)
    X = sequences[:, :-1, :]
    y = sequences[:, -1, -1]
    return X, y, scaler


def create_model():
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LEN, 4)),
        LSTM(64),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae', 'msle'])
    return model


def main():
    train_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_1h.csv')
    X_train, y_train, scaler = get_normalized_sequences(train_df, SEQUENCE_LEN)
    # Save scaler
    joblib.dump(scaler, os.path.dirname(__file__) + '/scaler.joblib')
    # Drop timestamps
    X_train = X_train[:, :, 2:].astype(float)
    y_train = y_train.astype(float)

    val_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_1h_val.csv')
    X_val, y_val, _ = get_normalized_sequences(val_df, SEQUENCE_LEN, 1, scaler)
    X_val = X_val[:, :, 2:].astype(float)
    y_val = y_val.astype(float)

    model = create_model()
    model.summary()
    log_dir = os.path.dirname(__file__) + "/logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    model.fit(X_train, y_train, epochs=2000, shuffle=True, validation_data=(X_val, y_val),
              callbacks=[
                  TensorBoard(log_dir, histogram_freq=1),
                  EarlyStopping(patience=10),
                  ModelCheckpoint(os.path.dirname(__file__) + '/logs/checkpoint'
                                  + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")),
              ])


if __name__ == '__main__':
    main()
