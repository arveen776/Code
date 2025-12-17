"""
Stock data fetcher using yfinance to get live stock prices.
"""

import yfinance as yf


class StockData:
    def __init__(self):
        """Initialize stock data fetcher."""
        pass
    
    def get_current_price(self, symbol):
        """
        Get current stock price for a symbol.
        Returns the latest closing price.
        """
        try:
            ticker = yf.Ticker(symbol)
            # Get the most recent data
            data = ticker.history(period="1d", interval="1m")
            if data.empty:
                # Fallback to daily data if intraday is not available
                data = ticker.history(period="5d")
                if data.empty:
                    raise ValueError(f"No data available for {symbol}")
            # Return the last closing price
            return float(data['Close'].iloc[-1])
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {str(e)}")
    
    def get_current_prices(self, symbols):
        """
        Get current prices for multiple symbols.
        Returns a dict of {symbol: price}
        """
        prices = {}
        for symbol in symbols:
            try:
                prices[symbol] = self.get_current_price(symbol)
            except Exception as e:
                print(f"Warning: Could not fetch price for {symbol}: {e}")
        return prices
    
    def get_stock_info(self, symbol):
        """
        Get basic info about a stock.
        Returns a dict with name and current price.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = self.get_current_price(symbol)
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', symbol),
                'current_price': current_price
            }
        except Exception as e:
            raise ValueError(f"Error fetching info for {symbol}: {str(e)}")

