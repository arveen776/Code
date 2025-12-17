const axios = require('axios');

class YahooFinanceService {
  constructor() {
    this.baseUrl = 'https://query1.finance.yahoo.com/v8/finance/chart';
    this.searchUrl = 'https://query1.finance.yahoo.com/v1/finance/search';
    this.quoteUrl = 'https://query1.finance.yahoo.com/v7/finance/quote';
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute cache
  }

  // Search for stocks
  async searchStocks(query) {
    try {
      const response = await axios.get(this.searchUrl, {
        params: {
          q: query,
          quotesCount: 10,
          newsCount: 0
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      if (response.data && response.data.quotes) {
        return response.data.quotes
          .filter(quote => quote.quoteType === 'EQUITY' && quote.symbol)
          .map(quote => ({
            symbol: quote.symbol,
            name: quote.longname || quote.shortname || quote.symbol,
            exchange: quote.exchange || 'N/A'
          }));
      }
      return [];
    } catch (error) {
      // Yahoo Finance is often blocked, don't spam console
      if (error.response && error.response.status === 401) {
        return [];
      }
      if (error.response && error.response.status !== 401) {
        console.error('Yahoo Finance Search Error:', error.message);
      }
      return [];
    }
  }

  // Get chart data for a symbol
  async getChartData(symbol, interval = '1d', range = '1y') {
    try {
      const url = `${this.baseUrl}/${symbol}`;
      const response = await axios.get(url, {
        params: {
          interval: interval,
          range: range,
          includePrePost: false,
          events: 'div,splits'
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000 // 10 second timeout
      });

      if (!response.data || !response.data.chart) {
        throw new Error('Invalid response from Yahoo Finance');
      }

      if (response.data.chart.error) {
        throw new Error(response.data.chart.error.description || 'Error from Yahoo Finance');
      }

      if (response.data.chart.result && response.data.chart.result.length > 0) {
        const result = response.data.chart.result[0];
        if (!result || !result.timestamp || !result.indicators) {
          throw new Error('Invalid data format from Yahoo Finance');
        }

        const timestamps = result.timestamp;
        const quote = result.indicators.quote[0];
        const adjclose = result.indicators.adjclose ? result.indicators.adjclose[0].adjclose : null;

        const data = [];
        for (let i = 0; i < timestamps.length; i++) {
          const timestamp = timestamps[i] * 1000; // Convert to milliseconds
          const date = new Date(timestamp);
          
          // Skip if any required data is missing
          if (quote.open[i] === null || quote.high[i] === null || 
              quote.low[i] === null || quote.close[i] === null) {
            continue;
          }

          const close = adjclose && adjclose[i] !== null ? adjclose[i] : quote.close[i];
          const open = quote.open[i];
          const high = quote.high[i];
          const low = quote.low[i];
          const volume = quote.volume[i] || 0;

          data.push({
            date: date.toISOString().split('T')[0],
            timestamp: timestamp,
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: parseInt(volume)
          });
        }

        return data.length > 0 ? data : [];
      }
      throw new Error('No data returned from Yahoo Finance');
    } catch (error) {
      if (error.response && error.response.status === 401) {
        // Yahoo Finance blocked, throw a specific error that can be caught
        throw new Error('YAHOO_BLOCKED');
      }
      if (error.response && error.response.status === 404) {
        throw new Error(`Symbol ${symbol} not found`);
      }
      // Only log non-401 errors
      if (!error.response || error.response.status !== 401) {
        console.error('Yahoo Finance Chart Error:', error.message);
      }
      throw error;
    }
  }

  // Get intraday data
  async getIntradayData(symbol, interval = '5m') {
    try {
      // For intraday, use 1d range to get today's data
      const url = `${this.baseUrl}/${symbol}`;
      const response = await axios.get(url, {
        params: {
          interval: interval,
          range: '1d',
          includePrePost: false
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      if (response.data && response.data.chart && response.data.chart.result) {
        const result = response.data.chart.result[0];
        if (!result || !result.timestamp || !result.indicators) {
          return [];
        }

        const timestamps = result.timestamp;
        const quote = result.indicators.quote[0];
        const adjclose = result.indicators.adjclose ? result.indicators.adjclose[0].adjclose : null;

        const data = [];
        for (let i = 0; i < timestamps.length; i++) {
          const timestamp = timestamps[i] * 1000;
          const date = new Date(timestamp);
          
          if (quote.open[i] === null || quote.high[i] === null || 
              quote.low[i] === null || quote.close[i] === null) {
            continue;
          }

          const close = adjclose && adjclose[i] !== null ? adjclose[i] : quote.close[i];
          
          data.push({
            date: date.toISOString().split('T')[0],
            timestamp: timestamp,
            open: parseFloat(quote.open[i].toFixed(2)),
            high: parseFloat(quote.high[i].toFixed(2)),
            low: parseFloat(quote.low[i].toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: parseInt(quote.volume[i] || 0)
          });
        }

        return data;
      }
      return [];
    } catch (error) {
      console.error('Yahoo Finance Intraday Error:', error.message);
      return [];
    }
  }

  // Get current quote
  async getQuote(symbol) {
    try {
      const response = await axios.get(this.quoteUrl, {
        params: {
          symbols: symbol,
          fields: 'regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketVolume'
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000 // 10 second timeout
      });

      if (response.data && response.data.quoteResponse) {
        if (response.data.quoteResponse.error) {
          console.error('Yahoo Finance Quote Error:', response.data.quoteResponse.error);
          return null;
        }
        
        if (response.data.quoteResponse.result && response.data.quoteResponse.result.length > 0) {
          const result = response.data.quoteResponse.result[0];
          if (result && result.regularMarketPrice !== null && result.regularMarketPrice !== undefined) {
            return {
              symbol: result.symbol,
              price: parseFloat(result.regularMarketPrice.toFixed(2)),
              change: parseFloat((result.regularMarketChange || 0).toFixed(2)),
              changePercent: parseFloat((result.regularMarketChangePercent || 0).toFixed(2)),
              volume: parseInt(result.regularMarketVolume || 0),
              timestamp: new Date().toISOString()
            };
          }
        }
      }
      return null;
    } catch (error) {
      // Yahoo Finance is often blocked (401), don't spam console
      if (error.response && error.response.status === 401) {
        // Silently fail - this is expected
        return null;
      }
      // Only log unexpected errors
      if (error.response && error.response.status !== 401) {
        console.error('Yahoo Finance Quote Error:', error.message);
      }
      return null;
    }
  }

  // Get data for timeframe
  async getDataForTimeframe(symbol, timeframe, days = 365) {
    // Map timeframes to Yahoo Finance intervals and ranges
    const intervalMap = {
      '1': '1m',   // 1 minute
      '5': '5m',   // 5 minutes
      '15': '15m', // 15 minutes
      '30': '30m', // 30 minutes
      '60': '1h',  // 1 hour
      '1D': '1d',  // 1 day
      '1W': '1wk', // 1 week
      '1M': '1mo', // 1 month
      '3M': '3mo', // 3 months
      '6M': '6mo', // 6 months
      '1Y': '1y'   // 1 year
    };

    const rangeMap = {
      '1': '1d',
      '5': '1d',
      '15': '1d',
      '30': '1d',
      '60': '5d',
      '1D': '1mo',
      '1W': '3mo',
      '1M': '6mo',
      '3M': '1y',
      '6M': '1y',
      '1Y': '2y'
    };

    const interval = intervalMap[timeframe] || '1d';
    const range = rangeMap[timeframe] || '1y';

    try {
      // For intraday timeframes, use intraday method
      if (['1', '5', '15', '30', '60'].includes(timeframe)) {
        const data = await this.getIntradayData(symbol, interval);
        return data;
      }

      // For daily and above, use chart data
      const data = await this.getChartData(symbol, interval, range);
      return data;
    } catch (error) {
      console.error('Error getting data for timeframe:', error.message);
      throw error;
    }
  }

  // Get historical data for date range
  async getHistoricalData(symbol, startDate, endDate) {
    try {
      // Calculate range based on date difference
      const start = new Date(startDate);
      const end = new Date(endDate);
      const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));

      let range = '1y';
      if (diffDays <= 5) range = '5d';
      else if (diffDays <= 30) range = '1mo';
      else if (diffDays <= 90) range = '3mo';
      else if (diffDays <= 180) range = '6mo';
      else if (diffDays <= 365) range = '1y';
      else range = '2y';

      const data = await this.getChartData(symbol, '1d', range);
      
      // Filter by date range
      return data.filter(d => {
        const date = new Date(d.date);
        return date >= start && date <= end;
      });
    } catch (error) {
      console.error('Error getting historical data:', error.message);
      throw error;
    }
  }

  // Check if service is configured (always true for Yahoo Finance)
  isConfigured() {
    return true;
  }
}

module.exports = new YahooFinanceService();

