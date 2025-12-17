const axios = require('axios');

class FinnhubService {
  constructor() {
    // Finnhub free tier: 60 calls/minute, no credit card required
    // Get free API key at: https://finnhub.io/register
    this.apiKey = process.env.FINNHUB_API_KEY || '';
    this.baseUrl = 'https://finnhub.io/api/v1';
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute cache
  }

  // Search for stocks
  async searchStocks(query) {
    try {
      if (!this.apiKey) {
        // Without API key, return empty (will fallback to other services)
        return [];
      }

      const response = await axios.get(`${this.baseUrl}/search`, {
        params: {
          q: query,
          token: this.apiKey
        },
        timeout: 10000
      });

      if (response.data && response.data.result) {
        return response.data.result
          .filter(item => item.type === 'Common Stock' && item.symbol)
          .slice(0, 10)
          .map(item => ({
            symbol: item.symbol,
            name: item.description || item.symbol,
            exchange: item.displaySymbol ? item.displaySymbol.split('.')[0] : 'N/A'
          }));
      }
      return [];
    } catch (error) {
      console.error('Finnhub Search Error:', error.message);
      return [];
    }
  }

  // Get quote (current price)
  async getQuote(symbol) {
    try {
      if (!this.apiKey) {
        return null;
      }

      const response = await axios.get(`${this.baseUrl}/quote`, {
        params: {
          symbol: symbol,
          token: this.apiKey
        },
        timeout: 10000
      });

      if (response.data && response.data.c !== null && response.data.c !== undefined) {
        const change = response.data.c - (response.data.pc || response.data.c);
        const changePercent = response.data.pc ? ((change / response.data.pc) * 100) : 0;

        return {
          symbol: symbol,
          price: parseFloat(response.data.c.toFixed(2)),
          change: parseFloat(change.toFixed(2)),
          changePercent: parseFloat(changePercent.toFixed(2)),
          volume: parseInt(response.data.v || 0),
          timestamp: new Date().toISOString()
        };
      }
      return null;
    } catch (error) {
      console.error('Finnhub Quote Error:', error.message);
      return null;
    }
  }

  // Get candlestick data
  async getCandles(symbol, resolution, from, to) {
    try {
      if (!this.apiKey) {
        return [];
      }

      const response = await axios.get(`${this.baseUrl}/stock/candle`, {
        params: {
          symbol: symbol,
          resolution: resolution,
          from: from,
          to: to,
          token: this.apiKey
        },
        timeout: 10000
      });

      if (response.data && response.data.s === 'ok' && response.data.t) {
        const data = [];
        for (let i = 0; i < response.data.t.length; i++) {
          data.push({
            date: new Date(response.data.t[i] * 1000).toISOString().split('T')[0],
            timestamp: response.data.t[i] * 1000,
            open: parseFloat(response.data.o[i].toFixed(2)),
            high: parseFloat(response.data.h[i].toFixed(2)),
            low: parseFloat(response.data.l[i].toFixed(2)),
            close: parseFloat(response.data.c[i].toFixed(2)),
            volume: parseInt(response.data.v[i] || 0)
          });
        }
        return data;
      }
      return [];
    } catch (error) {
      console.error('Finnhub Candles Error:', error.message);
      return [];
    }
  }

  // Get data for timeframe
  async getDataForTimeframe(symbol, timeframe, days = 365) {
    if (!this.apiKey || this.apiKey === 'your_finnhub_api_key_here') {
      return [];
    }

    const resolutionMap = {
      '1': '1',    // 1 minute
      '5': '5',    // 5 minutes
      '15': '15',  // 15 minutes
      '30': '30',  // 30 minutes
      '60': '60',  // 1 hour
      '1D': 'D',   // 1 day
      '1W': 'W',   // 1 week
      '1M': 'M',   // 1 month
      '3M': 'M',   // 1 month (for 3M, we'll get more data)
      '6M': 'M',   // 1 month
      '1Y': 'M'    // 1 month
    };

    const resolution = resolutionMap[timeframe] || 'D';
    
    // Calculate time range
    const to = Math.floor(Date.now() / 1000);
    let from;
    
    if (['1', '5', '15', '30', '60'].includes(timeframe)) {
      // Intraday: get last 1-5 days
      from = to - (days * 24 * 60 * 60);
    } else if (timeframe === '1D') {
      from = to - (30 * 24 * 60 * 60); // 30 days
    } else if (timeframe === '1W') {
      from = to - (90 * 24 * 60 * 60); // 90 days
    } else if (timeframe === '1M') {
      from = to - (180 * 24 * 60 * 60); // 180 days
    } else if (timeframe === '3M') {
      from = to - (365 * 24 * 60 * 60); // 1 year
    } else if (timeframe === '6M') {
      from = to - (365 * 24 * 60 * 60); // 1 year
    } else {
      from = to - (730 * 24 * 60 * 60); // 2 years
    }

    try {
      // For US stocks, add .US suffix if not present
      let symbolToUse = symbol;
      if (!symbol.includes('.') && !symbol.includes('-')) {
        symbolToUse = symbol + '.US';
      }

      const data = await this.getCandles(symbolToUse, resolution, from, to);
      return data;
    } catch (error) {
      console.error('Error getting data for timeframe:', error.message);
      return [];
    }
  }

  // Get historical data
  async getHistoricalData(symbol, startDate, endDate) {
    if (!this.apiKey) {
      return [];
    }

    const from = Math.floor(new Date(startDate).getTime() / 1000);
    const to = Math.floor(new Date(endDate).getTime() / 1000);

    let symbolToUse = symbol;
    if (!symbol.includes('.') && !symbol.includes('-')) {
      symbolToUse = symbol + '.US';
    }

    return await this.getCandles(symbolToUse, 'D', from, to);
  }

  // Check if API key is configured
  isConfigured() {
    return !!this.apiKey && this.apiKey.length > 0 && this.apiKey !== 'your_finnhub_api_key_here';
  }
}

module.exports = new FinnhubService();

