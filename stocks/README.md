# Stock Trading Simulator

A modern, web-based stock trading simulation application with live stock data. Built with Flask (backend) and vanilla HTML/CSS/JavaScript (frontend).

## Features

- **Live Stock Data**: Fetches real-time stock prices using yfinance
- **Interactive Charts**: Dynamic charts with multiple timeframes (1m, 5m, 10m, 30m)
- **Portfolio Management**: Track cash, holdings, and portfolio value in real-time
- **Trading Operations**: Buy and sell stocks with validation
- **Trade History**: Complete record of all transactions
- **Modern Web UI**: Responsive design with dark theme
- **Auto-refresh**: Automatic updates every 3 seconds

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask server:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

### Web Interface

1. **Search for a Stock**: Enter a stock symbol (e.g., AAPL, TSLA, MSFT) and click "Search"
2. **View Charts**: Select different timeframes (1m, 5m, 10m, 30m) to view price history
3. **Buy Stocks**: Enter quantity and click "BUY"
4. **Sell Stocks**: Enter quantity and click "SELL"
5. **Monitor Portfolio**: View your cash, holdings, and total portfolio value in the sidebar
6. **View History**: Check your trade history at the bottom

### API Endpoints

The Flask server provides the following REST API endpoints:

- `GET /api/portfolio` - Get portfolio summary
- `POST /api/stock/search` - Search for stock information
- `POST /api/stock/chart` - Get chart data for a stock
- `POST /api/trade/buy` - Execute a buy order
- `POST /api/trade/sell` - Execute a sell order
- `GET /api/history` - Get trade history

## Starting Cash

The simulator starts with $10,000 in cash by default. This can be modified in `app.py`.

## Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js
- **Data**: yfinance (Yahoo Finance API)

## Project Structure

```
stocks/
├── app.py                 # Flask server
├── portfolio.py           # Portfolio management class
├── stock_data.py          # Stock data fetching
├── trading_simulator.py   # Trading operations
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── app.js        # Frontend JavaScript
```

## Features

- **Live Stock Charts**: Interactive charts showing price history with multiple timeframes
- **Real-time Pricing**: Stock prices fetched live from Yahoo Finance
- **Portfolio Tracking**: Monitor cash, holdings value, and total portfolio value
- **Easy Trading**: One-click buy/sell interface with validation
- **Trade History**: Complete record of all transactions with timestamps
- **Modern UI**: Dark theme interface inspired by professional trading platforms
- **Responsive Design**: Works on desktop and tablet devices

## Notes

- Stock prices are fetched in real-time from Yahoo Finance via yfinance
- All trades are simulated - no real money is involved
- Prices may have slight delays depending on market hours
- Charts display price data based on selected timeframe
- The application uses browser sessions to maintain portfolio state

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

## License

This project is for educational purposes only.
