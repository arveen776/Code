// Stock Trading Simulator Web Application

class TradingApp {
    constructor() {
        this.currentSymbol = null;
        this.currentPrice = null;
        this.currentPeriod = '1d';
        this.currentInterval = '5m';
        this.chart = null;
        this.candlestickSeries = null;
        this.autoRefreshInterval = null;
        this.autoRefreshEnabled = true;
        
        this.initializeEventListeners();
        this.loadPortfolio();
        this.loadHistory();
    }
    
    initializeEventListeners() {
        // Search
        document.getElementById('search-btn').addEventListener('click', () => this.searchStock());
        document.getElementById('stock-symbol').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchStock();
        });
        
        // Timeframe buttons
        document.querySelectorAll('.timeframe-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentPeriod = btn.dataset.period;
                this.currentInterval = btn.dataset.interval;
                
                // Update active state
                document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                if (this.currentSymbol) {
                    this.loadChart();
                }
            });
        });
        
        // Trading
        document.getElementById('buy-btn').addEventListener('click', () => this.buyStock());
        document.getElementById('sell-btn').addEventListener('click', () => this.sellStock());
        
        // Refresh
        document.getElementById('refresh-btn').addEventListener('click', () => this.manualRefresh());
        document.getElementById('auto-refresh').addEventListener('change', (e) => {
            this.autoRefreshEnabled = e.target.checked;
            if (this.autoRefreshEnabled) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });
    }
    
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(`/api/${endpoint}`, options);
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type} show`;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    async loadPortfolio() {
        const result = await this.apiCall('portfolio');
        if (result.success) {
            this.updatePortfolio(result.data);
        }
    }
    
    updatePortfolio(data) {
        document.getElementById('total-value').textContent = `$${data.total_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        document.getElementById('cash-value').textContent = `$${data.cash.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        document.getElementById('holdings-value').textContent = `$${data.holdings_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        
        // Update holdings table
        const tbody = document.getElementById('holdings-body');
        tbody.innerHTML = '';
        
        if (Object.keys(data.holdings).length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-message">No holdings</td></tr>';
        } else {
            // We need to fetch current prices for holdings
            this.updateHoldingsTable(data.holdings);
        }
    }
    
    async updateHoldingsTable(holdings) {
        const tbody = document.getElementById('holdings-body');
        tbody.innerHTML = '';
        
        for (const [symbol, quantity] of Object.entries(holdings)) {
            try {
                const priceResult = await this.apiCall('stock/search', 'POST', { symbol });
                if (priceResult.success) {
                    const price = priceResult.data.current_price;
                    const value = quantity * price;
                    const row = `
                        <tr>
                            <td>${symbol}</td>
                            <td>${quantity}</td>
                            <td>$${price.toFixed(2)}</td>
                            <td>$${value.toFixed(2)}</td>
                        </tr>
                    `;
                    tbody.innerHTML += row;
                }
            } catch (error) {
                console.error(`Error fetching price for ${symbol}:`, error);
            }
        }
    }
    
    async searchStock() {
        const symbol = document.getElementById('stock-symbol').value.trim().toUpperCase();
        if (!symbol) {
            this.showToast('Please enter a stock symbol', 'error');
            return;
        }
        
        const result = await this.apiCall('stock/search', 'POST', { symbol });
        if (result.success) {
            this.currentSymbol = symbol;
            this.currentPrice = result.data.current_price;
            
            document.getElementById('stock-name').textContent = `${result.data.name} (${symbol})`;
            document.getElementById('stock-price').textContent = `$${result.data.current_price.toFixed(2)}`;
            
            this.loadChart();
            this.updateTradeInfo();
            
            if (this.autoRefreshEnabled) {
                this.startAutoRefresh();
            }
        } else {
            this.showToast(result.error, 'error');
        }
    }
    
    async loadChart() {
        if (!this.currentSymbol) return;
        
        const result = await this.apiCall('stock/chart', 'POST', {
            symbol: this.currentSymbol,
            period: this.currentPeriod,
            interval: this.currentInterval
        });
        
        if (result.success) {
            this.renderChart(result.data);
        } else {
            this.showToast(result.error, 'error');
        }
    }
    
    renderChart(data) {
        const container = document.getElementById('stock-chart');
        
        if (!container) {
            console.error('Chart container not found');
            return;
        }
        
        // Clear existing chart
        if (this.chart) {
            try {
                this.chart.remove();
            } catch (e) {
                console.log('No existing chart to remove');
            }
        }
        
        // Clear container
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="empty-message">No chart data available</div>';
            return;
        }
        
        try {
            // Ensure container has dimensions - wait a bit for layout
            setTimeout(() => {
                const width = container.clientWidth || 800;
                const height = container.clientHeight || 400;
                
                console.log('Creating chart with dimensions:', width, height);
                
                // Create lightweight-charts instance
                this.chart = LightweightCharts.createChart(container, {
                    layout: {
                        background: { type: 'solid', color: '#161b22' },
                        textColor: '#8b949e',
                    },
                    grid: {
                        vertLines: { color: '#21262d' },
                        horzLines: { color: '#21262d' },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                    },
                    rightPriceScale: {
                        borderColor: '#30363d',
                        textColor: '#8b949e',
                    },
                    timeScale: {
                        borderColor: '#30363d',
                        textColor: '#8b949e',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                    width: width,
                    height: height,
                });
                
                // Prepare candlestick data - lightweight-charts needs Unix timestamp in seconds
                const candlestickData = data.map(d => {
                    const date = new Date(d.time);
                    return {
                        time: Math.floor(date.getTime() / 1000), // Convert to Unix timestamp in seconds
                        open: parseFloat(d.open),
                        high: parseFloat(d.high),
                        low: parseFloat(d.low),
                        close: parseFloat(d.close),
                    };
                }).filter(d => !isNaN(d.time) && !isNaN(d.open) && !isNaN(d.high) && !isNaN(d.low) && !isNaN(d.close));
                
                console.log('Candlestick data points:', candlestickData.length);
                
                if (candlestickData.length === 0) {
                    container.innerHTML = '<div class="empty-message">Invalid chart data</div>';
                    return;
                }
                
                // Create candlestick series
                this.candlestickSeries = this.chart.addCandlestickSeries({
                    upColor: '#238636',
                    downColor: '#da3633',
                    borderVisible: false,
                    wickUpColor: '#238636',
                    wickDownColor: '#da3633',
                });
                
                // Set data
                this.candlestickSeries.setData(candlestickData);
                
                // Fit content
                this.chart.timeScale().fitContent();
                
                // Handle resize
                if (window.ResizeObserver) {
                    const resizeObserver = new ResizeObserver(entries => {
                        if (entries.length > 0 && this.chart) {
                            const { width, height } = entries[0].contentRect;
                            this.chart.applyOptions({ width, height });
                        }
                    });
                    resizeObserver.observe(container);
                } else {
                    // Fallback for browsers without ResizeObserver
                    window.addEventListener('resize', () => {
                        if (this.chart && container) {
                            this.chart.applyOptions({ 
                                width: container.clientWidth, 
                                height: container.clientHeight 
                            });
                        }
                    });
                }
            }, 100); // Small delay to ensure container is laid out
        } catch (error) {
            console.error('Error rendering chart:', error);
            container.innerHTML = `<div class="empty-message">Error loading chart: ${error.message}</div>`;
        }
    }
    
    updateTradeInfo() {
        // This would need portfolio data to show max affordable shares
        // For now, we'll update this when portfolio loads
        this.loadPortfolio().then(() => {
            // Update buy/sell info after portfolio loads
        });
    }
    
    async buyStock() {
        if (!this.currentSymbol) {
            this.showToast('Please search for a stock first', 'error');
            return;
        }
        
        const quantity = parseInt(document.getElementById('buy-quantity').value);
        if (!quantity || quantity <= 0) {
            this.showToast('Please enter a valid quantity', 'error');
            return;
        }
        
        const result = await this.apiCall('trade/buy', 'POST', {
            symbol: this.currentSymbol,
            quantity: quantity
        });
        
        if (result.success) {
            this.showToast(`Bought ${quantity} shares of ${this.currentSymbol} at $${result.price.toFixed(2)}`, 'success');
            document.getElementById('buy-quantity').value = '';
            this.loadPortfolio();
            this.loadHistory();
            this.updateTradeInfo();
        } else {
            this.showToast(result.error, 'error');
        }
    }
    
    async sellStock() {
        if (!this.currentSymbol) {
            this.showToast('Please search for a stock first', 'error');
            return;
        }
        
        const quantity = parseInt(document.getElementById('sell-quantity').value);
        if (!quantity || quantity <= 0) {
            this.showToast('Please enter a valid quantity', 'error');
            return;
        }
        
        const result = await this.apiCall('trade/sell', 'POST', {
            symbol: this.currentSymbol,
            quantity: quantity
        });
        
        if (result.success) {
            this.showToast(`Sold ${quantity} shares of ${this.currentSymbol} at $${result.price.toFixed(2)}`, 'success');
            document.getElementById('sell-quantity').value = '';
            this.loadPortfolio();
            this.loadHistory();
            this.updateTradeInfo();
        } else {
            this.showToast(result.error, 'error');
        }
    }
    
    async loadHistory() {
        const result = await this.apiCall('history');
        if (result.success) {
            this.updateHistory(result.data);
        }
    }
    
    updateHistory(history) {
        const container = document.getElementById('history-list');
        container.innerHTML = '';
        
        if (history.length === 0) {
            container.innerHTML = '<div class="empty-message">No trades yet</div>';
            return;
        }
        
        // Show most recent first
        history.reverse().forEach(trade => {
            const date = new Date(trade.timestamp);
            const action = trade.action.toUpperCase();
            const actionColor = action === 'BUY' ? '#238636' : '#da3633';
            
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                ${date.toLocaleString()} | 
                <span style="color: ${actionColor}">${action}</span> | 
                ${trade.symbol} | 
                ${trade.quantity} @ $${trade.price.toFixed(2)} = 
                $${trade.total_cost.toFixed(2)}
            `;
            container.appendChild(item);
        });
    }
    
    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing interval
        
        if (this.currentSymbol && this.autoRefreshEnabled) {
            this.autoRefreshInterval = setInterval(() => {
                this.manualRefresh();
            }, 3000); // 3 seconds
        }
    }
    
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
    
    async manualRefresh() {
        if (this.currentSymbol) {
            // Refresh stock info
            const result = await this.apiCall('stock/search', 'POST', { symbol: this.currentSymbol });
            if (result.success) {
                this.currentPrice = result.data.current_price;
                document.getElementById('stock-price').textContent = `$${result.data.current_price.toFixed(2)}`;
            }
            
            // Refresh chart
            this.loadChart();
            
            // Refresh portfolio
            this.loadPortfolio();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tradingApp = new TradingApp();
});

