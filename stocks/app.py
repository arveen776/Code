"""
Flask server for Stock Trading Simulator Web Application
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from trading_simulator import TradingSimulator

app = Flask(__name__)
CORS(app)

# Use a single simulator instance for simplicity (in production, use proper session management)
simulator = TradingSimulator(10000.0)

def get_simulator():
    """Get the simulator instance."""
    return simulator

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio summary."""
    try:
        simulator = get_simulator()
        summary = simulator.get_portfolio_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/search', methods=['POST'])
def search_stock():
    """Search for a stock symbol."""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
        
        simulator = get_simulator()
        info = simulator.stock_data.get_stock_info(symbol)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/chart', methods=['POST'])
def get_chart_data():
    """Get chart data for a stock."""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        period = data.get('period', '1d')
        interval = data.get('interval', '5m')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
        
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period, interval=interval)
        
        if hist_data.empty:
            return jsonify({'success': False, 'error': 'No chart data available'}), 404
        
        # Limit to last 500 candles
        if len(hist_data) > 500:
            hist_data = hist_data.tail(500)
        
            # Convert to JSON-serializable format
            chart_data = []
            for idx, row in hist_data.iterrows():
                # Convert timezone-aware datetime to ISO string
                if hasattr(idx, 'tz_localize'):
                    time_str = idx.tz_localize(None).isoformat() if idx.tzinfo is None else idx.isoformat()
                else:
                    time_str = idx.isoformat() if hasattr(idx, 'isoformat') else str(idx)
                
                chart_data.append({
                    'time': time_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })
        
        return jsonify({'success': True, 'data': chart_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trade/buy', methods=['POST'])
def buy_stock():
    """Execute a buy order."""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        quantity = int(data.get('quantity', 0))
        
        if not symbol or quantity <= 0:
            return jsonify({'success': False, 'error': 'Invalid symbol or quantity'}), 400
        
        simulator = get_simulator()
        result = simulator.buy_stock(symbol, quantity)
        
        if result['success']:
            # Get updated portfolio
            portfolio = simulator.get_portfolio_summary()
            result['portfolio'] = portfolio
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trade/sell', methods=['POST'])
def sell_stock():
    """Execute a sell order."""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        quantity = int(data.get('quantity', 0))
        
        if not symbol or quantity <= 0:
            return jsonify({'success': False, 'error': 'Invalid symbol or quantity'}), 400
        
        simulator = get_simulator()
        result = simulator.sell_stock(symbol, quantity)
        
        if result['success']:
            # Get updated portfolio
            portfolio = simulator.get_portfolio_summary()
            result['portfolio'] = portfolio
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get trade history."""
    try:
        simulator = get_simulator()
        history = simulator.get_trade_history()
        
        # Convert datetime to string
        history_data = []
        for trade in history:
            trade_dict = trade.copy()
            trade_dict['timestamp'] = trade['timestamp'].isoformat()
            history_data.append(trade_dict)
        
        return jsonify({'success': True, 'data': history_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

