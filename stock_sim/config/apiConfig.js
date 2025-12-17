require('dotenv').config();

const API_CONFIG = {
  provider: process.env.API_PROVIDER || 'finnhub', // Default to Finnhub (free tier, easy to get API key)
  finnhub: {
    apiKey: process.env.FINNHUB_API_KEY || '',
  },
  polygon: {
    apiKey: process.env.POLYGON_API_KEY || '',
    baseUrl: 'https://api.polygon.io',
    rateLimit: 5, // requests per minute on free tier
  },
  alphaVantage: {
    apiKey: process.env.ALPHA_VANTAGE_API_KEY || '',
    baseUrl: 'https://www.alphavantage.co/query',
    rateLimit: 5, // requests per minute on free tier
  }
};

module.exports = API_CONFIG;

