// Load environment variables first
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const path = require('path');
const http = require('http');
const { Server } = require('socket.io');

// Try to load services with error handling
let stockDataService;
try {
  stockDataService = require('./services/stockDataService');
} catch (error) {
  console.error('Error loading stockDataService:', error.message);
  console.error('Stack:', error.stack);
  process.exit(1);
}

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// In-memory storage for trades and portfolio
let portfolio = {
  cash: 10000,
  holdings: {},
  trades: []
};

// Real-time price updates
const subscribedSymbols = new Set();
const priceUpdateIntervals = new Map();

// Get stock data for a symbol and time frame
app.get('/api/stock/:symbol', async (req, res) => {
  const { symbol } = req.params;
  const timeframe = req.query.timeframe || '1D';
  const days = parseInt(req.query.days) || 365;

  try {
    const data = await stockDataService.getStockData(symbol.toUpperCase(), timeframe, days);
    
    res.json({
      symbol: symbol.toUpperCase(),
      timeframe,
      data
    });
  } catch (error) {
    console.error('Error fetching stock data:', error);
    res.status(500).json({ error: 'Failed to fetch stock data: ' + error.message });
  }
});

// Get historical data for a specific date range
app.get('/api/stock/:symbol/history', async (req, res) => {
  const { symbol } = req.params;
  const startDate = req.query.startDate;
  const endDate = req.query.endDate;

  try {
    if (!startDate || !endDate) {
      return res.status(400).json({ error: 'startDate and endDate are required' });
    }

    const data = await stockDataService.getHistoricalData(symbol.toUpperCase(), startDate, endDate);

    res.json({
      symbol: symbol.toUpperCase(),
      data
    });
  } catch (error) {
    console.error('Error fetching historical data:', error);
    res.status(500).json({ error: 'Failed to fetch historical data: ' + error.message });
  }
});

// Get current price for a symbol
app.get('/api/stock/:symbol/price', async (req, res) => {
  const { symbol } = req.params;

  try {
    const price = await stockDataService.getCurrentPrice(symbol.toUpperCase());
    if (price === null) {
      return res.status(404).json({ error: 'Price not available' });
    }
    res.json({ symbol: symbol.toUpperCase(), price });
  } catch (error) {
    console.error('Error fetching current price:', error);
    res.status(500).json({ error: 'Failed to fetch current price: ' + error.message });
  }
});

// Get current portfolio
app.get('/api/portfolio', (req, res) => {
  res.json(portfolio);
});

// Execute a trade
app.post('/api/trade', (req, res) => {
  const { symbol, action, quantity, price } = req.body;

  if (!symbol || !action || !quantity || !price) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const totalCost = quantity * price;

  if (action === 'buy') {
    if (portfolio.cash < totalCost) {
      return res.status(400).json({ error: 'Insufficient funds' });
    }

    portfolio.cash -= totalCost;
    portfolio.holdings[symbol] = (portfolio.holdings[symbol] || 0) + quantity;
  } else if (action === 'sell') {
    if (!portfolio.holdings[symbol] || portfolio.holdings[symbol] < quantity) {
      return res.status(400).json({ error: 'Insufficient shares' });
    }

    portfolio.cash += totalCost;
    portfolio.holdings[symbol] -= quantity;
    if (portfolio.holdings[symbol] === 0) {
      delete portfolio.holdings[symbol];
    }
  } else {
    return res.status(400).json({ error: 'Invalid action' });
  }

  portfolio.trades.push({
    symbol,
    action,
    quantity,
    price,
    totalCost,
    timestamp: new Date().toISOString()
  });

  res.json(portfolio);
});

// Search for stocks
app.get('/api/search', async (req, res) => {
  const query = req.query.q;
  
  if (!query || query.trim().length === 0) {
    return res.status(400).json({ error: 'Search query is required' });
  }

  try {
    const results = await stockDataService.searchStocks(query.trim());
    res.json(results);
  } catch (error) {
    console.error('Error searching stocks:', error);
    res.status(500).json({ error: 'Failed to search stocks: ' + error.message });
  }
});

// Get available symbols (default popular stocks)
app.get('/api/symbols', (req, res) => {
  res.json([
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'META', name: 'Meta Platforms Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' }
  ]);
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Subscribe to symbol updates
  socket.on('subscribe', async (symbol) => {
    if (!symbol) return;
    
    const upperSymbol = symbol.toUpperCase();
    subscribedSymbols.add(upperSymbol);
    
    // Start price updates if not already running
    if (!priceUpdateIntervals.has(upperSymbol)) {
      startPriceUpdates(upperSymbol);
    }
    
    socket.join(upperSymbol);
    console.log(`Client ${socket.id} subscribed to ${upperSymbol}`);
  });

  // Unsubscribe from symbol updates
  socket.on('unsubscribe', (symbol) => {
    if (!symbol) return;
    
    const upperSymbol = symbol.toUpperCase();
    socket.leave(upperSymbol);
    console.log(`Client ${socket.id} unsubscribed from ${upperSymbol}`);
    
    // Check if anyone else is subscribed to this symbol
    const room = io.sockets.adapter.rooms.get(upperSymbol);
    if (!room || room.size === 0) {
      stopPriceUpdates(upperSymbol);
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Start real-time price updates for a symbol
function startPriceUpdates(symbol) {
  // Don't start if already running
  if (priceUpdateIntervals.has(symbol)) {
    return;
  }
  
  const interval = setInterval(async () => {
    try {
      const price = await stockDataService.getCurrentPrice(symbol);
      if (price !== null && price > 0) {
        io.to(symbol).emit('priceUpdate', {
          symbol,
          price,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error(`Error updating price for ${symbol}:`, error.message);
    }
  }, 5000); // Update every 5 seconds

  priceUpdateIntervals.set(symbol, interval);
  console.log(`Started price updates for ${symbol}`);
}

// Stop price updates when no one is subscribed
function stopPriceUpdates(symbol) {
  const interval = priceUpdateIntervals.get(symbol);
  if (interval) {
    clearInterval(interval);
    priceUpdateIntervals.delete(symbol);
  }
}

server.listen(PORT, () => {
  console.log(`Stock Simulator server running on http://localhost:${PORT}`);
  console.log('WebSocket server ready for real-time updates');
  console.log('\n📊 API Status:');
  
  // Check which APIs are configured
  const finnhubService = require('./services/finnhubService');
  
  if (finnhubService.isConfigured()) {
    console.log('   ✅ Finnhub API: Configured');
  } else {
    console.log('   ⚠️  Finnhub API: Not configured (using mock data)');
    console.log('   💡 Get free API key: https://finnhub.io/register');
    console.log('   💡 Add FINNHUB_API_KEY to .env file for real stock data');
  }
  
  console.log('   📖 See README_API.md for setup instructions');
}).on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`\n❌ Error: Port ${PORT} is already in use!`);
    console.error('   Please stop the other process or change the PORT in server.js');
    console.error(`   To find what's using port ${PORT}, run: netstat -ano | findstr :${PORT}`);
  } else {
    console.error('\n❌ Server error:', error.message);
    console.error('Stack:', error.stack);
  }
  process.exit(1);
});

