import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

# Set the style for all plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Custom color palette for modern look
COLORS = {
    'blue': '#2196F3',
    'green': '#4CAF50',
    'red': '#F44336',
    'purple': '#9C27B0',
    'orange': '#FF9800',
    'background': '#F5F5F5'
}

# Read the CSV file
df = pd.read_csv('Capvalis Exclusive.csv')

# Filter out monthly total rows
df = df[~df['Date'].str.contains('Monthly Total', na=False)]

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate cumulative P&L
df['Cumulative_PnL'] = df['P&L'].cumsum()

def money_formatter(x, p):
    return f'₹{x:,.0f}'

# 1. Equity Curve
def plot_equity_curve():
    fig = plt.figure(figsize=(15, 8))
    fig.patch.set_facecolor(COLORS['background'])
    
    # Plot cumulative equity curve
    plt.subplot(1, 2, 1)
    plt.plot(df['Date'], df['Cumulative_PnL'], label='Cumulative P&L', 
             color=COLORS['blue'], linewidth=2)
    plt.title('Growth of Capital Over Time', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Cumulative Profit & Loss (₹)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(money_formatter))
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Plot logarithmic equity curve
    plt.subplot(1, 2, 2)
    plt.semilogy(df['Date'], df['Cumulative_PnL'] - df['Cumulative_PnL'].min() + 1, 
                label='Logarithmic Growth', color=COLORS['green'], linewidth=2)
    plt.title('Logarithmic Growth Curve', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Log Scale (₹)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.tight_layout()
    plt.savefig('equity_curve.png', dpi=300, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

# 2. Yearly Returns Bar Chart
def plot_yearly_returns():
    # Calculate yearly returns
    yearly_returns = df.groupby(df['Date'].dt.year)['P&L'].sum()
    
    fig = plt.figure(figsize=(15, 8))
    fig.patch.set_facecolor(COLORS['background'])
    
    bars = plt.bar(range(len(yearly_returns)), yearly_returns.values)
    
    # Color coding with modern colors
    for bar in bars:
        if bar.get_height() >= 0:
            bar.set_color(COLORS['green'])
            bar.set_alpha(0.7)
        else:
            bar.set_color(COLORS['red'])
            bar.set_alpha(0.7)
    
    plt.title('Yearly Performance Overview', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Profit/Loss (₹)', fontsize=12)
    
    # Add value labels on top of bars
    for i, v in enumerate(yearly_returns.values):
        color = 'green' if v >= 0 else 'red'
        plt.text(i, v + (v * 0.01), f'₹{v:,.0f}', 
                ha='center', va='bottom', fontsize=10,
                color=color, fontweight='bold')
    
    plt.xticks(range(len(yearly_returns)), yearly_returns.index, rotation=0)
    plt.grid(True, alpha=0.3)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(money_formatter))
    
    plt.tight_layout()
    plt.savefig('yearly_returns.png', dpi=300, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

# 3. Drawdown Chart
def plot_drawdown():
    # Calculate drawdown
    rolling_max = df['Cumulative_PnL'].expanding().max()
    drawdown = (df['Cumulative_PnL'] - rolling_max) / rolling_max * 100
    
    fig = plt.figure(figsize=(15, 8))
    fig.patch.set_facecolor(COLORS['background'])
    
    plt.fill_between(df['Date'], drawdown, 0, color=COLORS['red'], alpha=0.3)
    plt.plot(df['Date'], drawdown, color=COLORS['red'], label='Maximum Drawdown', linewidth=2)
    plt.title('Risk Analysis: Maximum Drawdown', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Drawdown (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.legend(fontsize=10)
    
    # Add min drawdown annotation
    min_dd = drawdown.min()
    min_dd_date = df['Date'].iloc[drawdown.argmin()]
    plt.annotate(f'Max Drawdown: {min_dd:.1f}%',
                xy=(min_dd_date, min_dd),
                xytext=(10, -30),
                textcoords='offset points',
                ha='left',
                va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    plt.savefig('drawdown.png', dpi=300, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

# 4. Win Rate vs Risk-Reward Ratio
def plot_win_rate_rr():
    # Calculate win rate
    total_trades = len(df)
    winning_trades = len(df[df['P&L'] > 0])
    win_rate = (winning_trades / total_trades) * 100
    
    # Calculate average R:R ratio
    avg_win = df[df['P&L'] > 0]['P&L'].mean()
    avg_loss = abs(df[df['P&L'] < 0]['P&L'].mean())
    rr_ratio = avg_win / avg_loss if avg_loss != 0 else 0
    
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor(COLORS['background'])
    
    bars = plt.bar(['Win Rate', 'Risk-Reward Ratio'], 
            [win_rate, rr_ratio],
            color=[COLORS['blue'], COLORS['purple']])
    
    plt.title('Strategy Performance Metrics', pad=20, fontsize=14, fontweight='bold')
    plt.ylabel('Ratio', fontsize=12)
    
    # Add value labels on top of bars with more details
    plt.text(0, win_rate, f'{win_rate:.1f}%\n({winning_trades}/{total_trades} trades)', 
             ha='center', va='bottom', fontsize=10)
    plt.text(1, rr_ratio, f'{rr_ratio:.2f}\n(Win: ₹{avg_win:,.0f} / Loss: ₹{avg_loss:,.0f})', 
             ha='center', va='bottom', fontsize=10)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('win_rate_rr.png', dpi=300, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

# 5. Monthly PnL Heatmap
def plot_monthly_heatmap():
    # Create monthly PnL matrix
    monthly_pnl = df.pivot_table(
        values='P&L',
        index=df['Date'].dt.year,
        columns=df['Date'].dt.month,
        aggfunc='sum'
    )
    
    # Rename columns to month names
    monthly_pnl.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig = plt.figure(figsize=(15, 8))
    fig.patch.set_facecolor(COLORS['background'])
    
    # Create custom diverging colormap
    cmap = sns.diverging_palette(10, 133, as_cmap=True)
    
    sns.heatmap(monthly_pnl, 
                annot=True, 
                fmt=',.0f',
                cmap=cmap,
                center=0,
                annot_kws={'size': 8},
                cbar_kws={'label': 'Profit/Loss (₹)'})
    
    plt.title('Seasonal Performance Analysis', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Year', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('monthly_heatmap.png', dpi=300, bbox_inches='tight', facecolor=COLORS['background'])
    plt.close()

# Execute all plotting functions
if __name__ == "__main__":
    try:
        plot_equity_curve()
        plot_yearly_returns()
        plot_drawdown()
        plot_win_rate_rr()
        plot_monthly_heatmap()
        print("All visualizations have been generated successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}") 