import joblib
import os
import numpy as np
import logging
from tensorflow.python.keras.models import load_model


def infer(input_sequences: np.ndarray, scaler_path: str, ckpt_path):
    std_scaler = joblib.load(scaler_path)
    input_sequences = np.asarray([std_scaler.transform(s) for s in input_sequences])
    model = load_model(ckpt_path)
    logging.info("Model loaded successfully from {0}".format(ckpt_path))
    model.summary()
    predictions = model.predict(input_sequences) * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
    logging.info("Predictions: {0}".format(predictions))
    return predictions

