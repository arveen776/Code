"""
Modern GUI interface for the stock trading simulator with Webull-like design.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
import yfinance as yf
from trading_simulator import TradingSimulator


class TradingSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Trading Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0e27')
        
        # Enhanced color scheme (modern dark theme)
        self.colors = {
            'bg': '#0d1117',  # Deeper, richer background
            'panel': '#161b22',  # Slightly lighter panel
            'panel_highlight': '#1c2128',  # Subtle highlight for panels
            'border': '#30363d',  # Better contrast border
            'border_light': '#21262d',  # Lighter border for subtle separation
            'text': '#e6edf3',  # Softer, more readable text
            'text_secondary': '#8b949e',  # Better secondary text
            'text_muted': '#6e7681',  # Muted text for labels
            'green': '#238636',  # More vibrant green
            'green_hover': '#2ea043',
            'red': '#da3633',  # Better red
            'red_hover': '#f85149',
            'blue': '#1f6feb',  # Modern blue
            'blue_hover': '#388bfd',
            'hover': '#21262d',  # Better hover state
            'accent': '#f78166'  # Accent color for highlights
        }
        
        # Initialize simulator
        self.simulator = TradingSimulator(10000.0)
        self.current_symbol = None
        self.current_price = None
        self.current_timeframe = ('1d', '5m')  # Default timeframe (period, interval) - 1 day, 5 min intervals
        self.auto_refresh = True  # Auto-refresh enabled by default
        self.refresh_interval = 3000  # 3 seconds in milliseconds
        self.refresh_job = None  # Store refresh job ID
        
        # Configure style
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Initial portfolio update
        self.update_portfolio()
        
        # Start auto-refresh if enabled
        self.start_auto_refresh()
    
    def setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Dark.TFrame', background=self.colors['panel'], borderwidth=1)
        style.configure('Border.TFrame', background=self.colors['border'])
        
        # Configure label styles
        style.configure('Dark.TLabel', background=self.colors['panel'], foreground=self.colors['text'])
        style.configure('Title.TLabel', background=self.colors['panel'], foreground=self.colors['text'], 
                       font=('Segoe UI', 14, 'bold'))
        style.configure('Price.TLabel', background=self.colors['panel'], foreground=self.colors['text'], 
                       font=('Segoe UI', 20, 'bold'))
        style.configure('Secondary.TLabel', background=self.colors['panel'], foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 10))
        
        # Configure button styles
        style.configure('Buy.TButton', background=self.colors['green'], foreground='white',
                       font=('Segoe UI', 11, 'bold'))
        style.map('Buy.TButton', background=[('active', '#1e8e82')])
        
        style.configure('Sell.TButton', background=self.colors['red'], foreground='white',
                       font=('Segoe UI', 11, 'bold'))
        style.map('Sell.TButton', background=[('active', '#d32f2f')])
        
        style.configure('Dark.TButton', background=self.colors['border'], foreground=self.colors['text'],
                       font=('Segoe UI', 10))
        style.map('Dark.TButton', background=[('active', self.colors['hover'])])
        
        # Configure entry styles
        style.configure('Dark.TEntry', fieldbackground=self.colors['border'], foreground=self.colors['text'],
                       borderwidth=1, relief='solid')
    
    def create_layout(self):
        """Create the main layout with sidebar and main content area."""
        # Left sidebar (Portfolio & Holdings)
        sidebar = tk.Frame(self.root, bg=self.colors['bg'], width=320)
        sidebar.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 8), pady=10)
        sidebar.pack_propagate(False)
        
        self.create_portfolio_section(sidebar)
        self.create_holdings_section(sidebar)
        
        # Main content area
        main_area = tk.Frame(self.root, bg=self.colors['bg'])
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        # Top bar (Stock search and info)
        self.create_search_bar(main_area)
        
        # Chart area
        self.create_chart_section(main_area)
        
        # Trading panel (bottom)
        self.create_trading_panel(main_area)
        
        # Trade history (right side or bottom)
        self.create_history_section(main_area)
    
    def create_portfolio_section(self, parent):
        """Create portfolio summary in sidebar."""
        portfolio_frame = tk.Frame(parent, bg=self.colors['panel'], relief=tk.FLAT)
        portfolio_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Inner padding frame
        inner_frame = tk.Frame(portfolio_frame, bg=self.colors['panel'])
        inner_frame.pack(fill=tk.X, padx=18, pady=18)
        
        # Title with subtle styling
        title_label = tk.Label(inner_frame, text="Portfolio Value", 
                              bg=self.colors['panel'], fg=self.colors['text_muted'],
                              font=('Segoe UI', 10, 'normal'))
        title_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Large portfolio value
        self.total_value_label = tk.Label(inner_frame, text="$10,000.00", 
                                          bg=self.colors['panel'], fg=self.colors['text'],
                                          font=('Segoe UI', 24, 'bold'))
        self.total_value_label.pack(anchor=tk.W, pady=(0, 16))
        
        # Stats with better spacing
        stats_frame = tk.Frame(inner_frame, bg=self.colors['panel'])
        stats_frame.pack(fill=tk.X)
        
        # Cash row
        cash_row = tk.Frame(stats_frame, bg=self.colors['panel'])
        cash_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(cash_row, text="Cash", bg=self.colors['panel'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.cash_label = tk.Label(cash_row, text="$10,000.00", bg=self.colors['panel'],
                                   fg=self.colors['text'], font=('Segoe UI', 10, 'bold'))
        self.cash_label.pack(side=tk.RIGHT)
        
        # Holdings value row
        holdings_row = tk.Frame(stats_frame, bg=self.colors['panel'])
        holdings_row.pack(fill=tk.X)
        tk.Label(holdings_row, text="Holdings", bg=self.colors['panel'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        self.holdings_value_label = tk.Label(holdings_row, text="$0.00", bg=self.colors['panel'],
                                            fg=self.colors['text'], font=('Segoe UI', 10, 'bold'))
        self.holdings_value_label.pack(side=tk.RIGHT)
    
    def create_holdings_section(self, parent):
        """Create holdings list in sidebar."""
        holdings_frame = tk.Frame(parent, bg=self.colors['panel'], relief=tk.FLAT)
        holdings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = tk.Frame(holdings_frame, bg=self.colors['panel'])
        title_frame.pack(fill=tk.X, padx=18, pady=(0, 12))
        tk.Label(title_frame, text="Holdings", bg=self.colors['panel'], fg=self.colors['text_muted'],
                font=('Segoe UI', 10, 'normal')).pack(anchor=tk.W)
        
        # Treeview for holdings
        tree_frame = tk.Frame(holdings_frame, bg=self.colors['panel'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))
        
        # Create treeview with custom style
        style = ttk.Style()
        style.configure("Holdings.Treeview", background=self.colors['panel_highlight'], 
                       foreground=self.colors['text'], fieldbackground=self.colors['panel_highlight'], 
                       borderwidth=0, rowheight=28)
        style.configure("Holdings.Treeview.Heading", background=self.colors['panel_highlight'], 
                       foreground=self.colors['text_secondary'], borderwidth=0, relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        style.map("Holdings.Treeview", background=[('selected', self.colors['hover'])])
        
        columns = ('Symbol', 'Shares', 'Price', 'Value')
        self.holdings_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                         style="Holdings.Treeview", height=15)
        
        for col in columns:
            self.holdings_tree.heading(col, text=col.upper())
            if col == 'Symbol':
                self.holdings_tree.column(col, width=70, anchor=tk.W)
            else:
                self.holdings_tree.column(col, width=65, anchor=tk.E)
        
        scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.holdings_tree.yview,
                                bg=self.colors['panel'], troughcolor=self.colors['panel'],
                                activebackground=self.colors['border'], width=12)
        self.holdings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.holdings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_search_bar(self, parent):
        """Create stock search bar at top."""
        search_frame = tk.Frame(parent, bg=self.colors['panel'], height=75)
        search_frame.pack(fill=tk.X, pady=(0, 8))
        search_frame.pack_propagate(False)
        
        content_frame = tk.Frame(search_frame, bg=self.colors['panel'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        
        # Search section with better styling
        search_section = tk.Frame(content_frame, bg=self.colors['panel'])
        search_section.pack(side=tk.LEFT)
        
        search_label = tk.Label(search_section, text="Symbol", bg=self.colors['panel'], 
                               fg=self.colors['text_secondary'], font=('Segoe UI', 9))
        search_label.pack(anchor=tk.W, pady=(0, 4))
        
        search_input_frame = tk.Frame(search_section, bg=self.colors['border'], relief=tk.FLAT)
        search_input_frame.pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_input_frame, bg=self.colors['panel_highlight'], 
                                     fg=self.colors['text'], insertbackground=self.colors['text'],
                                     font=('Segoe UI', 11), width=14, relief=tk.FLAT, bd=0)
        self.search_entry.pack(padx=12, pady=8)
        self.search_entry.bind('<Return>', lambda e: self.search_stock())
        self.search_entry.focus_set()
        
        search_btn = tk.Button(search_section, text="Search", command=self.search_stock,
                              bg=self.colors['blue'], fg='white', font=('Segoe UI', 10, 'bold'),
                              relief=tk.FLAT, padx=24, pady=8, cursor='hand2',
                              activebackground=self.colors['blue_hover'])
        search_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        # Stock info display with better layout
        info_frame = tk.Frame(content_frame, bg=self.colors['panel'])
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(32, 0))
        
        info_inner = tk.Frame(info_frame, bg=self.colors['panel'])
        info_inner.pack(side=tk.RIGHT)
        
        self.stock_name_label = tk.Label(info_inner, text="", bg=self.colors['panel'], 
                                         fg=self.colors['text'], font=('Segoe UI', 13, 'bold'))
        self.stock_name_label.pack(side=tk.LEFT, padx=(0, 16))
        
        self.stock_price_label = tk.Label(info_inner, text="", bg=self.colors['panel'], 
                                          fg=self.colors['text'], font=('Segoe UI', 20, 'bold'))
        self.stock_price_label.pack(side=tk.LEFT)
    
    def create_chart_section(self, parent):
        """Create chart display area with timeframe selector."""
        chart_container = tk.Frame(parent, bg=self.colors['bg'])
        chart_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Chart header with timeframe buttons
        chart_header = tk.Frame(chart_container, bg=self.colors['panel'], height=52)
        chart_header.pack(fill=tk.X, pady=(0, 8))
        chart_header.pack_propagate(False)
        
        header_content = tk.Frame(chart_header, bg=self.colors['panel'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        # Timeframe buttons
        timeframe_frame = tk.Frame(header_content, bg=self.colors['panel'])
        timeframe_frame.pack(side=tk.LEFT)
        
        tk.Label(timeframe_frame, text="Timeframe", bg=self.colors['panel'], 
                fg=self.colors['text_secondary'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 12))
        
        # Timeframe options: (button_text, period, interval) - Intraday timeframes
        timeframes = [
            ('1m', '1d', '1m'),   # 1 minute
            ('5m', '1d', '5m'),   # 5 minutes
            ('10m', '5d', '10m'), # 10 minutes
            ('30m', '60d', '30m') # 30 minutes
        ]
        
        self.timeframe_buttons = {}
        for btn_text, period, interval in timeframes:
            btn = tk.Button(timeframe_frame, text=btn_text, bg=self.colors['panel_highlight'],
                           fg=self.colors['text'], font=('Segoe UI', 9),
                           relief=tk.FLAT, padx=14, pady=6, cursor='hand2',
                           command=lambda p=period, i=interval, t=btn_text: self.set_timeframe(p, i, t),
                           activebackground=self.colors['hover'])
            btn.pack(side=tk.LEFT, padx=2)
            self.timeframe_buttons[btn_text] = btn
        
        # Highlight default timeframe (5m)
        self.highlight_timeframe_button('5m')
        
        # Refresh button
        refresh_frame = tk.Frame(header_content, bg=self.colors['panel'])
        refresh_frame.pack(side=tk.RIGHT)
        
        self.refresh_btn = tk.Button(refresh_frame, text="🔄 Refresh", 
                                     bg=self.colors['blue'], fg='white',
                                     font=('Segoe UI', 9, 'bold'),
                                     relief=tk.FLAT, padx=18, pady=6, cursor='hand2',
                                     command=self.manual_refresh,
                                     activebackground=self.colors['blue_hover'])
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_check = tk.Checkbutton(refresh_frame, text="Auto-refresh",
                                           variable=self.auto_refresh_var,
                                           bg=self.colors['panel'], fg=self.colors['text'],
                                           selectcolor=self.colors['panel_highlight'],
                                           activebackground=self.colors['panel'],
                                           activeforeground=self.colors['text'],
                                           font=('Segoe UI', 9),
                                           command=self.toggle_auto_refresh)
        auto_refresh_check.pack(side=tk.LEFT)
        
        # Chart area
        chart_frame = tk.Frame(chart_container, bg=self.colors['panel'], height=400)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 6), facecolor=self.colors['panel'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['panel'])
        self.ax.tick_params(colors=self.colors['text_secondary'])
        self.ax.spines['bottom'].set_color(self.colors['text_secondary'])
        self.ax.spines['top'].set_color(self.colors['text_secondary'])
        self.ax.spines['right'].set_color(self.colors['text_secondary'])
        self.ax.spines['left'].set_color(self.colors['text_secondary'])
        self.fig.patch.set_facecolor(self.colors['panel'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar for zoom/pan/home controls
        toolbar_frame = tk.Frame(chart_frame, bg=self.colors['panel'], height=30)
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.config(bg=self.colors['panel'])
        self.toolbar.update()
        
        # Enable interactive features
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        
        # Store chart data for interaction
        self.chart_data = None
        self.chart_dates = None
        self.chart_opens = None
        self.chart_highs = None
        self.chart_lows = None
        self.chart_closes = None
        
        # Crosshair lines
        self.crosshair_vline = None
        self.crosshair_hline = None
        
        # Tooltip annotation
        self.tooltip_annotation = None
        
        # Initial empty chart
        self.ax.text(0.5, 0.5, 'Search for a stock to view chart', 
                    ha='center', va='center', transform=self.ax.transAxes,
                    color=self.colors['text_secondary'], fontsize=14)
        self.canvas.draw()
    
    def create_trading_panel(self, parent):
        """Create buy/sell trading panel."""
        trading_frame = tk.Frame(parent, bg=self.colors['panel'], height=180)
        trading_frame.pack(fill=tk.X, pady=(0, 8))
        trading_frame.pack_propagate(False)
        
        # Main container
        container = tk.Frame(trading_frame, bg=self.colors['panel'])
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        
        # Buy section
        buy_frame = tk.Frame(container, bg=self.colors['panel_highlight'], relief=tk.FLAT)
        buy_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        buy_inner = tk.Frame(buy_frame, bg=self.colors['panel_highlight'], padx=20, pady=18)
        buy_inner.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(buy_inner, text="BUY", bg=self.colors['panel_highlight'], fg=self.colors['green'],
                font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 12))
        
        form_frame = tk.Frame(buy_inner, bg=self.colors['panel_highlight'])
        form_frame.pack(fill=tk.X)
        
        tk.Label(form_frame, text="Quantity", bg=self.colors['panel_highlight'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 6))
        
        entry_frame = tk.Frame(form_frame, bg=self.colors['border'], relief=tk.FLAT)
        entry_frame.grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=(0, 8))
        
        self.buy_quantity_entry = tk.Entry(entry_frame, bg=self.colors['panel'], fg=self.colors['text'],
                                           insertbackground=self.colors['text'], font=('Segoe UI', 11),
                                           width=14, relief=tk.FLAT, bd=0)
        self.buy_quantity_entry.pack(padx=10, pady=8)
        
        buy_btn = tk.Button(form_frame, text="BUY", command=self.buy_stock,
                           bg=self.colors['green'], fg='white', font=('Segoe UI', 11, 'bold'),
                           relief=tk.FLAT, padx=32, pady=10, cursor='hand2',
                           activebackground=self.colors['green_hover'])
        buy_btn.grid(row=1, column=1, padx=(0, 0))
        
        self.buy_info_label = tk.Label(form_frame, text="", bg=self.colors['panel_highlight'], 
                                       fg=self.colors['text_secondary'], font=('Segoe UI', 8))
        self.buy_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))
        
        # Sell section
        sell_frame = tk.Frame(container, bg=self.colors['panel_highlight'], relief=tk.FLAT)
        sell_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        sell_inner = tk.Frame(sell_frame, bg=self.colors['panel_highlight'], padx=20, pady=18)
        sell_inner.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(sell_inner, text="SELL", bg=self.colors['panel_highlight'], fg=self.colors['red'],
                font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 12))
        
        form_frame2 = tk.Frame(sell_inner, bg=self.colors['panel_highlight'])
        form_frame2.pack(fill=tk.X)
        
        tk.Label(form_frame2, text="Quantity", bg=self.colors['panel_highlight'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 6))
        
        entry_frame2 = tk.Frame(form_frame2, bg=self.colors['border'], relief=tk.FLAT)
        entry_frame2.grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=(0, 8))
        
        self.sell_quantity_entry = tk.Entry(entry_frame2, bg=self.colors['panel'], fg=self.colors['text'],
                                            insertbackground=self.colors['text'], font=('Segoe UI', 11),
                                            width=14, relief=tk.FLAT, bd=0)
        self.sell_quantity_entry.pack(padx=10, pady=8)
        
        sell_btn = tk.Button(form_frame2, text="SELL", command=self.sell_stock,
                            bg=self.colors['red'], fg='white', font=('Segoe UI', 11, 'bold'),
                            relief=tk.FLAT, padx=32, pady=10, cursor='hand2',
                            activebackground=self.colors['red_hover'])
        sell_btn.grid(row=1, column=1, padx=(0, 0))
        
        self.sell_info_label = tk.Label(form_frame2, text="", bg=self.colors['panel_highlight'], 
                                        fg=self.colors['text_secondary'], font=('Segoe UI', 8))
        self.sell_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))
    
    def create_history_section(self, parent):
        """Create trade history section."""
        history_frame = tk.Frame(parent, bg=self.colors['panel'], height=150)
        history_frame.pack(fill=tk.BOTH, expand=False)
        history_frame.pack_propagate(False)
        
        header = tk.Frame(history_frame, bg=self.colors['panel'], height=30)
        header.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        tk.Label(header, text="Trade History", bg=self.colors['panel'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # History listbox with scrollbar
        listbox_frame = tk.Frame(history_frame, bg=self.colors['panel'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(listbox_frame, bg=self.colors['border'], fg=self.colors['text'],
                                          selectbackground=self.colors['hover'], selectforeground=self.colors['text'],
                                          font=('Consolas', 9), yscrollcommand=scrollbar.set,
                                          relief=tk.FLAT, borderwidth=0)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
    
    def search_stock(self):
        """Search for a stock and update display."""
        symbol = self.search_entry.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a stock symbol")
            return
        
        try:
            info = self.simulator.stock_data.get_stock_info(symbol)
            self.current_symbol = symbol
            self.current_price = info['current_price']
            
            # Update stock info
            self.stock_name_label.config(text=f"{info['name']} ({symbol})")
            self.stock_price_label.config(text=f"${info['current_price']:.2f}")
            
            # Update chart
            self.update_chart(symbol)
            
            # Update buy/sell info
            self.update_trade_info()
            
            # Restart auto-refresh if enabled
            if self.auto_refresh:
                self.start_auto_refresh()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch stock data:\n{str(e)}")
    
    def set_timeframe(self, period, interval, button_text):
        """Set the chart timeframe."""
        self.current_timeframe = (period, interval)
        self.highlight_timeframe_button(button_text)
        if self.current_symbol:
            self.update_chart(self.current_symbol)
    
    def highlight_timeframe_button(self, selected_text):
        """Highlight the selected timeframe button."""
        for btn_text, btn in self.timeframe_buttons.items():
            if btn_text == selected_text:
                btn.config(bg=self.colors['blue'], fg='white', activebackground=self.colors['blue_hover'])
            else:
                btn.config(bg=self.colors['panel_highlight'], fg=self.colors['text'], 
                          activebackground=self.colors['hover'])
    
    def update_chart(self, symbol):
        """Update the stock chart with candlestick chart for current timeframe."""
        try:
            ticker = yf.Ticker(symbol)
            period, interval = self.current_timeframe
            
            # Get data based on timeframe
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError("No chart data available")
            
            # Prepare OHLC data for candlestick chart
            # Limit data points for performance (last 500 candles)
            if len(data) > 500:
                data = data.tail(500)
            
            # Clear axes first
            self.ax.clear()
            self.ax.set_facecolor(self.colors['panel'])
            self.ax.tick_params(colors=self.colors['text_secondary'])
            
            # Reset index to get dates as a column, then convert to matplotlib date format
            data_copy = data.reset_index()
            # Handle different possible date column names (Datetime, Date, etc.)
            date_col = data_copy.columns[0]  # First column is usually the datetime index
            data_copy[date_col] = mdates.date2num(data_copy[date_col])
            
            # Prepare OHLC data
            dates = data_copy[date_col].values
            opens = data_copy['Open'].values
            highs = data_copy['High'].values
            lows = data_copy['Low'].values
            closes = data_copy['Close'].values
            
            # Remove any NaN values
            valid_mask = ~(pd.isna(opens) | pd.isna(highs) | pd.isna(lows) | pd.isna(closes))
            dates = dates[valid_mask]
            opens = opens[valid_mask]
            highs = highs[valid_mask]
            lows = lows[valid_mask]
            closes = closes[valid_mask]
            
            if len(dates) == 0:
                raise ValueError("No valid chart data available after filtering")
            
            # Store data for interactive features
            self.chart_data = data_copy.iloc[valid_mask].copy()
            self.chart_dates = dates
            self.chart_opens = opens
            self.chart_highs = highs
            self.chart_lows = lows
            self.chart_closes = closes
            
            # Calculate width based on interval for better visibility
            # Width is a fraction of the date range
            date_range = dates[-1] - dates[0] if len(dates) > 1 else 1
            num_candles = len(dates)
            if interval == '1m':
                width = date_range / (num_candles * 2.5)
                date_format = '%H:%M'
            elif interval == '5m':
                width = date_range / (num_candles * 2.5)
                date_format = '%H:%M'
            elif interval == '10m':
                width = date_range / (num_candles * 2.5)
                date_format = '%m/%d %H:%M'
            else:  # 30m
                width = date_range / (num_candles * 2.5)
                date_format = '%m/%d %H:%M'
            
            # Plot candlesticks manually
            for i, (date, open_price, high, low, close) in enumerate(zip(dates, opens, highs, lows, closes)):
                # Determine if bullish (green) or bearish (red)
                is_bullish = close >= open_price
                color = self.colors['green'] if is_bullish else self.colors['red']
                
                # Draw the wick (high-low line)
                self.ax.plot([date, date], [low, high], color=color, linewidth=1, solid_capstyle='round')
                
                # Draw the body (rectangle for open-close)
                body_low = min(open_price, close)
                body_high = max(open_price, close)
                body_height = body_high - body_low
                # Ensure minimum body height for visibility
                if body_height < (high - low) * 0.1:
                    body_height = (high - low) * 0.1
                    body_low = (open_price + close) / 2 - body_height / 2
                
                rect = Rectangle((date - width/2, body_low), width, body_height,
                               facecolor=color, edgecolor=color, linewidth=1)
                self.ax.add_patch(rect)
            
            # Format axes
            self.ax.set_xlabel('Time', color=self.colors['text_secondary'])
            self.ax.set_ylabel('Price ($)', color=self.colors['text_secondary'])
            
            # Format title with timeframe
            timeframe_names = {
                '1m': '1 Minute', '5m': '5 Minutes', 
                '10m': '10 Minutes', '30m': '30 Minutes'
            }
            timeframe_name = timeframe_names.get(interval, interval)
            self.ax.set_title(f'{symbol} - {timeframe_name} Candles', color=self.colors['text'], 
                            fontsize=14, fontweight='bold')
            
            # Format x-axis
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
            self.ax.grid(True, alpha=0.3, color=self.colors['text_secondary'], linestyle='--')
            
            # Rotate x-axis labels for better readability
            self.fig.autofmt_xdate()
            
            # Enable zoom and pan
            self.canvas.draw()
            
        except Exception as e:
            self.ax.clear()
            self.ax.set_facecolor(self.colors['panel'])
            self.ax.text(0.5, 0.5, f'Error loading chart:\n{str(e)}', 
                        ha='center', va='center', transform=self.ax.transAxes,
                        color=self.colors['red'], fontsize=12)
            # Clear chart data on error
            self.chart_data = None
            self.chart_dates = None
            self.canvas.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement for crosshair and tooltip."""
        if event.inaxes != self.ax or self.chart_dates is None or len(self.chart_dates) == 0:
            # Remove crosshair if mouse leaves chart area
            if self.crosshair_vline:
                self.crosshair_vline.remove()
                self.crosshair_vline = None
            if self.crosshair_hline:
                self.crosshair_hline.remove()
                self.crosshair_hline = None
            if self.tooltip_annotation:
                self.tooltip_annotation.remove()
                self.tooltip_annotation = None
            self.canvas.draw_idle()
            return
        
        # Find nearest candle to mouse x position
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Find closest date index
        date_idx = np.abs(self.chart_dates - xdata).argmin()
        
        if date_idx >= len(self.chart_dates):
            return
        
        # Remove old crosshair
        if self.crosshair_vline:
            self.crosshair_vline.remove()
        if self.crosshair_hline:
            self.crosshair_hline.remove()
        if self.tooltip_annotation:
            self.tooltip_annotation.remove()
        
        # Draw vertical crosshair line
        self.crosshair_vline = self.ax.axvline(x=self.chart_dates[date_idx], 
                                               color=self.colors['text_secondary'], 
                                               linestyle='--', linewidth=1, alpha=0.7)
        
        # Draw horizontal crosshair line at current price
        self.crosshair_hline = self.ax.axhline(y=ydata, 
                                              color=self.colors['text_secondary'], 
                                              linestyle='--', linewidth=1, alpha=0.7)
        
        # Get OHLC data for tooltip
        open_price = self.chart_opens[date_idx]
        high_price = self.chart_highs[date_idx]
        low_price = self.chart_lows[date_idx]
        close_price = self.chart_closes[date_idx]
        
        # Convert date back to readable format
        date_str = mdates.num2date(self.chart_dates[date_idx]).strftime('%Y-%m-%d %H:%M')
        
        # Create tooltip text
        tooltip_text = (f"Time: {date_str}\n"
                       f"Open: ${open_price:.2f}\n"
                       f"High: ${high_price:.2f}\n"
                       f"Low: ${low_price:.2f}\n"
                       f"Close: ${close_price:.2f}")
        
        # Position tooltip near cursor
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(self.chart_dates[date_idx], high_price),
            xytext=(10, 10),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['border'], 
                     edgecolor=self.colors['text_secondary'], alpha=0.9),
            fontsize=9,
            color=self.colors['text'],
            family='monospace'
        )
        
        self.canvas.draw_idle()
    
    def on_mouse_click(self, event):
        """Handle mouse click for price selection."""
        if event.inaxes != self.ax or self.chart_dates is None:
            return
        
        # Double click to reset zoom
        if event.dblclick:
            self.ax.relim()
            self.ax.autoscale()
            self.canvas.draw()
    
    def on_mouse_release(self, event):
        """Handle mouse release."""
        pass
    
    def manual_refresh(self):
        """Manually refresh stock price and chart."""
        if self.current_symbol:
            self.refresh_stock_data()
    
    def refresh_stock_data(self):
        """Refresh current stock price and chart."""
        if not self.current_symbol:
            return
        
        try:
            # Update price
            info = self.simulator.stock_data.get_stock_info(self.current_symbol)
            self.current_price = info['current_price']
            self.stock_price_label.config(text=f"${info['current_price']:.2f}")
            
            # Update chart
            self.update_chart(self.current_symbol)
            
            # Update trade info
            self.update_trade_info()
            
        except Exception as e:
            # Silently fail on refresh to avoid spam
            pass
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Start automatic refresh."""
        if self.auto_refresh and self.current_symbol:
            self.refresh_stock_data()
        self.schedule_refresh()
    
    def stop_auto_refresh(self):
        """Stop automatic refresh."""
        if hasattr(self, 'refresh_job'):
            self.root.after_cancel(self.refresh_job)
    
    def schedule_refresh(self):
        """Schedule the next refresh."""
        if self.auto_refresh:
            self.refresh_job = self.root.after(self.refresh_interval, self.start_auto_refresh)
    
    def update_trade_info(self):
        """Update buy/sell information displays."""
        if not self.current_symbol or not self.current_price:
            return
        
        # Check if we own this stock
        holdings = self.simulator.portfolio.get_holdings()
        owned_shares = holdings.get(self.current_symbol, 0)
        
        # Update buy info (show max affordable)
        if self.current_price > 0:
            max_affordable = int(self.simulator.portfolio.get_cash() / self.current_price)
            self.buy_info_label.config(text=f"Max affordable: {max_affordable} shares (${self.current_price:.2f} per share)")
        
        # Update sell info
        if owned_shares > 0:
            self.sell_info_label.config(text=f"You own: {owned_shares} shares")
        else:
            self.sell_info_label.config(text="You don't own any shares of this stock")
    
    def buy_stock(self):
        """Execute a buy order."""
        if not self.current_symbol:
            messagebox.showwarning("Warning", "Please search for a stock first")
            return
        
        quantity_str = self.buy_quantity_entry.get().strip()
        if not quantity_str:
            messagebox.showwarning("Warning", "Please enter a quantity")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity (positive integer)")
            return
        
        result = self.simulator.buy_stock(self.current_symbol, quantity)
        
        if result['success']:
            messagebox.showinfo(
                "Success",
                f"Bought {quantity} shares of {self.current_symbol} at ${result['price']:.2f}\n"
                f"Total cost: ${result['total_cost']:.2f}\n"
                f"Remaining cash: ${self.simulator.portfolio.get_cash():.2f}"
            )
            self.buy_quantity_entry.delete(0, tk.END)
            self.update_portfolio()
            self.update_history()
            self.update_trade_info()
        else:
            messagebox.showerror("Error", result['error'])
    
    def sell_stock(self):
        """Execute a sell order."""
        if not self.current_symbol:
            messagebox.showwarning("Warning", "Please search for a stock first")
            return
        
        quantity_str = self.sell_quantity_entry.get().strip()
        if not quantity_str:
            messagebox.showwarning("Warning", "Please enter a quantity")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity (positive integer)")
            return
        
        result = self.simulator.sell_stock(self.current_symbol, quantity)
        
        if result['success']:
            messagebox.showinfo(
                "Success",
                f"Sold {quantity} shares of {self.current_symbol} at ${result['price']:.2f}\n"
                f"Total proceeds: ${result['total_proceeds']:.2f}\n"
                f"Cash balance: ${self.simulator.portfolio.get_cash():.2f}"
            )
            self.sell_quantity_entry.delete(0, tk.END)
            self.update_portfolio()
            self.update_history()
            self.update_trade_info()
        else:
            messagebox.showerror("Error", result['error'])
    
    def update_portfolio(self):
        """Update the portfolio display."""
        summary = self.simulator.get_portfolio_summary()
        
        # Update portfolio values
        self.total_value_label.config(text=f"${summary['total_value']:,.2f}")
        self.cash_label.config(text=f"${summary['cash']:,.2f}")
        self.holdings_value_label.config(text=f"${summary['holdings_value']:,.2f}")
        
        # Update holdings tree
        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)
        
        if summary['holdings']:
            for symbol, quantity in summary['holdings'].items():
                try:
                    price = self.simulator.stock_data.get_current_price(symbol)
                    value = quantity * price
                    self.holdings_tree.insert('', tk.END, values=(
                        symbol, quantity, f"${price:.2f}", f"${value:.2f}"
                    ))
                except:
                    self.holdings_tree.insert('', tk.END, values=(
                        symbol, quantity, "N/A", "N/A"
                    ))
    
    def update_history(self):
        """Update the trade history display."""
        history = self.simulator.get_trade_history()
        
        self.history_listbox.delete(0, tk.END)
        
        if history:
            # Show most recent first
            for trade in reversed(history):
                timestamp = trade['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                action = trade['action'].upper()
                symbol = trade['symbol']
                quantity = trade['quantity']
                price = trade['price']
                total = trade['total_cost']
                
                action_color = "GREEN" if action == "BUY" else "RED"
                entry = f"{timestamp} | {action:4s} | {symbol:5s} | {quantity:4d} @ ${price:7.2f} = ${total:10.2f}"
                self.history_listbox.insert(0, entry)
        else:
            self.history_listbox.insert(0, "No trades yet.")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = TradingSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
