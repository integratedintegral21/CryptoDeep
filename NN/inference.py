import joblib
import os
import numpy as np
import logging
from tensorflow.python.keras.models import load_model

from train import load_data


def main(input_sequences: np.ndarray, scaler_path: str, ckpt_path):
    std_scaler = joblib.load(scaler_path)
    input_sequences = np.asarray([std_scaler.transform(s) for s in input_sequences])
    model = load_model(ckpt_path)
    logging.info("Model loaded successfully from {0}".format(ckpt_path))
    model.summary()
    predictions = model.predict(input_sequences) * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
    print(predictions)
    return predictions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    val_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_1h_val.csv')
    sequence0 = val_df[['open', 'high', 'low', 'close']].to_numpy()[-50:, :]
    sequence1 = val_df[['open', 'high', 'low', 'close']].to_numpy()[-75:-25, :]
    sequence2 = val_df[['open', 'high', 'low', 'close']].to_numpy()[-150:-100, :]
    main([sequence0,
          sequence1,
          sequence2],
         os.path.dirname(__file__) + '/scaler.joblib',
         os.path.dirname(__file__) + '/logs/checkpoint-1h-50-back')
