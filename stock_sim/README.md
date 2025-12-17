# Stock Trading Simulator

A professional stock trading simulator with interactive charts, real-time data updates, historical data viewing, and comprehensive trading functionality. Perfect for backtesting trading strategies!

## Features

- 📈 **Interactive Stock Charts** - Multiple time frames (1D, 1W, 1M, 3M, 6M, 1Y)
- 🔴 **Real-Time Updates** - Live price updates via WebSocket (updates every 5 seconds)
- 📅 **Historical Data Viewing** - View any past date to test strategies
- 💼 **Portfolio Management** - Buy/sell stocks with portfolio tracking
- 🎯 **Backtesting Ready** - Test your logic on historical data
- 🔄 **Multiple API Support** - Polygon.io (primary) and Alpha Vantage (fallback)
- 📊 **Comprehensive Data** - OHLCV data with high/low indicators

## Getting Started

### Installation

1. Install dependencies:
```bash
npm install
```

2. **Configure API Keys** (Recommended for real data):

   Create a `.env` file in the root directory:
   ```env
   # Primary API (Polygon.io - Best for real-time data)
   POLYGON_API_KEY=your_polygon_api_key_here
   
   # Fallback API (Alpha Vantage)
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   
   # API Provider: 'polygon', 'alphavantage', or 'mock'
   API_PROVIDER=polygon
   ```

   **Get Free API Keys:**
   - **Polygon.io** (Recommended): https://polygon.io/ 
     - Free tier: 5 API calls/minute
     - Excellent real-time data
     - Best for live updates
   - **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
     - Free tier: 5 API calls/minute, 500 calls/day
     - Good historical data coverage

   **Note:** If no API keys are configured, the app will use mock data for testing.

3. Start the server:
```bash
npm start
```

4. Open your browser and navigate to:
```
http://localhost:3000
```

## Usage

1. **Select a Stock**: Choose a stock symbol from the dropdown in the chart section
2. **Choose Time Frame**: Click on 1D, 1W, 1M, 3M, 6M, or 1Y to view different time periods
3. **View Historical Data**: 
   - Select a date in the date picker
   - Click "View" to see data up to that date
   - Click "Live" to return to current data
4. **Trade Stocks**:
   - Select a symbol in the trading section
   - Choose Buy or Sell
   - Enter quantity
   - Execute the trade

## Usage

1. **Select a Stock**: Choose a stock symbol from the dropdown in the chart section
2. **Choose Time Frame**: Click on 1D, 1W, 1M, 3M, 6M, or 1Y to view different time periods
3. **View Historical Data**: 
   - Select a date in the date picker
   - Click "View" to see data up to that date (perfect for backtesting!)
   - Click "Live" to return to real-time data
4. **Real-Time Updates**: Prices update automatically every 5 seconds when viewing live data
5. **Trade Stocks**:
   - Select a symbol in the trading section
   - Choose Buy or Sell
   - Enter quantity
   - Execute the trade

## Technology Stack

- **Backend**: Node.js with Express
- **Real-Time**: Socket.IO for WebSocket connections
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js with date adapter
- **APIs**: 
  - Polygon.io (primary) - Best for real-time data
  - Alpha Vantage (fallback) - Good historical coverage
  - Mock data generator (fallback when no API keys)

## API Configuration Details

### Polygon.io (Recommended)
- **Why**: Best real-time data with low latency
- **Free Tier**: 5 requests/minute
- **Features**: Real-time quotes, historical aggregates, tick-level data
- **Best For**: Live trading simulation and real-time updates

### Alpha Vantage
- **Why**: Extensive historical data, reliable service
- **Free Tier**: 5 requests/minute, 500 requests/day
- **Features**: Daily/intraday time series, global quotes
- **Best For**: Historical backtesting and analysis

### Mock Data
- **When**: No API keys configured or API limits exceeded
- **Features**: Realistic random walk data
- **Best For**: Development and testing without API keys

## Project Structure

```
stock_sim/
├── server.js              # Main Express server with WebSocket
├── config/
│   └── apiConfig.js       # API configuration
├── services/
│   ├── polygonService.js  # Polygon.io API integration
│   ├── alphaVantageService.js # Alpha Vantage API integration
│   └── stockDataService.js # Unified data service with fallbacks
├── public/
│   ├── index.html         # Main HTML
│   ├── styles.css         # Styling
│   └── app.js             # Frontend logic with Socket.IO
└── package.json
```

## Future Enhancements

- ✅ Real stock data API integration (DONE!)
- ✅ Real-time price updates (DONE!)
- 🔄 Add more technical indicators (RSI, MACD, Moving Averages)
- 🔄 Implement advanced backtesting framework
- 🔄 Add order history and trade analytics
- 🔄 Portfolio performance metrics and charts
- 🔄 Multiple chart types (candlestick, volume bars)
- 🔄 Alert system for price targets

