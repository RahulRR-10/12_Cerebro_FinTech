from datetime import datetime
import pandas as pd
from binance.spot import Spot

client = Spot()

def fetch_historical_klines(symbol, interval, start_time, end_time):
    data = []
    while True:
        # Fetch klines
        klines = client.klines(symbol, interval, startTime=start_time, endTime=end_time, limit=1000)
        if not klines:
            break
        data.extend(klines)
        start_time = klines[-1][0] + 1  # Increment start time
        if len(klines) < 1000:
            break

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 
                                     'Trades', 'BaseAssetVolume', 'QuoteVolume'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df.set_index('Time', inplace=True)
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

# Example Usage
start_time = int(datetime(2013, 1, 1).timestamp() * 1000)
end_time = int(datetime.now().timestamp() * 1000)
btc_data = fetch_historical_klines('BTCUSDT', '1d', start_time, end_time)
btc_data.to_csv('btc_usdt_historical.csv')
