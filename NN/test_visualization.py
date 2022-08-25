import os.path
from train import load_data, get_normalized_sequences, create_model
import matplotlib.pyplot as plt
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_log_error
from tensorflow.python.keras.models import load_model


def main():
    std_scaler = joblib.load(os.path.dirname(__file__) + '/ETHGBP_scaler.joblib')
    val_df = load_data(os.path.dirname(__file__) + '/data/Binance_ETHGBP_d_val.csv')
    X_val, y_val, _ = get_normalized_sequences(val_df, 50, 1, std_scaler)
    timestamps = X_val[:, :, 1]
    X_val = X_val[:, :, 2:].astype(float)
    y_val = y_val.astype(float)

    model = load_model(os.path.dirname(__file__) + '/logs/checkpoint-1d-30-back')
    model.evaluate(X_val, y_val)

    y_pred = model.predict(X_val)[:, 0]
    unscaled_inference = []
    for t_stp, x, y_t, y_p in zip(timestamps, X_val, y_val, y_pred):
        # Inverse scaling
        x = x * np.sqrt(std_scaler.var_) + std_scaler.mean_
        y_t = y_t * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
        y_p = y_p * np.sqrt(std_scaler.var_[-1]) + std_scaler.mean_[-1]
        unscaled_inference.append([y_t, y_p])
        openings = x[:, 0]
        closings = x[:, -1]
        plt.plot(t_stp, closings)
        plt.scatter(t_stp[-1:], [y_t])
        plt.scatter(t_stp[-1:], [y_p], c='red')
        plt.show()
    unscaled_inference = np.asarray(unscaled_inference)
    print("Mean absolute prediction error (unscaled predictions):", mean_absolute_error(unscaled_inference[:, 0],
                                                                                        unscaled_inference[:, 1]))
    print("Mean squared logarithmic prediction error (unscaled predictions):",
          mean_squared_log_error(unscaled_inference[:, 0],
                                 unscaled_inference[:, 1]))


if __name__ == "__main__":
    main()
