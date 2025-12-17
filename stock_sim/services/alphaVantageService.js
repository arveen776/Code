const axios = require('axios');
const API_CONFIG = require('../config/apiConfig');

class AlphaVantageService {
  constructor() {
    this.apiKey = API_CONFIG.alphaVantage.apiKey;
    this.baseUrl = API_CONFIG.alphaVantage.baseUrl;
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute cache
  }

  // Get daily time series
  async getDailyTimeSeries(symbol, outputsize = 'full') {
    try {
      const url = this.baseUrl;
      const response = await axios.get(url, {
        params: {
          function: 'TIME_SERIES_DAILY',
          symbol: symbol,
          outputsize: outputsize,
          apikey: this.apiKey
        }
      });

      if (response.data['Error Message']) {
        throw new Error(response.data['Error Message']);
      }

      if (response.data['Note']) {
        throw new Error('API rate limit exceeded. Please wait a moment.');
      }

      const timeSeries = response.data['Time Series (Daily)'];
      if (!timeSeries) {
        throw new Error('No time series data available');
      }

      // Convert to our format
      const data = [];
      for (const [date, values] of Object.entries(timeSeries)) {
        data.push({
          date: date,
          open: parseFloat(values['1. open']),
          high: parseFloat(values['2. high']),
          low: parseFloat(values['3. low']),
          close: parseFloat(values['4. close']),
          volume: parseInt(values['5. volume'])
        });
      }

      // Sort by date ascending
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
      return data;
    } catch (error) {
      console.error('Alpha Vantage API Error:', error.message);
      throw error;
    }
  }

  // Get intraday data (for 1D timeframe)
  async getIntradayTimeSeries(symbol, interval = '1min') {
    try {
      const url = this.baseUrl;
      const response = await axios.get(url, {
        params: {
          function: 'TIME_SERIES_INTRADAY',
          symbol: symbol,
          interval: interval,
          outputsize: 'full',
          apikey: this.apiKey
        }
      });

      if (response.data['Error Message']) {
        throw new Error(response.data['Error Message']);
      }

      if (response.data['Note']) {
        throw new Error('API rate limit exceeded. Please wait a moment.');
      }

      const timeSeriesKey = `Time Series (${interval})`;
      const timeSeries = response.data[timeSeriesKey];
      if (!timeSeries) {
        throw new Error('No intraday data available');
      }

      // Convert to our format
      const data = [];
      for (const [timestamp, values] of Object.entries(timeSeries)) {
        const date = timestamp.split(' ')[0];
        data.push({
          date: date,
          timestamp: timestamp,
          open: parseFloat(values['1. open']),
          high: parseFloat(values['2. high']),
          low: parseFloat(values['3. low']),
          close: parseFloat(values['4. close']),
          volume: parseInt(values['5. volume'])
        });
      }

      // Sort by timestamp ascending
      data.sort((a, b) => {
        const timeA = a.timestamp || a.date;
        const timeB = b.timestamp || b.date;
        return new Date(timeA) - new Date(timeB);
      });

      return data;
    } catch (error) {
      console.error('Alpha Vantage Intraday Error:', error.message);
      throw error;
    }
  }

  // Get quote endpoint (real-time)
  async getQuote(symbol) {
    try {
      const url = this.baseUrl;
      const response = await axios.get(url, {
        params: {
          function: 'GLOBAL_QUOTE',
          symbol: symbol,
          apikey: this.apiKey
        }
      });

      if (response.data['Error Message']) {
        throw new Error(response.data['Error Message']);
      }

      const quote = response.data['Global Quote'];
      if (!quote || !quote['05. price']) {
        return null;
      }

      return {
        symbol: quote['01. symbol'],
        price: parseFloat(quote['05. price']),
        change: parseFloat(quote['09. change']),
        changePercent: parseFloat(quote['10. change percent'].replace('%', '')),
        volume: parseInt(quote['06. volume']),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Alpha Vantage Quote Error:', error.message);
      return null;
    }
  }

  // Get data for timeframe
  async getDataForTimeframe(symbol, timeframe, days = 365) {
    if (timeframe === '1D') {
      // Try intraday, fallback to daily
      try {
        const data = await this.getIntradayTimeSeries(symbol, '5min');
        // Get only today's data
        const today = new Date().toISOString().split('T')[0];
        return data.filter(d => d.date === today);
      } catch (error) {
        // Fallback to daily
        const allData = await this.getDailyTimeSeries(symbol, 'full');
        return allData.slice(-1);
      }
    }

    // For other timeframes, use daily data
    const allData = await this.getDailyTimeSeries(symbol, 'full');
    return allData;
  }

  // Check if API key is configured
  isConfigured() {
    return !!this.apiKey && this.apiKey !== 'your_alpha_vantage_api_key_here';
  }
}

module.exports = new AlphaVantageService();

