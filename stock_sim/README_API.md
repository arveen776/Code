# API Setup Guide

## Quick Start (No API Key Required)

The app works out of the box with **mock data** for testing. No API key needed!

## Get Real Stock Data (Recommended)

For real stock data, get a **free Finnhub API key** (takes 30 seconds):

1. Go to https://finnhub.io/register
2. Sign up (free, no credit card required)
3. Copy your API key from the dashboard
4. Create a `.env` file in the project root:
   ```
   FINNHUB_API_KEY=your_api_key_here
   ```
5. Restart the server

**Finnhub Free Tier:**
- ✅ 60 API calls per minute
- ✅ Real-time and historical data
- ✅ Stock search
- ✅ No credit card required
- ✅ Free forever

## Alternative APIs

You can also use:
- **Polygon.io** - Free tier: 5 calls/minute
- **Alpha Vantage** - Free tier: 5 calls/minute, 500 calls/day

Add to `.env`:
```
POLYGON_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

The app will automatically use the best available API.

