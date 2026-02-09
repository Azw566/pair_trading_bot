import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

def load_and_clean(filepath, symbol):
    df = pd.read_csv(filepath)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    df = df[['close']].rename(columns={'close': f'{symbol.lower()}_close'})

    df = df.resample('1min').asfreq() # Re-échantillonnage à 1 minute pour aligner les timestamps

    df = df.interpolate(method='linear', limit=3) # Interpolation linéaire pour les petits trous (ex: max 3 minutes consécutives)
    
    return df

btc = load_and_clean('BTC_USDT_1m.csv', 'BTC') # Modifier les path si besoin
eth = load_and_clean('ETH_USDT_1m.csv', 'ETH')

df_pair = btc.join(eth, how='inner')
df_pair.dropna(inplace=True)

def remove_outliers(series, window=20, n_sigmas=4): # Contrôle du nombre de sigmas
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    
    # On remplace par la moyenne mobile si le prix dévie de plus de X sigmas
    outliers = (np.abs(series - rolling_mean) > (n_sigmas * rolling_std))
    series[outliers] = rolling_mean[outliers]
    return series

df_pair['btc_close'] = remove_outliers(df_pair['btc_close'])
df_pair['eth_close'] = remove_outliers(df_pair['eth_close'])

df_pair['btc_log_ret'] = np.log(df_pair['btc_close'] / df_pair['btc_close'].shift(1))
df_pair['eth_log_ret'] = np.log(df_pair['eth_close'] / df_pair['eth_close'].shift(1))

df_pair['spread'] = df_pair['btc_close'] / df_pair['eth_close']
window_z = 60
spread_mean = df_pair['spread'].rolling(window=window_z).mean()
spread_std = df_pair['spread'].rolling(window=window_z).std()
df_pair['z_score'] = (df_pair['spread'] - spread_mean) / spread_std

df_pair.dropna(inplace=True)

connection_string = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

engine = create_engine(connection_string, client_encoding='utf8') 

df_pair.to_sql('ohlcv_aligned', engine, if_exists='replace', index=True, method='multi')
print("Données envoyées en toute sécurité vers PostgreSQL.")
