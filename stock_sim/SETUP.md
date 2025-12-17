# API Setup Guide

This guide will help you set up API keys for real stock data in the Stock Trading Simulator.

## Why Use Real APIs?

- **Real Market Data**: Test with actual stock prices and movements
- **Historical Accuracy**: Backtest strategies on real historical data
- **Live Updates**: See real-time price changes as they happen
- **Market Realism**: Experience realistic trading conditions

## Option 1: Polygon.io (Recommended) ⭐

**Best for:** Real-time data and live updates

### Steps:

1. **Sign Up**: Go to https://polygon.io/
2. **Get Free API Key**: 
   - Create a free account
   - Navigate to your dashboard
   - Copy your API key
3. **Configure**:
   ```env
   POLYGON_API_KEY=your_key_here
   API_PROVIDER=polygon
   ```

### Free Tier Limits:
- 5 API calls per minute
- Real-time data access
- Historical data (limited)

### Why Polygon.io?
- ✅ Lowest latency real-time data
- ✅ Excellent for live trading simulation
- ✅ WebSocket support available (paid tiers)
- ✅ Comprehensive market coverage

---

## Option 2: Alpha Vantage

**Best for:** Historical data and backtesting

### Steps:

1. **Sign Up**: Go to https://www.alphavantage.co/support/#api-key
2. **Get Free API Key**:
   - Fill out the form
   - Receive API key via email (usually instant)
3. **Configure**:
   ```env
   ALPHA_VANTAGE_API_KEY=your_key_here
   API_PROVIDER=alphavantage
   ```

### Free Tier Limits:
- 5 API calls per minute
- 500 API calls per day
- Full historical data access

### Why Alpha Vantage?
- ✅ Extensive historical data
- ✅ Reliable and stable service
- ✅ Good for backtesting
- ✅ Multiple data functions

---

## Configuration

1. **Create `.env` file** in the project root:
   ```env
   # Primary API (Polygon.io)
   POLYGON_API_KEY=your_polygon_api_key_here
   
   # Fallback API (Alpha Vantage)
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   
   # Which API to use: 'polygon', 'alphavantage', or 'mock'
   API_PROVIDER=polygon
   ```

2. **Restart the server** after adding API keys

3. **Verify**: Check the server console for API status messages

## Using Both APIs

The simulator automatically uses fallback logic:
1. Tries primary provider (set in `API_PROVIDER`)
2. Falls back to other provider if primary fails
3. Uses mock data if both fail or no keys configured

## Testing Without API Keys

The simulator works with mock data if no API keys are configured. This is perfect for:
- Development and testing
- Learning the interface
- Testing without API rate limits

## Rate Limit Handling

Both free tiers have rate limits. The simulator:
- Caches data to reduce API calls
- Shows error messages if limits are exceeded
- Automatically falls back to other provider or mock data

## Troubleshooting

**"API rate limit exceeded"**
- Wait a minute and try again
- Consider using both APIs for better coverage
- Check your API key is valid

**"No data returned"**
- Verify your API key is correct
- Check if the symbol exists (use major stocks like AAPL, MSFT)
- Try the fallback provider

**Real-time updates not working**
- Ensure WebSocket connection is established (check browser console)
- Verify API key has real-time access (Polygon.io free tier has limited real-time)
- Check server console for errors

## Next Steps

Once configured:
1. Start the server: `npm start`
2. Open http://localhost:3000
3. Select a stock symbol
4. Watch real-time updates!
5. Test historical data viewing for backtesting

