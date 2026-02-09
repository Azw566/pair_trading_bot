# Trading Bot - Crypto Pairs Trading Pipeline

A cryptocurrency data pipeline for building a BTC/ETH pairs trading strategy. Fetches historical OHLCV data from Binance, processes and aligns time series, computes statistical indicators, and stores everything in a PostgreSQL database.

## Architecture

```
Binance API  →  fetch_binance_ohlcv.py  →  CSV Files  →  data_treatment.py  →  PostgreSQL
```

## Project Structure

```
Trading_Bot/
├── data/
│   ├── fetch_binance_ohlcv.py    # Fetches OHLCV data from Binance via CCXT
│   ├── data_treatment.py          # Cleans, aligns, and enriches data
│   └── Dockerfile                 # Containerized data fetching
├── src/                           # Trading strategy (WIP)
├── .env                           # Database credentials
├── BTC_USDT_1m.csv                # Raw BTC 1-min candles
└── ETH_USDT_1m.csv                # Raw ETH 1-min candles
```

## Data Pipeline

### 1. Fetching (`fetch_binance_ohlcv.py`)

Downloads 6 months of 1-minute OHLCV candles for BTC/USDT and ETH/USDT from Binance using CCXT. Outputs raw CSV files.

### 2. Processing (`data_treatment.py`)

- **Alignment**: Resamples both series to a common 1-minute grid
- **Gap filling**: Linear interpolation for gaps up to 3 consecutive minutes
- **Outlier removal**: Rolling mean/std with a 4-sigma threshold
- **Feature engineering**:
  - Log returns for BTC and ETH
  - Spread ratio (BTC/ETH price)
  - Z-score of spread (60-minute rolling window)

### Database Schema (`ohlcv_aligned`)

| Column | Description |
|--------|-------------|
| `timestamp` | Candle timestamp (index) |
| `btc_close` | Bitcoin closing price |
| `eth_close` | Ethereum closing price |
| `btc_log_ret` | Bitcoin log returns |
| `eth_log_ret` | Ethereum log returns |
| `spread` | BTC/ETH price ratio |
| `z_score` | Normalized spread |

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker (optional)

### Installation

```bash
pip install ccxt pandas numpy sqlalchemy python-dotenv
```

### Configuration

Create a `.env` file at the project root:

```env
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_data
```

### Usage

```bash
# 1. Fetch raw data from Binance
python data/fetch_binance_ohlcv.py

# 2. Process data and load into PostgreSQL
python data/data_treatment.py
```

Or with Docker:

```bash
docker build -t trading-data ./data
docker run trading-data
```

## Tech Stack

- **Python** - Core language
- **CCXT** - Exchange API wrapper
- **Pandas / NumPy** - Data processing
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Data storage
- **Docker** - Containerization
