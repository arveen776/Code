"""
Main CLI interface for the stock trading simulator.
"""

from trading_simulator import TradingSimulator


def print_portfolio_summary(simulator):
    """Print a formatted portfolio summary."""
    summary = simulator.get_portfolio_summary()
    
    print("\n" + "="*60)
    print("PORTFOLIO SUMMARY")
    print("="*60)
    print(f"Cash: ${summary['cash']:.2f}")
    print(f"Holdings Value: ${summary['holdings_value']:.2f}")
    print(f"Total Portfolio Value: ${summary['total_value']:.2f}")
    print("\nHoldings:")
    if summary['holdings']:
        for symbol, quantity in summary['holdings'].items():
            # Get current price for display
            try:
                price = simulator.stock_data.get_current_price(symbol)
                value = quantity * price
                print(f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}")
            except:
                print(f"  {symbol}: {quantity} shares (price unavailable)")
    else:
        print("  No holdings")
    print("="*60 + "\n")


def print_trade_history(simulator):
    """Print trade history."""
    history = simulator.get_trade_history()
    if not history:
        print("\nNo trades yet.\n")
        return
    
    print("\n" + "="*60)
    print("TRADE HISTORY")
    print("="*60)
    for trade in history:
        timestamp = trade['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        action = trade['action'].upper()
        symbol = trade['symbol']
        quantity = trade['quantity']
        price = trade['price']
        total = trade['total_cost']
        print(f"{timestamp} - {action} {quantity} {symbol} @ ${price:.2f} = ${total:.2f}")
    print("="*60 + "\n")


def get_stock_info(simulator, symbol):
    """Get and display stock information."""
    try:
        info = simulator.stock_data.get_stock_info(symbol)
        print(f"\n{symbol.upper()}: {info['name']}")
        print(f"Current Price: ${info['current_price']:.2f}\n")
    except Exception as e:
        print(f"\nError: {e}\n")


def main():
    """Main CLI loop."""
    print("="*60)
    print("STOCK TRADING SIMULATOR")
    print("="*60)
    
    # Initialize simulator with $10,000 starting cash
    initial_cash = 10000.0
    simulator = TradingSimulator(initial_cash)
    
    print(f"\nStarting with ${initial_cash:.2f} in cash.\n")
    
    while True:
        print("\nOptions:")
        print("1. Check stock price")
        print("2. Buy stock")
        print("3. Sell stock")
        print("4. View portfolio")
        print("5. View trade history")
        print("6. Quit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            symbol = input("Enter stock symbol: ").strip().upper()
            get_stock_info(simulator, symbol)
        
        elif choice == '2':
            symbol = input("Enter stock symbol to buy: ").strip().upper()
            try:
                quantity = int(input("Enter quantity: ").strip())
                result = simulator.buy_stock(symbol, quantity)
                if result['success']:
                    print(f"\n✓ Bought {quantity} shares of {symbol} at ${result['price']:.2f}")
                    print(f"  Total cost: ${result['total_cost']:.2f}")
                    print(f"  Remaining cash: ${simulator.portfolio.get_cash():.2f}")
                else:
                    print(f"\n✗ Error: {result['error']}")
            except ValueError as e:
                print(f"\n✗ Invalid input: {e}")
        
        elif choice == '3':
            symbol = input("Enter stock symbol to sell: ").strip().upper()
            try:
                quantity = int(input("Enter quantity: ").strip())
                result = simulator.sell_stock(symbol, quantity)
                if result['success']:
                    print(f"\n✓ Sold {quantity} shares of {symbol} at ${result['price']:.2f}")
                    print(f"  Total proceeds: ${result['total_proceeds']:.2f}")
                    print(f"  Cash balance: ${simulator.portfolio.get_cash():.2f}")
                else:
                    print(f"\n✗ Error: {result['error']}")
            except ValueError as e:
                print(f"\n✗ Invalid input: {e}")
        
        elif choice == '4':
            print_portfolio_summary(simulator)
        
        elif choice == '5':
            print_trade_history(simulator)
        
        elif choice == '6':
            print("\nThanks for using the Stock Trading Simulator!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()

