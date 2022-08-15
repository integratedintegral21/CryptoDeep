class CryptoRecord:
    def __init__(self, timestamp, opening, high, low, closing, crypto, currency):
        self.timestamp = timestamp
        self.open = opening
        self.high = high
        self.low = low
        self.close = closing
        self.crypto = crypto
        self.currency = currency

    def __str__(self):
        return "Timestamp: {0}, Open: {1}, High: {2}, Low: {3}, Close: {4}, Symbol {5}".format(
            self.timestamp,
            self.open,
            self.high,
            self.low,
            self.close,
            self.crypto + '/' + self.currency
        )
