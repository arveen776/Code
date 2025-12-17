// Global state
let currentSymbol = '';
let currentTimeframe = '1D';
let currentChart = null;
let stockData = [];
let isHistoricalView = false;
let historicalDate = null;
let socket = null;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing app...');
    initializeSocket();
    await loadSymbols();
    await loadPortfolio();
    setupEventListeners();
    updateHeader();
    
    // Load default stock (AAPL) on startup so user sees a chart immediately
    console.log('📊 Loading default stock: AAPL');
    currentSymbol = 'AAPL';
    document.getElementById('chartSymbol').value = 'AAPL';
    await updateHeader();
    await loadChartData();
    if (socket) {
        socket.emit('subscribe', currentSymbol);
    }
});

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server for real-time updates');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
    
    // Listen for real-time price updates
    socket.on('priceUpdate', (data) => {
        if (data.symbol && currentSymbol && data.symbol.toUpperCase() === currentSymbol.toUpperCase()) {
            if (data.price && !isNaN(data.price) && data.price > 0) {
                updateCurrentPrice(data.price);
                updateHeaderPrice(data.price);
                // Update chart if showing live data
                if (!isHistoricalView && currentChart && stockData && stockData.length > 0) {
                    updateChartWithNewPrice(data.price);
                }
            }
        }
    });
}

// Update header with symbol info
async function updateHeader() {
    if (currentSymbol) {
        document.getElementById('headerSymbol').textContent = currentSymbol;
        const price = await getCurrentPrice(currentSymbol);
        if (price) {
            updateHeaderPrice(price);
        }
    } else {
        document.getElementById('headerSymbol').textContent = '--';
        document.getElementById('headerPrice').textContent = '$0.00';
        document.getElementById('headerChange').textContent = '+0.00 (0.00%)';
        document.getElementById('headerChange').className = 'change-display';
    }
}

// Update header price display
function updateHeaderPrice(price) {
    if (!stockData || stockData.length === 0) return;
    
    const latest = stockData[stockData.length - 1];
    const previous = stockData.length > 1 ? stockData[stockData.length - 2] : latest;
    
    const change = price - previous.close;
    const changePercent = ((change / previous.close) * 100).toFixed(2);
    
    document.getElementById('headerPrice').textContent = `$${price.toFixed(2)}`;
    
    const changeEl = document.getElementById('headerChange');
    if (change >= 0) {
        changeEl.textContent = `+$${change.toFixed(2)} (+${changePercent}%)`;
        changeEl.className = 'change-display positive';
    } else {
        changeEl.textContent = `$${change.toFixed(2)} (${changePercent}%)`;
        changeEl.className = 'change-display negative';
    }
}

// Search stocks
let searchTimeout = null;
let currentSearchResults = [];

async function searchStocks(query, resultContainer) {
    if (!query || query.trim().length < 1) {
        resultContainer.classList.remove('show');
        return;
    }

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        currentSearchResults = results;
        displaySearchResults(results, resultContainer);
    } catch (error) {
        console.error('Error searching stocks:', error);
        resultContainer.classList.remove('show');
    }
}

function displaySearchResults(results, container) {
    container.innerHTML = '';
    
    if (results.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'search-result-item';
        noResults.textContent = 'No results found';
        noResults.style.color = 'var(--text-muted)';
        container.appendChild(noResults);
    } else {
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <div class="symbol">${result.symbol}</div>
                <div class="name">${result.name}</div>
                <div class="exchange">${result.exchange}</div>
            `;
            item.addEventListener('click', () => {
                selectSymbol(result.symbol, container);
            });
            container.appendChild(item);
        });
    }
    
    container.classList.add('show');
}

async function selectSymbol(symbol, resultContainer) {
    // Find which input triggered this
    const chartInput = document.getElementById('chartSymbol');
    const tradeInput = document.getElementById('symbolSelect');
    
    if (resultContainer.id === 'searchResults') {
        // Unsubscribe from previous symbol
        if (currentSymbol && socket) {
            socket.emit('unsubscribe', currentSymbol);
        }
        
        chartInput.value = symbol;
        currentSymbol = symbol;
        await updateHeader();
        await loadChartData();
        // Subscribe to real-time updates
        if (socket) {
            socket.emit('subscribe', currentSymbol);
        }
        // Update trade form price
        const price = await getCurrentPrice(symbol);
        if (price) {
            document.getElementById('currentPrice').textContent = `$${price.toFixed(2)}`;
        }
    } else if (resultContainer.id === 'tradeSearchResults') {
        tradeInput.value = symbol;
        const price = await getCurrentPrice(symbol);
        if (price) {
            document.getElementById('currentPrice').textContent = `$${price.toFixed(2)}`;
            updateTradeTotal();
        }
    }
    
    resultContainer.classList.remove('show');
}

// Load available symbols (for reference, not used in UI anymore)
async function loadSymbols() {
    // This function is kept for compatibility but symbols are now searched dynamically
}

// Load portfolio data
async function loadPortfolio() {
    try {
        const response = await fetch('/api/portfolio');
        const portfolio = await response.json();
        
        const cash = portfolio.cash.toFixed(2);
        document.getElementById('cash').textContent = `$${cash}`;
        document.getElementById('headerCash').textContent = `$${cash}`;
        
        // Calculate total value
        let totalValue = portfolio.cash;
        const holdingsList = document.getElementById('holdingsList');
        holdingsList.innerHTML = '';
        
        if (Object.keys(portfolio.holdings).length === 0) {
            holdingsList.innerHTML = '<div class="holdings-empty">No holdings</div>';
        } else {
            for (const [symbol, quantity] of Object.entries(portfolio.holdings)) {
                const price = await getCurrentPrice(symbol);
                const value = quantity * price;
                totalValue += value;
                
                const holdingItem = document.createElement('div');
                holdingItem.className = 'holdings-item';
                holdingItem.innerHTML = `
                    <span><strong>${symbol}</strong>: ${quantity} shares</span>
                    <span>$${value.toFixed(2)}</span>
                `;
                holdingsList.appendChild(holdingItem);
            }
        }
        
        const total = totalValue.toFixed(2);
        document.getElementById('totalValue').textContent = `$${total}`;
        document.getElementById('headerTotal').textContent = `$${total}`;
    } catch (error) {
        console.error('Error loading portfolio:', error);
    }
}

// Get current price for a symbol
async function getCurrentPrice(symbol) {
    if (!symbol || symbol.trim().length === 0) {
        return 0;
    }
    
    try {
        const response = await fetch(`/api/stock/${symbol.toUpperCase()}/price`);
        if (response.ok) {
            const data = await response.json();
            if (data.price && !isNaN(data.price)) {
                return data.price;
            }
        }
        // Fallback to latest close price from chart data
        const chartResponse = await fetch(`/api/stock/${symbol.toUpperCase()}?timeframe=1D&days=1`);
        if (chartResponse.ok) {
            const chartData = await chartResponse.json();
            if (chartData.data && chartData.data.length > 0) {
                const lastPrice = chartData.data[chartData.data.length - 1].close;
                if (!isNaN(lastPrice)) {
                    return lastPrice;
                }
            }
        }
    } catch (error) {
        console.error('Error getting current price:', error);
    }
    return 0;
}

// Update current price display
function updateCurrentPrice(price) {
    const tradeSymbol = document.getElementById('symbolSelect').value.trim().toUpperCase();
    if (tradeSymbol && tradeSymbol === currentSymbol) {
        document.getElementById('currentPrice').textContent = `$${price.toFixed(2)}`;
        updateTradeTotal();
    }
}

// Update chart with new real-time price
function updateChartWithNewPrice(price) {
    if (!currentChart || !stockData || stockData.length === 0) return;
    
    const today = new Date().toISOString().split('T')[0];
    const now = new Date();
    const lastDataPoint = stockData[stockData.length - 1];
    
    // Update last data point if it's today
    if (lastDataPoint.date === today || !lastDataPoint.date) {
        lastDataPoint.close = price;
        if (price > lastDataPoint.high) lastDataPoint.high = price;
        if (price < lastDataPoint.low) lastDataPoint.low = price;
        
        // Update candlestick data
        const dataset = currentChart.data.datasets[0];
        const lastIndex = dataset.data.length - 1;
        if (lastIndex >= 0) {
            // Update the existing data point
            dataset.data[lastIndex] = {
                x: dataset.data[lastIndex].x,
                o: lastDataPoint.open,
                h: lastDataPoint.high,
                l: lastDataPoint.low,
                c: lastDataPoint.close
            };
            // Use 'none' mode for smooth updates without animation
            currentChart.update('none');
        } else {
            // If no data point exists, add a new one
            dataset.data.push({
                x: now,
                o: price,
                h: price,
                l: price,
                c: price
            });
            currentChart.update('none');
        }
    } else {
        // If it's a new day, add a new data point
        const dataset = currentChart.data.datasets[0];
        dataset.data.push({
            x: now,
            o: price,
            h: price,
            l: price,
            c: price
        });
        stockData.push({
            date: today,
            timestamp: now.getTime(),
            open: price,
            high: price,
            low: price,
            close: price,
            volume: 0
        });
        currentChart.update('none');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Chart symbol search
    const chartInput = document.getElementById('chartSymbol');
    const chartResults = document.getElementById('searchResults');
    
    chartInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        clearTimeout(searchTimeout);
        if (query.length >= 1) {
            searchTimeout = setTimeout(() => {
                searchStocks(query, chartResults);
            }, 300);
        } else {
            chartResults.classList.remove('show');
        }
    });
    
    chartInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && currentSearchResults.length > 0) {
            selectSymbol(currentSearchResults[0].symbol, chartResults);
        }
    });
    
    // Click outside to close search results
    document.addEventListener('click', (e) => {
        if (!chartInput.contains(e.target) && !chartResults.contains(e.target)) {
            chartResults.classList.remove('show');
        }
        if (!document.getElementById('symbolSelect').contains(e.target) && 
            !document.getElementById('tradeSearchResults').contains(e.target)) {
            document.getElementById('tradeSearchResults').classList.remove('show');
        }
    });
    
    // Trade symbol search
    const tradeInput = document.getElementById('symbolSelect');
    const tradeResults = document.getElementById('tradeSearchResults');
    
    tradeInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        clearTimeout(searchTimeout);
        if (query.length >= 1) {
            searchTimeout = setTimeout(() => {
                searchStocks(query, tradeResults);
            }, 300);
        } else {
            tradeResults.classList.remove('show');
        }
    });
    
    tradeInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && currentSearchResults.length > 0) {
            selectSymbol(currentSearchResults[0].symbol, tradeResults);
        }
    });
    
    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentTimeframe = e.target.dataset.timeframe;
            isHistoricalView = false;
            historicalDate = null;
            document.getElementById('viewLiveBtn').classList.add('active');
            document.getElementById('viewHistoricalBtn').classList.remove('active');
            if (currentSymbol) {
                await loadChartData();
                // Fetch current price to keep header consistent
                const price = await getCurrentPrice(currentSymbol);
                if (price && price > 0) {
                    updateHeaderPrice(price);
                }
            }
        });
    });
    
    // Historical date view
    document.getElementById('viewHistoricalBtn').addEventListener('click', () => {
        const date = document.getElementById('historicalDate').value;
        if (date && currentSymbol) {
            isHistoricalView = true;
            historicalDate = date;
            document.getElementById('viewHistoricalBtn').classList.add('active');
            document.getElementById('viewLiveBtn').classList.remove('active');
            loadHistoricalData(date);
        }
    });
    
    // Live view
    document.getElementById('viewLiveBtn').addEventListener('click', () => {
        isHistoricalView = false;
        historicalDate = null;
        document.getElementById('viewLiveBtn').classList.add('active');
        document.getElementById('viewHistoricalBtn').classList.remove('active');
        if (currentSymbol) {
            loadChartData();
            // Subscribe to real-time updates
            if (socket) {
                socket.emit('subscribe', currentSymbol);
            }
        }
    });
    
    // Trade symbol is now handled by search input above
    
    // Quantity input
    document.getElementById('quantityInput').addEventListener('input', updateTradeTotal);
    
    // Buy/Sell buttons
    document.getElementById('buyBtn').addEventListener('click', () => executeTrade('buy'));
    document.getElementById('sellBtn').addEventListener('click', () => executeTrade('sell'));
}

// Update trade total
function updateTradeTotal() {
    const quantity = parseInt(document.getElementById('quantityInput').value) || 0;
    const priceText = document.getElementById('currentPrice').textContent.replace('$', '');
    const price = parseFloat(priceText) || 0;
    const total = quantity * price;
    document.getElementById('tradeTotal').textContent = `$${total.toFixed(2)}`;
}

// Load chart data
async function loadChartData() {
    if (!currentSymbol) return;
    
    try {
        // Unsubscribe from previous symbol
        if (socket && currentSymbol) {
            socket.emit('unsubscribe', currentSymbol);
        }
        
        const days = getDaysForTimeframe(currentTimeframe);
        const response = await fetch(`/api/stock/${currentSymbol}?timeframe=${currentTimeframe}&days=${days}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load data');
        }
        
        const result = await response.json();
        
        if (!result.data || result.data.length === 0) {
            console.warn('No data returned for symbol:', currentSymbol);
            // Show error message to user
            const canvas = document.getElementById('stockChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                if (currentChart) {
                    currentChart.destroy();
                    currentChart = null;
                }
                // Clear and show message
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#9aa0a6';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('No data available for ' + currentSymbol, canvas.width / 2, canvas.height / 2);
            }
            return;
        }
        
        console.log('✅ Received', result.data.length, 'data points for', currentSymbol);
        console.log('Sample data point:', result.data[0]);
        stockData = result.data;
        
        // Render the chart
        console.log('🔄 Rendering chart...');
        renderChart();
        
        // Update chart info
        updateChartInfo();
        
        // Always fetch current price separately to ensure consistency across timeframes
        if (currentSymbol && !isHistoricalView) {
            const currentPrice = await getCurrentPrice(currentSymbol);
            if (currentPrice && currentPrice > 0) {
                updateHeaderPrice(currentPrice);
            } else if (stockData.length > 0) {
                // Fallback to latest close from data if current price unavailable
                updateHeaderPrice(stockData[stockData.length - 1].close);
            }
        } else if (stockData.length > 0) {
            // For historical view, use latest close from data
            updateHeaderPrice(stockData[stockData.length - 1].close);
        }
        
        // Subscribe to real-time updates if viewing live data
        if (!isHistoricalView && socket) {
            socket.emit('subscribe', currentSymbol);
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        const canvas = document.getElementById('stockChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#f23645';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Error: ' + error.message, canvas.width / 2, canvas.height / 2);
        }
        alert('Error loading stock data: ' + error.message);
    }
}

// Load historical data for a specific date
async function loadHistoricalData(date) {
    if (!currentSymbol) return;
    
    try {
        // Get data up to the selected date
        const endDate = new Date(date);
        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - getDaysForTimeframe(currentTimeframe));
        
        const response = await fetch(`/api/stock/${currentSymbol}/history?startDate=${startDate.toISOString().split('T')[0]}&endDate=${endDate.toISOString().split('T')[0]}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load historical data');
        }
        
        const result = await response.json();
        
        // Filter to show only data up to the selected date
        stockData = result.data.filter(d => d.date <= date);
        renderChart();
        updateChartInfo();
        
        // Unsubscribe from real-time updates when viewing historical data
        if (socket) {
            socket.emit('unsubscribe', currentSymbol);
        }
    } catch (error) {
        console.error('Error loading historical data:', error);
        alert('Error loading historical data: ' + error.message);
    }
}

// Get days for timeframe
function getDaysForTimeframe(timeframe) {
    const daysMap = {
        '1': 1,      // 1 minute - get 1 day of data
        '5': 1,      // 5 minutes - get 1 day
        '15': 1,     // 15 minutes - get 1 day
        '30': 1,     // 30 minutes - get 1 day
        '60': 7,     // 1 hour - get 7 days
        '1D': 30,    // 1 day - get 30 days
        '1W': 90,    // 1 week - get 90 days
        '1M': 180,   // 1 month - get 180 days
        '3M': 365,   // 3 months - get 365 days
        '6M': 365,   // 6 months - get 365 days
        '1Y': 365    // 1 year - get 365 days
    };
    return daysMap[timeframe] || 365;
}

// Render simple line chart (guaranteed to work)
function renderChart() {
    const canvas = document.getElementById('stockChart');
    if (!canvas) {
        console.error('❌ Chart canvas element not found!');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('❌ Could not get 2D context from canvas');
        return;
    }
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js is not loaded!');
        ctx.fillStyle = '#f23645';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Chart.js library not loaded', canvas.width / 2 || 400, canvas.height / 2 || 200);
        return;
    }
    
    // Destroy previous chart if exists
    if (currentChart) {
        try {
            currentChart.destroy();
        } catch (err) {
            console.warn('Error destroying previous chart:', err);
        }
        currentChart = null;
    }
    
    if (!stockData || stockData.length === 0) {
        console.warn('No stock data to render');
        ctx.clearRect(0, 0, canvas.width || 800, canvas.height || 400);
        ctx.fillStyle = '#9aa0a6';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', (canvas.width || 800) / 2, (canvas.height || 400) / 2);
        return;
    }
    
    console.log('📊 Rendering chart with', stockData.length, 'data points');
    console.log('📊 Current timeframe:', currentTimeframe);
    console.log('📊 Current symbol:', currentSymbol);
    
    // Prepare simple line chart data - use close price
    const chartData = stockData.map((d, index) => {
        // Parse date
        let x;
        if (d.timestamp) {
            x = new Date(typeof d.timestamp === 'number' && d.timestamp < 10000000000 
                ? d.timestamp * 1000 
                : d.timestamp);
        } else if (d.date) {
            x = new Date(d.date);
        } else {
            x = new Date();
        }
        
        // Use close price for line chart
        const y = parseFloat(d.close);
        
        if (isNaN(y)) {
            console.warn('Invalid close price at index', index, d);
            return null;
        }
        
        return {
            x: x,
            y: y
        };
    }).filter(d => d !== null);
    
    if (chartData.length === 0) {
        console.warn('No valid chart data to render');
        return;
    }
    
    // Determine color based on price trend
    const firstPrice = chartData[0].y;
    const lastPrice = chartData[chartData.length - 1].y;
    const isUp = lastPrice >= firstPrice;
    const lineColor = isUp ? '#00d4aa' : '#f23645';
    
    console.log('✅ Creating line chart with', chartData.length, 'data points');
    console.log('📊 Sample data point:', chartData[0]);
    
    try {
        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: currentSymbol,
                    data: chartData,
                    borderColor: lineColor,
                    backgroundColor: lineColor + '20', // Add transparency
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0 // Disable animation for instant rendering
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            title: function(context) {
                                const point = chartData[context[0].dataIndex];
                                if (point && point.x) {
                                    return new Date(point.x).toLocaleString();
                                }
                                return '';
                            },
                            label: function(context) {
                                const point = stockData[context.dataIndex];
                                if (point) {
                                    return [
                                        `Open: $${point.open.toFixed(2)}`,
                                        `High: $${point.high.toFixed(2)}`,
                                        `Low: $${point.low.toFixed(2)}`,
                                        `Close: $${point.close.toFixed(2)}`
                                    ];
                                }
                                return `Price: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: getTimeUnit(),
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'MMM dd HH:mm',
                                day: 'MMM dd',
                                week: 'MMM dd',
                                month: 'MMM yyyy'
                            }
                        },
                        grid: {
                            color: 'rgba(45, 49, 66, 0.5)',
                            display: true
                        },
                        ticks: {
                            color: '#9aa0a6',
                            font: {
                                size: 11
                            },
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        position: 'right',
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(45, 49, 66, 0.5)',
                            display: true
                        },
                        ticks: {
                            color: '#9aa0a6',
                            font: {
                                size: 11
                            },
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        console.log('✅ Line chart created successfully!');
    } catch (error) {
        console.error('❌ Error creating chart:', error);
        console.error('Error details:', error.message);
        if (error.stack) console.error('Stack:', error.stack);
        
        // Show error on canvas
        ctx.clearRect(0, 0, canvas.width || 800, canvas.height || 400);
        ctx.fillStyle = '#f23645';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Error rendering chart: ' + error.message, (canvas.width || 800) / 2, (canvas.height || 400) / 2);
    }
}

// Custom candlestick chart renderer (Webull-style green/red candles)
function createCustomCandlestickChart(ctx, candlestickData) {
    if (!candlestickData || candlestickData.length === 0) {
        console.warn('No data for custom candlestick chart');
        return;
    }
    
    // Format data for Chart.js
    const formattedData = candlestickData.map(d => {
        const date = d.t instanceof Date ? d.t : new Date(d.t || d.x);
        return {
            x: date,
            o: d.o,
            h: d.h,
            l: d.l,
            c: d.c
        };
    });
    
    // Create a custom plugin to draw candlesticks
    const candlestickPluginId = 'customCandlestick' + Date.now();
    const candlestickPlugin = {
        id: candlestickPluginId,
        afterDatasetsDraw: (chart) => {
            try {
                const ctx = chart.ctx;
                const xScale = chart.scales.x;
                const yScale = chart.scales.y;
                
                if (!xScale || !yScale) {
                    console.warn('Scales not available for candlestick drawing');
                    return;
                }
                
                ctx.save();
                
                // Calculate candle width based on available space
                const chartWidth = xScale.width || (xScale.right - xScale.left);
                const candleWidth = Math.max(3, Math.min(10, (chartWidth / formattedData.length) * 0.5));
                
                formattedData.forEach((d, index) => {
                    try {
                        const x = xScale.getPixelForValue(d.x);
                        if (isNaN(x)) return;
                        
                        const openY = yScale.getPixelForValue(d.o);
                        const highY = yScale.getPixelForValue(d.h);
                        const lowY = yScale.getPixelForValue(d.l);
                        const closeY = yScale.getPixelForValue(d.c);
                        
                        if (isNaN(openY) || isNaN(highY) || isNaN(lowY) || isNaN(closeY)) {
                            return;
                        }
                        
                        const isUp = d.c >= d.o;
                        const bodyTop = Math.max(openY, closeY);
                        const bodyBottom = Math.min(openY, closeY);
                        const bodyHeight = Math.abs(closeY - openY);
                        
                        // Draw wick (high-low line)
                        ctx.strokeStyle = isUp ? '#00d4aa' : '#f23645';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(x, highY);
                        ctx.lineTo(x, lowY);
                        ctx.stroke();
                        
                        // Draw body (open-close rectangle)
                        ctx.fillStyle = isUp ? '#00d4aa' : '#f23645';
                        ctx.fillRect(x - candleWidth/2, bodyTop, candleWidth, Math.max(1, bodyHeight));
                        
                        // Draw body border
                        ctx.strokeStyle = isUp ? '#00b894' : '#d63031';
                        ctx.lineWidth = 1;
                        ctx.strokeRect(x - candleWidth/2, bodyTop, candleWidth, Math.max(1, bodyHeight));
                    } catch (err) {
                        console.warn('Error drawing candle at index', index, err);
                    }
                });
                
                ctx.restore();
            } catch (error) {
                console.error('Error in candlestick plugin:', error);
            }
        }
    };
    
    // Register plugin
    try {
        if (Chart.register) {
            Chart.register(candlestickPlugin);
        }
    } catch (err) {
        console.warn('Could not register candlestick plugin:', err);
    }
    
    // Create line chart as base (we'll draw candlesticks on top)
    console.log('🔄 Creating custom candlestick chart with', formattedData.length, 'data points');
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: currentSymbol,
                data: formattedData.map(d => ({ x: d.x, y: d.c })),
                borderColor: 'transparent',
                backgroundColor: 'transparent',
                pointRadius: 0,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        title: function(context) {
                            const d = formattedData[context[0].dataIndex];
                            return d ? new Date(d.x).toLocaleString() : '';
                        },
                        label: function(context) {
                            const d = formattedData[context.dataIndex];
                            if (d) {
                                return [
                                    `Open: $${d.o.toFixed(2)}`,
                                    `High: $${d.h.toFixed(2)}`,
                                    `Low: $${d.l.toFixed(2)}`,
                                    `Close: $${d.c.toFixed(2)}`
                                ];
                            }
                            return [];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(),
                        displayFormats: {
                            minute: 'HH:mm',
                            hour: 'MMM dd HH:mm',
                            day: 'MMM dd',
                            week: 'MMM dd',
                            month: 'MMM yyyy'
                        }
                    },
                    grid: {
                        color: 'rgba(45, 49, 66, 0.5)',
                        display: true
                    },
                    ticks: {
                        color: '#9aa0a6',
                        font: { size: 11 },
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    position: 'right',
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(45, 49, 66, 0.5)',
                        display: true
                    },
                    ticks: {
                        color: '#9aa0a6',
                        font: { size: 11 },
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        },
        plugins: [candlestickPlugin]
    });
    
    console.log('✅ Custom candlestick chart created successfully!');
    if (currentChart) {
        console.log('✅ Chart instance:', currentChart.id || 'created');
    }
}

// Fallback to line chart if candlestick is not available
function createLineChartFallback(ctx, candlestickData) {
    const lineData = candlestickData.map(d => ({
        x: d.x,
        y: d.c // Use close price for line chart
    }));
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: currentSymbol,
                data: lineData,
                borderColor: '#2962ff',
                backgroundColor: 'rgba(41, 98, 255, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = candlestickData[context.dataIndex];
                            if (point) {
                                return [
                                    `Open: $${point.o.toFixed(2)}`,
                                    `High: $${point.h.toFixed(2)}`,
                                    `Low: $${point.l.toFixed(2)}`,
                                    `Close: $${point.c.toFixed(2)}`
                                ];
                            }
                            return `Price: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(),
                        displayFormats: {
                            minute: 'HH:mm',
                            hour: 'MMM dd HH:mm',
                            day: 'MMM dd',
                            week: 'MMM dd',
                            month: 'MMM yyyy'
                        }
                    },
                    grid: {
                        color: 'rgba(45, 49, 66, 0.5)'
                    },
                    ticks: {
                        color: '#9aa0a6',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    position: 'right',
                    grid: {
                        color: 'rgba(45, 49, 66, 0.5)'
                    },
                    ticks: {
                        color: '#9aa0a6',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Get time unit for x-axis based on timeframe
function getTimeUnit() {
    if (['1', '5', '15', '30'].includes(currentTimeframe)) {
        return 'minute';
    } else if (currentTimeframe === '60') {
        return 'hour';
    } else if (currentTimeframe === '1D') {
        return 'day';
    } else if (currentTimeframe === '1W') {
        return 'week';
    } else {
        return 'day';
    }
}

// Update chart info
function updateChartInfo() {
    if (stockData.length === 0) return;
    
    const latest = stockData[stockData.length - 1];
    const first = stockData[0];
    const change = latest.close - first.open;
    const changePercent = ((change / first.open) * 100).toFixed(2);
    const dayChange = latest.close - latest.open;
    const dayChangePercent = ((dayChange / latest.open) * 100).toFixed(2);
    
    const infoDiv = document.getElementById('chartInfo');
    infoDiv.innerHTML = `
        <div class="info-badge">
            <strong>Open</strong>
            <span>$${latest.open.toFixed(2)}</span>
        </div>
        <div class="info-badge">
            <strong>High</strong>
            <span style="color: var(--green)">$${latest.high.toFixed(2)}</span>
        </div>
        <div class="info-badge">
            <strong>Low</strong>
            <span style="color: var(--red)">$${latest.low.toFixed(2)}</span>
        </div>
        <div class="info-badge">
            <strong>Close</strong>
            <span>$${latest.close.toFixed(2)}</span>
        </div>
        <div class="info-badge">
            <strong>Change</strong>
            <span style="color: ${dayChange >= 0 ? 'var(--green)' : 'var(--red)'}">
                ${dayChange >= 0 ? '+' : ''}$${dayChange.toFixed(2)} (${dayChangePercent >= 0 ? '+' : ''}${dayChangePercent}%)
            </span>
        </div>
        <div class="info-badge">
            <strong>Period Change</strong>
            <span style="color: ${change >= 0 ? 'var(--green)' : 'var(--red)'}">
                ${change >= 0 ? '+' : ''}$${change.toFixed(2)} (${changePercent >= 0 ? '+' : ''}${changePercent}%)
            </span>
        </div>
        <div class="info-badge">
            <strong>Volume</strong>
            <span>${latest.volume.toLocaleString()}</span>
        </div>
    `;
}

// Execute trade
async function executeTrade(action) {
    const symbol = document.getElementById('symbolSelect').value.trim().toUpperCase();
    const quantity = parseInt(document.getElementById('quantityInput').value);
    const priceText = document.getElementById('currentPrice').textContent.replace('$', '').replace(',', '');
    const price = parseFloat(priceText);
    
    if (!symbol || symbol.length === 0) {
        alert('Please enter a stock symbol');
        return;
    }
    
    if (!quantity || quantity <= 0 || isNaN(quantity)) {
        alert('Please enter a valid quantity');
        return;
    }
    
    if (!price || isNaN(price) || price <= 0) {
        alert('Please wait for price to load');
        return;
    }
    
    try {
        const response = await fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol,
                action,
                quantity,
                price
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            alert(error.error || 'Trade failed');
            return;
        }
        
        await loadPortfolio();
        document.getElementById('quantityInput').value = '';
        document.getElementById('tradeTotal').textContent = '$0.00';
        alert(`${action.toUpperCase()} order executed successfully!`);
    } catch (error) {
        console.error('Error executing trade:', error);
        alert('Error executing trade');
    }
}
