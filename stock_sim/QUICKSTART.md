# Quick Start Guide

Get up and running in 3 minutes!

## Step 1: Install Dependencies
```bash
npm install
```

## Step 2: (Optional) Add API Keys for Real Data

**Option A: Use Polygon.io (Recommended)**
1. Sign up at https://polygon.io/
2. Get your free API key
3. Create `.env` file:
   ```env
   POLYGON_API_KEY=your_key_here
   API_PROVIDER=polygon
   ```

**Option B: Use Alpha Vantage**
1. Get free key at https://www.alphavantage.co/support/#api-key
2. Create `.env` file:
   ```env
   ALPHA_VANTAGE_API_KEY=your_key_here
   API_PROVIDER=alphavantage
   ```

**Option C: Skip API Keys (Use Mock Data)**
- No configuration needed!
- App works with realistic mock data
- Perfect for testing and learning

## Step 3: Start the Server
```bash
npm start
```

## Step 4: Open in Browser
```
http://localhost:3000
```

## That's It! 🎉

You can now:
- View stock charts with multiple time frames
- See real-time price updates (if API keys configured)
- View historical data for backtesting
- Buy and sell stocks in your portfolio

## Tips

- **No API keys?** The app uses mock data - still fully functional!
- **Rate limits?** The app automatically falls back to other providers or mock data
- **Testing strategies?** Use the historical date picker to view past data
- **Real-time updates?** Prices update every 5 seconds when viewing live data

For detailed setup, see [SETUP.md](SETUP.md)

