import time
import pandas as pd
import numpy as np
import ta
from binance.um_futures import UMFutures
from binance.error import ClientError
from keys import api, secret
import time
from datetime import datetime
import os

class BTCSignalLogger:
    def __init__(self, api_key, secret_key):
        self.client = UMFutures(key=api_key, secret=secret_key)
        self.symbol = 'BTCUSDT'
        self.log_file = 'btc.csv'
        
        # Track the last signal and timestamp
        self.last_signal = None
        self.last_signal_time = 0
        
        # Initialize CSV file if it doesn't exist
        self._initialize_log_file()

    def fetch_klines(self, interval='5m', limit=50):
        """
        Fetch historical kline (candlestick) data from Binance
        
        :param interval: Kline interval (e.g., '5m' for 5-minute intervals)
        :param limit: Number of data points to fetch
        :return: DataFrame with historical price data
        """
        try:
            # Fetch klines from Binance Futures
            klines = self.client.klines(
                symbol=self.symbol, 
                interval=interval, 
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close_time', 'Quote_asset_volume', 'Number_of_trades',
                'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore'
            ])
            
            # Convert numeric columns to float
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            return df
        
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return None
    
    def _initialize_log_file(self):
        """
        Create CSV file with headers if it doesn't exist
        """
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=[
                'Timestamp', 
                'Price', 
                'RSI', 
                'MACD', 
                'Stochastic_K', 
                'Trend', 
                'Signal'
            ])
            df.to_csv(self.log_file, index=False)
    
    def log_signal(self, analysis):
        """
        Log trading signal to CSV file
        """
        try:
            # Read existing CSV
            df = pd.read_csv(self.log_file)
            
            # Prepare new row as a DataFrame
            new_row = pd.DataFrame([{
                'Timestamp': analysis['Timestamp'],
                'Price': analysis['Price'].replace('$', ''),
                'RSI': analysis['RSI'],
                'MACD': analysis['MACD'],
                'Stochastic_K': analysis['Stoch_K'],
                'Trend': analysis['Trend'],
                'Signal': analysis['Signal']
            }])
            
            # Concatenate the new row to the existing DataFrame
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.log_file, index=False)
            
            print(f"Signal logged to {self.log_file}")
        
        except Exception as e:
            print(f"Error logging signal: {e}")

    
    def analyze_price(self, data):
        # More sensitive RSI with shorter window
        rsi = ta.momentum.RSIIndicator(close=data['Close'], window=7)
        data['RSI'] = rsi.rsi()

        # Shorter-term Bollinger Bands
        bbands = ta.volatility.BollingerBands(close=data['Close'], window=10, window_dev=1.5)
        data['BB_High'] = bbands.bollinger_hband()
        data['BB_Low'] = bbands.bollinger_lband()

        # Shorter-term Moving Averages
        ema_ultra_short = ta.trend.EMAIndicator(close=data['Close'], window=5)
        ema_short = ta.trend.EMAIndicator(close=data['Close'], window=9)

        data['EMA_Ultra_Short'] = ema_ultra_short.ema_indicator()
        data['EMA_Short'] = ema_short.ema_indicator()

        # MACD for additional momentum
        macd = ta.trend.MACD(close=data['Close'])
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()

        # Stochastic Oscillator for momentum
        stoch = ta.momentum.StochasticOscillator(
            high=data['High'], 
            low=data['Low'], 
            close=data['Close'], 
            window=10,
            smooth_window=3
        )
        data['Stoch_K'] = stoch.stoch()
        data['Stoch_D'] = stoch.stoch_signal()

        # Trend and signal identification
        latest = data.iloc[-1]

        buy_conditions = [
            latest['RSI'] < 30,
            latest['Close'] < latest['BB_Low'],
            latest['EMA_Ultra_Short'] > latest['EMA_Short'],
            latest['MACD'] > latest['MACD_Signal'],
            latest['Stoch_K'] < 20
        ]
        sell_conditions = [
            latest['RSI'] > 70,
            latest['Close'] > latest['BB_High'],
            latest['EMA_Ultra_Short'] < latest['EMA_Short'],
            latest['MACD'] < latest['MACD_Signal'],
            latest['Stoch_K'] > 80
        ]

        buy_count = sum(buy_conditions)
        sell_count = sum(sell_conditions)

        if buy_count == 5:
            signal = "🟢 STRONG BUY"
        elif sell_count == 5:
            signal = "🔴 STRONG SELL"
        elif buy_count >= 3:
            signal = "🔵 BUY"
        elif sell_count >= 3:
            signal = "🟠 SELL"
        else:
            signal = "🟡 HOLD"

        # Avoid repeated signals within 30 seconds
        current_time = time.time()
        if signal in ["🟢 STRONG BUY", "🔴 STRONG SELL", "🔵 BUY", "🟠 SELL"]:
            if self.last_signal == signal and (current_time - self.last_signal_time) <= 30:
                # Suppress signal if within 30 seconds
                signal = "🟡 HOLD"
            else:
                # Update last signal and time if it's a new signal or past the threshold
                self.last_signal = signal
                self.last_signal_time = current_time

        return {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Price': f"${latest['Close']:,.2f}",
            'RSI': f"{latest['RSI']:.2f}",
            'MACD': f"{latest['MACD']:.4f}",
            'Stoch_K': f"{latest['Stoch_K']:.2f}",
            'Trend': "Bullish" if latest['EMA_Ultra_Short'] > latest['EMA_Short'] else "Bearish",
            'Signal': signal
        }

    def run_continuous_analysis(self, interval=2):
        print("Starting short-term continuous analysis. Press Ctrl+C to stop.")
        print("=" * 60)
        print(f"Logging signals to: {self.log_file}")
        print("=" * 60)
        
        try:
            while True:
                # Fetch and analyze data (5-minute intervals)
                historical_data = self.fetch_klines(interval='5m')
                
                if historical_data is not None:
                    analysis = self.analyze_price(historical_data)

                    # Print analysis in a single line
                    print(f"{analysis['Timestamp']} | {analysis['Price']} | {analysis['RSI']} | {analysis['MACD']} | {analysis['Stoch_K']} | {analysis['Trend']} | {analysis['Signal']}")
                    print("=" * 60)

                    # Log signal to CSV
                    self.log_signal(analysis)
                
                # Wait before next check
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\nAnalysis stopped by user.")
        
        except Exception as e:
            print(f"\nError in continuous analysis: {e}")

def main():
    analyzer = BTCSignalLogger(api, secret)
    analyzer.run_continuous_analysis()

if __name__ == "__main__":
    main()
