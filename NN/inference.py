import joblib
import os
import numpy as np
import logging
from tensorflow.python.keras.models import load_model

from train import load_data


def main(input_sequence: np.ndarray, scaler_path: str, ckpt_path):
    std_scaler = joblib.load(scaler_path)
    input_sequence = std_scaler.transform(input_sequence)
    model = load_model(ckpt_path)
    logging.info("Model loaded successfully from {0}".format(ckpt_path))
    model.summary()
    predictions = model.predict(np.asarray([input_sequence])) * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
    print(predictions)
    return predictions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    val_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_1h_val.csv')
    sequence = val_df[['open', 'high', 'low', 'close']].to_numpy()[-50:, :]
    main(sequence,
         os.path.dirname(__file__) + '/scaler.joblib',
         os.path.dirname(__file__) + '/logs/checkpoint-1h-50-back')
