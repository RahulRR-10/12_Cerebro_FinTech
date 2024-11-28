import time
import pandas as pd
import numpy as np
import ta
import json
from binance.um_futures import UMFutures
from binance.error import ClientError
from keys import api, secret
import time
from datetime import datetime
import os
from web3 import Web3
from dotenv import load_dotenv

# Add the BlockchainTradeLogger class here (from previous code)
class BlockchainTradeLogger:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Connect to Sepolia testnet
        sepolia_rpc_url = os.getenv('SEPOLIA_RPC_URL', 'https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID')
        self.w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
        
        # Validate connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Sepolia testnet")

        # Load contract
        self.contract_address = Web3.to_checksum_address(os.getenv('CONTRACT_ADDRESS'))
        
        # Load contract ABI (you'll get this when you compile the Solidity contract)
        with open('TradeLogger_abi.json', 'r') as abi_file:
            contract_abi = json.load(abi_file)
        
        # Create contract instance
        self.contract = self.w3.eth.contract(
            address=self.contract_address, 
            abi=contract_abi
        )

        # Setup account
        private_key = os.getenv('PRIVATE_KEY')
        self.account = self.w3.eth.account.from_key(private_key)
        self.w3.eth.default_account = self.account.address

        # Track last trade for profit calculation
        self.last_trade = None

    # Include log_trade and close_trade methods from previous code
    # (Keep the entire BlockchainTradeLogger class as it was)

# Modify the BTCSignalLogger to include blockchain logging
class BTCSignalLogger:
    def __init__(self, api_key, secret_key):
        # Existing initialization
        self.client = UMFutures(key=api_key, secret=secret_key)
        self.symbol = 'BTCUSDT'
        self.log_file = 'btc.csv'
        
        # Track the last signal, timestamp, and entry price
        self.last_order_type = None  # 'BUY' or 'SELL'
        self.last_entry_price = None
        self.last_signal_time = 0
        
        # Initialize blockchain logger
        self.blockchain_logger = BlockchainTradeLogger()
        
        # Initialize CSV file if it doesn't exist
        self._initialize_log_file()

    # Modify the analyze_price method to include blockchain logging
    def analyze_price(self, data):
        # Existing analysis logic
        analysis = super().analyze_price(data)

        # Extract current price
        current_price = float(analysis['Price'].replace('$', ''))

        # Blockchain trade logging logic
        if analysis['Signal'].startswith('🟢') or analysis['Signal'].startswith('🔵'):
            # LONG trade
            if self.last_order_type != 'BUY':
                self.blockchain_logger.log_trade(
                    self.symbol, 
                    'LONG', 
                    current_price
                )
                self.last_order_type = 'BUY'
        elif analysis['Signal'].startswith('🔴') or analysis['Signal'].startswith('🟠'):
            # SHORT trade
            if self.last_order_type != 'SELL':
                self.blockchain_logger.log_trade(
                    self.symbol, 
                    'SHORT', 
                    current_price
                )
                self.last_order_type = 'SELL'
        
        # Close previous trade before opening a new one
        if self.last_order_type is not None:
            self.blockchain_logger.close_trade(current_price)

        return analysis

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
        current_price = latest['Close']

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

        potential_signal = None
        if buy_count == 5:
            potential_signal = "🟢 STRONG BUY"
        elif sell_count == 5:
            potential_signal = "🔴 STRONG SELL"
        elif buy_count >= 3:
            potential_signal = "🔵 BUY"
        elif sell_count >= 3:
            potential_signal = "🟠 SELL"
        else:
            potential_signal = "🟡 HOLD"

        # Ensure opposite order and price condition
        if self.last_order_type == "BUY" and "SELL" in potential_signal:
            # Check price condition for selling
            if current_price >= self.last_entry_price * 0.99:
                self.last_order_type = "SELL"
                self.last_entry_price = current_price
            else:
                potential_signal = "🟡 HOLD"  # Suppress signal
        elif self.last_order_type == "SELL" and "BUY" in potential_signal:
            # Check price condition for buying
            if current_price <= self.last_entry_price * 1.01:
                self.last_order_type = "BUY"
                self.last_entry_price = current_price
            else:
                potential_signal = "🟡 HOLD"  # Suppress signal
        elif self.last_order_type is None:
            # Allow the first order of either type
            self.last_order_type = "BUY" if "BUY" in potential_signal else "SELL"
            self.last_entry_price = current_price

        # Avoid repeated signals within 30 seconds
        current_time = time.time()
        if potential_signal not in ["🟡 HOLD"] and (current_time - self.last_signal_time) > 30:
            self.last_signal_time = current_time
        else:
            potential_signal = "🟡 HOLD"

        return {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Price': f"${latest['Close']:,.2f}",
            'RSI': f"{latest['RSI']:.2f}",
            'MACD': f"{latest['MACD']:.4f}",
            'Stoch_K': f"{latest['Stoch_K']:.2f}",
            'Trend': "Bullish" if latest['EMA_Ultra_Short'] > latest['EMA_Short'] else "Bearish",
            'Signal': potential_signal
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
