"""
Trading simulator that handles buy and sell operations.
"""

from portfolio import Portfolio
from stock_data import StockData


class TradingSimulator:
    def __init__(self, initial_cash=10000.0):
        """Initialize the trading simulator."""
        self.portfolio = Portfolio(initial_cash)
        self.stock_data = StockData()
    
    def buy_stock(self, symbol, quantity):
        """
        Buy a stock.
        Returns a dict with trade details or raises an error.
        """
        try:
            # Get current price
            price = self.stock_data.get_current_price(symbol)
            total_cost = price * quantity
            
            # Check if we have enough cash
            if total_cost > self.portfolio.get_cash():
                raise ValueError(
                    f"Insufficient cash. Need ${total_cost:.2f}, have ${self.portfolio.get_cash():.2f}"
                )
            
            # Execute the trade
            self.portfolio.deduct_cash(total_cost)
            self.portfolio.add_shares(symbol.upper(), quantity)
            self.portfolio.record_trade(symbol.upper(), 'buy', quantity, price, total_cost)
            
            return {
                'success': True,
                'symbol': symbol.upper(),
                'quantity': quantity,
                'price': price,
                'total_cost': total_cost
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sell_stock(self, symbol, quantity):
        """
        Sell a stock.
        Returns a dict with trade details or raises an error.
        """
        try:
            # Get current price
            price = self.stock_data.get_current_price(symbol)
            total_proceeds = price * quantity
            
            # Check if we have enough shares
            if symbol.upper() not in self.portfolio.get_holdings():
                raise ValueError(f"You don't own any shares of {symbol}")
            
            holdings = self.portfolio.get_holdings()[symbol.upper()]
            if quantity > holdings:
                raise ValueError(
                    f"Insufficient shares. You own {holdings} shares of {symbol}, trying to sell {quantity}"
                )
            
            # Execute the trade
            self.portfolio.remove_shares(symbol.upper(), quantity)
            self.portfolio.add_cash(total_proceeds)
            self.portfolio.record_trade(symbol.upper(), 'sell', quantity, price, total_proceeds)
            
            return {
                'success': True,
                'symbol': symbol.upper(),
                'quantity': quantity,
                'price': price,
                'total_proceeds': total_proceeds
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_portfolio_summary(self):
        """Get a summary of the current portfolio."""
        holdings = self.portfolio.get_holdings()
        if not holdings:
            return self.portfolio.get_summary({})
        
        # Get current prices for all holdings
        current_prices = self.stock_data.get_current_prices(list(holdings.keys()))
        return self.portfolio.get_summary(current_prices)
    
    def get_trade_history(self):
        """Get the trade history."""
        return self.portfolio.trade_history

