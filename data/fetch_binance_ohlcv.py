import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
exchange = ccxt.binance() 
symbols = ['BTC/USDT', 'ETH/USDT'] # You can add more symbols as needed
timeframe = '1m'  # You can change this to '1d', '15m', etc.
six_months_ago = datetime.now() - timedelta(days=180)
since = int(six_months_ago.timestamp() * 1000)

def fetch_all_ohlcv(symbol, timeframe, since):
    all_ohlcv = []
    current_since = since
    
    print(f"Fetching data for {symbol}...")
    
    while current_since < exchange.milliseconds():
        try:
            # Fetch data (Binance limit is usually 1000 candles)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=1000)
            if not ohlcv:
                break
            
            # Update current_since to the timestamp of the last candle + 1ms
            current_since = ohlcv[-1][0] + 1
            all_ohlcv.extend(ohlcv)
            
            # Respect rate limits
            time.sleep(exchange.rateLimit / 1000)
            
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return all_ohlcv

# --- EXECUTION ---
for symbol in symbols:
    data = fetch_all_ohlcv(symbol, timeframe, since)
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert timestamp to readable date
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Save to CSV
    filename = f"{symbol.replace('/', '_')}_1m.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")