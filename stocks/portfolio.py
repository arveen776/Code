"""
Portfolio class to manage cash, holdings, and portfolio value.
"""


class Portfolio:
    def __init__(self, initial_cash=10000.0):
        """Initialize portfolio with starting cash."""
        self.cash = initial_cash
        self.holdings = {}  # {symbol: quantity}
        self.trade_history = []  # List of trade records
        
    def get_holdings(self):
        """Return current holdings dictionary."""
        return self.holdings.copy()
    
    def get_cash(self):
        """Return current cash balance."""
        return self.cash
    
    def add_shares(self, symbol, quantity):
        """Add shares to holdings."""
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
            
    def remove_shares(self, symbol, quantity):
        """Remove shares from holdings."""
        if symbol not in self.holdings:
            raise ValueError(f"No holdings found for {symbol}")
        if self.holdings[symbol] < quantity:
            raise ValueError(f"Insufficient shares. You own {self.holdings[symbol]} shares of {symbol}")
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
    
    def deduct_cash(self, amount):
        """Deduct cash from portfolio."""
        if amount > self.cash:
            raise ValueError(f"Insufficient cash. You have ${self.cash:.2f}")
        self.cash -= amount
    
    def add_cash(self, amount):
        """Add cash to portfolio."""
        self.cash += amount
    
    def record_trade(self, symbol, action, quantity, price, total_cost):
        """Record a trade in history."""
        trade = {
            'symbol': symbol,
            'action': action,  # 'buy' or 'sell'
            'quantity': quantity,
            'price': price,
            'total_cost': total_cost,
            'timestamp': __import__('datetime').datetime.now()
        }
        self.trade_history.append(trade)
    
    def get_portfolio_value(self, current_prices):
        """
        Calculate total portfolio value (cash + holdings value).
        current_prices: dict of {symbol: current_price}
        """
        holdings_value = sum(
            self.holdings.get(symbol, 0) * price 
            for symbol, price in current_prices.items()
        )
        return self.cash + holdings_value
    
    def get_summary(self, current_prices):
        """Get a summary of the portfolio."""
        summary = {
            'cash': self.cash,
            'holdings': self.holdings.copy(),
            'holdings_value': 0,
            'total_value': self.cash
        }
        
        for symbol, quantity in self.holdings.items():
            if symbol in current_prices:
                value = quantity * current_prices[symbol]
                summary['holdings_value'] += value
                summary['total_value'] += value
        
        return summary

