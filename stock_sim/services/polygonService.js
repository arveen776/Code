const axios = require('axios');
const API_CONFIG = require('../config/apiConfig');

class PolygonService {
  constructor() {
    this.apiKey = API_CONFIG.polygon.apiKey;
    this.baseUrl = API_CONFIG.polygon.baseUrl;
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute cache
  }

  // Get aggregates (bars) for a stock
  async getAggregates(symbol, multiplier, timespan, from, to) {
    try {
      const url = `${this.baseUrl}/v2/aggs/ticker/${symbol}/range/${multiplier}/${timespan}/${from}/${to}`;
      const response = await axios.get(url, {
        params: {
          adjusted: true,
          sort: 'asc',
          limit: 50000,
          apiKey: this.apiKey
        }
      });

      if (response.data.status === 'OK' && response.data.results) {
        return response.data.results.map(bar => ({
          date: new Date(bar.t).toISOString().split('T')[0],
          timestamp: bar.t,
          open: bar.o,
          high: bar.h,
          low: bar.l,
          close: bar.c,
          volume: bar.v
        }));
      }
      throw new Error('No data returned from Polygon API');
    } catch (error) {
      console.error('Polygon API Error:', error.message);
      throw error;
    }
  }

  // Get previous close
  async getPreviousClose(symbol) {
    try {
      const url = `${this.baseUrl}/v2/aggs/ticker/${symbol}/prev`;
      const response = await axios.get(url, {
        params: {
          adjusted: true,
          apiKey: this.apiKey
        }
      });

      if (response.data.status === 'OK' && response.data.results && response.data.results.length > 0) {
        const result = response.data.results[0];
        return {
          date: new Date(result.t).toISOString().split('T')[0],
          open: result.o,
          high: result.h,
          low: result.l,
          close: result.c,
          volume: result.v
        };
      }
      return null;
    } catch (error) {
      console.error('Polygon Previous Close Error:', error.message);
      return null;
    }
  }

  // Get real-time quote
  async getQuote(symbol) {
    try {
      const url = `${this.baseUrl}/v2/last/trade/${symbol}`;
      const response = await axios.get(url, {
        params: {
          apiKey: this.apiKey
        }
      });

      if (response.data.status === 'OK' && response.data.results) {
        return {
          price: response.data.results.p,
          timestamp: response.data.results.t
        };
      }
      return null;
    } catch (error) {
      console.error('Polygon Quote Error:', error.message);
      return null;
    }
  }

  // Get daily bars for a date range
  async getDailyBars(symbol, startDate, endDate) {
    return await this.getAggregates(symbol, 1, 'day', startDate, endDate);
  }

  // Get data for timeframe
  async getDataForTimeframe(symbol, timeframe, days = 365) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const from = startDate.toISOString().split('T')[0];
    const to = endDate.toISOString().split('T')[0];

    let multiplier = 1;
    let timespan = 'day';

    // Adjust for intraday timeframes
    if (timeframe === '1D') {
      // Get today's minute bars
      const today = new Date().toISOString().split('T')[0];
      try {
        return await this.getAggregates(symbol, 1, 'minute', today, today);
      } catch (error) {
        // Fallback to daily if intraday fails
        return await this.getDailyBars(symbol, from, to);
      }
    }

    return await this.getDailyBars(symbol, from, to);
  }

  // Check if API key is configured
  isConfigured() {
    return !!this.apiKey && this.apiKey !== 'your_polygon_api_key_here';
  }
}

module.exports = new PolygonService();

