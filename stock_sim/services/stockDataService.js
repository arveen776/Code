const finnhubService = require('./finnhubService');
const yahooFinanceService = require('./yahooFinanceService');
const polygonService = require('./polygonService');
const alphaVantageService = require('./alphaVantageService');
const API_CONFIG = require('../config/apiConfig');

// Mock data generator (fallback)
function generateMockData(symbol, days = 365) {
  const data = [];
  const basePrice = 100 + Math.random() * 50;
  let currentPrice = basePrice;
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    
    const change = (Math.random() - 0.45) * 2;
    currentPrice = Math.max(10, currentPrice + change);
    
    const open = currentPrice + (Math.random() - 0.5) * 2;
    const high = Math.max(open, currentPrice) + Math.random() * 3;
    const low = Math.min(open, currentPrice) - Math.random() * 3;
    const close = currentPrice;
    const volume = Math.floor(1000000 + Math.random() * 5000000);

    data.push({
      date: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: volume
    });
  }

  return data;
}

class StockDataService {
  async getStockData(symbol, timeframe, days = 365) {
    const provider = API_CONFIG.provider.toLowerCase();
    
    try {
      // Try Finnhub first (free tier, requires API key but very easy to get)
      if (finnhubService.isConfigured()) {
        try {
          const data = await finnhubService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            const filtered = this.filterByTimeframe(data, timeframe);
            if (filtered && filtered.length > 0) {
              return filtered;
            }
          }
        } catch (error) {
          console.log('Finnhub API error:', error.message);
        }
      }
      
      // Try Yahoo Finance as fallback (may be blocked)
      if (yahooFinanceService.isConfigured()) {
        try {
          const data = await yahooFinanceService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            const filtered = this.filterByTimeframe(data, timeframe);
            if (filtered && filtered.length > 0) {
              return filtered;
            }
          }
        } catch (yahooError) {
          // Yahoo Finance is often blocked (401), silently continue to next provider
          if (yahooError.message !== 'YAHOO_BLOCKED' && !yahooError.message.includes('401')) {
            console.log('Yahoo Finance unavailable:', yahooError.message);
          }
        }
      }
      
      // Fallback to other providers if configured
      if (provider === 'polygon' && polygonService.isConfigured()) {
        try {
          const data = await polygonService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        } catch (error) {
          console.log('Polygon API error:', error.message);
        }
      }
      
      if (provider === 'alphavantage' && alphaVantageService.isConfigured()) {
        try {
          const data = await alphaVantageService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        } catch (error) {
          console.log('Alpha Vantage API error:', error.message);
        }
      }
      
      // Try other providers as fallback
      if (provider !== 'alphavantage' && alphaVantageService.isConfigured()) {
        try {
          const data = await alphaVantageService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        } catch (error) {
          console.log('Alpha Vantage fallback error:', error.message);
        }
      }
      
      if (provider !== 'polygon' && polygonService.isConfigured()) {
        try {
          const data = await polygonService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        } catch (error) {
          console.log('Polygon fallback error:', error.message);
        }
      }
      
      // Fallback to mock data
      console.log('⚠️  Using mock data - no API keys configured or all APIs failed');
      console.log('   To get real stock data, add FINNHUB_API_KEY to .env file');
      console.log('   Get free API key at: https://finnhub.io/register');
      const mockData = generateMockData(symbol, days);
      const filtered = this.filterByTimeframe(mockData, timeframe);
      if (filtered && filtered.length > 0) {
        return filtered;
      }
      // If filtering removed all data, return the mock data anyway
      return mockData;
      
    } catch (error) {
      console.error(`Error fetching from ${provider}, trying fallback:`, error.message);
      
      // Try fallback providers
      try {
        if (provider === 'polygon' && alphaVantageService.isConfigured()) {
          const data = await alphaVantageService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        }
        if (provider === 'alphavantage' && polygonService.isConfigured()) {
          const data = await polygonService.getDataForTimeframe(symbol, timeframe, days);
          if (data && data.length > 0) {
            return this.filterByTimeframe(data, timeframe);
          }
        }
      } catch (fallbackError) {
        console.error('Fallback also failed, using mock data:', fallbackError.message);
      }
      
      // Ultimate fallback to mock data
      console.log('⚠️  Using mock data - all APIs failed');
      const mockData = generateMockData(symbol, days);
      const filtered = this.filterByTimeframe(mockData, timeframe);
      if (filtered && filtered.length > 0) {
        return filtered;
      }
      // If filtering removed all data, return the mock data anyway
      return mockData;
    }
  }

  async getHistoricalData(symbol, startDate, endDate) {
    const provider = API_CONFIG.provider.toLowerCase();
    
    try {
      // Try Finnhub first
      if (finnhubService.isConfigured()) {
        const data = await finnhubService.getHistoricalData(symbol, startDate, endDate);
        if (data && data.length > 0) {
          return data;
        }
      }
      
      // Try Yahoo Finance as fallback
      if (yahooFinanceService.isConfigured()) {
        try {
          const data = await yahooFinanceService.getHistoricalData(symbol, startDate, endDate);
          if (data && data.length > 0) {
            return data;
          }
        } catch (yahooError) {
          // Yahoo Finance may be blocked
        }
      }
      
      // Fallback to other providers
      if (provider === 'polygon' && polygonService.isConfigured()) {
        return await polygonService.getDailyBars(symbol, startDate, endDate);
      }
      
      if (provider === 'alphavantage' && alphaVantageService.isConfigured()) {
        const allData = await alphaVantageService.getDailyTimeSeries(symbol, 'full');
        return allData.filter(d => d.date >= startDate && d.date <= endDate);
      }
      
      // Fallback to mock
      const mockData = generateMockData(symbol, 365);
      return mockData.filter(d => d.date >= startDate && d.date <= endDate);
      
    } catch (error) {
      console.error('Error fetching historical data:', error.message);
      const mockData = generateMockData(symbol, 365);
      return mockData.filter(d => d.date >= startDate && d.date <= endDate);
    }
  }

  async getCurrentPrice(symbol) {
    const provider = API_CONFIG.provider.toLowerCase();
    
    try {
      // Try Finnhub first
      if (finnhubService.isConfigured()) {
        const quote = await finnhubService.getQuote(symbol);
        if (quote && quote.price) {
          return quote.price;
        }
      }
      
      // Try Yahoo Finance as fallback
      if (yahooFinanceService.isConfigured()) {
        try {
          const quote = await yahooFinanceService.getQuote(symbol);
          if (quote && quote.price) {
            return quote.price;
          }
        } catch (yahooError) {
          // Yahoo Finance may be blocked, continue to other providers
        }
      }
      
      // Fallback to other providers
      if (provider === 'polygon' && polygonService.isConfigured()) {
        const quote = await polygonService.getQuote(symbol);
        if (quote) return quote.price;
      }
      
      if (provider === 'alphavantage' && alphaVantageService.isConfigured()) {
        const quote = await alphaVantageService.getQuote(symbol);
        if (quote) return quote.price;
      }
      
      // Fallback: get latest from daily data
      const data = await this.getStockData(symbol, '1D', 1);
      if (data && data.length > 0) {
        return data[data.length - 1].close;
      }
      
      return null;
    } catch (error) {
      console.error('Error getting current price:', error.message);
      return null;
    }
  }

  // Search for stocks
  async searchStocks(query) {
    try {
      // Try Finnhub first
      if (finnhubService.isConfigured()) {
        const results = await finnhubService.searchStocks(query);
        if (results && results.length > 0) {
          return results;
        }
      }
      
      // Try Yahoo Finance as fallback
      if (yahooFinanceService.isConfigured()) {
        try {
          const results = await yahooFinanceService.searchStocks(query);
          if (results && results.length > 0) {
            return results;
          }
        } catch (yahooError) {
          // Yahoo Finance may be blocked
        }
      }
      
      // If no API keys, return some common stocks for demo
      if (!finnhubService.isConfigured() && !yahooFinanceService.isConfigured()) {
        const commonStocks = [
          { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ' },
          { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ' },
          { symbol: 'GOOGL', name: 'Alphabet Inc.', exchange: 'NASDAQ' },
          { symbol: 'AMZN', name: 'Amazon.com Inc.', exchange: 'NASDAQ' },
          { symbol: 'TSLA', name: 'Tesla Inc.', exchange: 'NASDAQ' },
          { symbol: 'META', name: 'Meta Platforms Inc.', exchange: 'NASDAQ' },
          { symbol: 'NVDA', name: 'NVIDIA Corporation', exchange: 'NASDAQ' }
        ];
        
        // Filter by query if provided
        if (query && query.trim().length > 0) {
          const upperQuery = query.toUpperCase();
          return commonStocks.filter(stock => 
            stock.symbol.includes(upperQuery) || 
            stock.name.toUpperCase().includes(upperQuery)
          );
        }
        
        return commonStocks;
      }
      
      return [];
    } catch (error) {
      console.error('Error searching stocks:', error.message);
      return [];
    }
  }

  filterByTimeframe(data, timeframe) {
    if (!data || data.length === 0) return data;
    
    // For intraday timeframes, return all data (already filtered by API)
    if (['1', '5', '15', '30', '60'].includes(timeframe)) {
      return data;
    }
    
    const now = new Date();
    let cutoffDate = new Date();
    
    switch (timeframe) {
      case '1D':
        // For 1D timeframe, show daily candles for the last 30 days (or all available data)
        // Don't filter to just today - show the daily candles
        cutoffDate.setDate(now.getDate() - 30);
        break;
      case '1W':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case '1M':
        cutoffDate.setMonth(now.getMonth() - 1);
        break;
      case '3M':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      case '6M':
        cutoffDate.setMonth(now.getMonth() - 6);
        break;
      case '1Y':
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        return data;
    }
    
    return data.filter(d => {
      const date = new Date(d.date);
      return date >= cutoffDate;
    });
  }
}

module.exports = new StockDataService();

