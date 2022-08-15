import os.path
from train import load_data, get_normalized_sequences, create_model
import matplotlib.pyplot as plt
import numpy as np
import joblib


def main():
    std_scaler = joblib.load(os.path.dirname(__file__) + '/scaler.joblib')
    val_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_d_val.csv')
    X_val, y_val, _ = get_normalized_sequences(val_df, 10, 1, std_scaler)
    timestamps = X_val[:, :, 1]
    X_val = X_val[:, :, 2:].astype(float)
    y_val = y_val.astype(float)

    model = create_model()
    model.load_weights(os.path.dirname(__file__) + '/logs/checkpoint-1d-10-back')
    model.evaluate(X_val, y_val)

    y_pred = model.predict(X_val)[:, 0]
    for t_stp, x, y_t, y_p in zip(timestamps, X_val, y_val, y_pred):
        # Inverse scaling
        x = x * np.sqrt(std_scaler.var_) + std_scaler.mean_
        y_t = y_t * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
        y_p = y_p * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
        openings = x[:, 0]
        closings = x[:, -1]
        plt.plot(t_stp, closings)
        plt.scatter(t_stp[-1:], [y_t])
        plt.scatter(t_stp[-1:], [y_p], c='red')
        plt.show()


if __name__ == "__main__":
    main()
