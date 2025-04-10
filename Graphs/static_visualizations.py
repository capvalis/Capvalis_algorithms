import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from datetime import datetime

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

print("Loading data...")
# Read the CSV file
df = pd.read_csv('Capvalis Exclusive.csv')

# Filter out monthly total rows
df = df[~df['Date'].str.contains('Monthly Total', na=False)]

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate cumulative P&L
df['Cumulative_PnL'] = df['P&L'].cumsum()

# Calculate drawdown
rolling_max = df['Cumulative_PnL'].expanding().max()
df['Drawdown'] = (df['Cumulative_PnL'] - rolling_max) / rolling_max * 100

# Money formatter for y-axis
def money_formatter(x, p):
    return f'₹{x:,.0f}'

# 1. Equity Curve
def create_equity_curve():
    print("Creating equity curve...")
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # Set up the plot
    ax.set_title('Equity Curve', pad=20, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Profit & Loss (₹)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(FuncFormatter(money_formatter))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Plot the equity curve
    ax.plot(df['Date'], df['Cumulative_PnL'], color=COLORS['blue'], linewidth=2, label='Cumulative P&L')
    
    # Add a point marker at the end
    ax.plot([df['Date'].iloc[-1]], [df['Cumulative_PnL'].iloc[-1]], 'o', color=COLORS['red'], markersize=8)
    
    # Add text annotation for final value
    final_value = df['Cumulative_PnL'].iloc[-1]
    ax.text(0.02, 0.95, f'Final Value: ₹{final_value:,.0f}', transform=ax.transAxes, fontsize=12, 
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('equity_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Equity curve saved as 'equity_curve.png'")

# 2. Drawdown Chart
def create_drawdown_chart():
    print("Creating drawdown chart...")
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # Set up the plot
    ax.set_title('Drawdown Analysis', pad=20, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Plot the drawdown
    ax.fill_between(df['Date'], df['Drawdown'], 0, color=COLORS['red'], alpha=0.3)
    ax.plot(df['Date'], df['Drawdown'], color=COLORS['red'], linewidth=2, label='Drawdown')
    
    # Add text annotation for maximum drawdown
    max_drawdown = df['Drawdown'].min()
    max_drawdown_date = df['Date'].iloc[df['Drawdown'].argmin()]
    ax.text(0.02, 0.95, f'Maximum Drawdown: {max_drawdown:.2f}%', transform=ax.transAxes, fontsize=12, 
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add annotation for maximum drawdown point
    ax.annotate(f'Max Drawdown: {max_drawdown:.2f}%',
                xy=(max_drawdown_date, max_drawdown),
                xytext=(10, -30),
                textcoords='offset points',
                ha='left',
                va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('drawdown_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Drawdown chart saved as 'drawdown_chart.png'")

# 3. Monthly Performance Heatmap
def create_monthly_heatmap():
    print("Creating monthly performance heatmap...")
    # Create monthly PnL matrix
    monthly_pnl = df.pivot_table(
        values='P&L',
        index=df['Date'].dt.year,
        columns=df['Date'].dt.month,
        aggfunc='sum',
        fill_value=0
    )
    
    # Rename columns to month names
    monthly_pnl.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # Set up the plot
    ax.set_title('Monthly Performance Heatmap', pad=20, fontsize=14, fontweight='bold')
    
    # Create custom diverging colormap
    cmap = plt.cm.RdYlGn
    
    # Create heatmap
    im = ax.imshow(monthly_pnl, cmap=cmap, aspect='auto')
    
    # Set up axes
    ax.set_xticks(np.arange(len(monthly_pnl.columns)))
    ax.set_yticks(np.arange(len(monthly_pnl.index)))
    ax.set_xticklabels(monthly_pnl.columns)
    ax.set_yticklabels(monthly_pnl.index)
    
    # Add colorbar
    cbar = fig.colorbar(im, ax=ax, label='Profit/Loss (₹)')
    
    # Add text annotations
    for i in range(len(monthly_pnl.index)):
        for j in range(len(monthly_pnl.columns)):
            value = monthly_pnl.iloc[i, j]
            if value != 0:
                text_color = 'black' if abs(value) < monthly_pnl.abs().max().max() / 2 else 'white'
                ax.text(j, i, f'₹{value:,.0f}', ha='center', va='center', color=text_color, fontsize=8)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('monthly_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Monthly heatmap saved as 'monthly_heatmap.png'")

# 4. Win Rate and Risk-Reward Ratio
def create_win_rate_chart():
    print("Creating win rate chart...")
    # Calculate metrics
    total_trades = len(df)
    winning_trades = len(df[df['P&L'] > 0])
    win_rate = (winning_trades / total_trades) * 100
    
    # Calculate average win and loss
    avg_win = df[df['P&L'] > 0]['P&L'].mean() if winning_trades > 0 else 0
    avg_loss = abs(df[df['P&L'] < 0]['P&L'].mean()) if len(df[df['P&L'] < 0]) > 0 else 0
    rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax1.set_facecolor(COLORS['background'])
    ax2.set_facecolor(COLORS['background'])
    
    # Set up the win rate plot
    ax1.set_title('Win Rate', pad=20, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Category', fontsize=12)
    ax1.set_ylabel('Percentage (%)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Create win rate bar chart
    bars1 = ax1.bar(['Win Rate', 'Loss Rate'], [win_rate, 100-win_rate], 
                    color=[COLORS['green'], COLORS['red']])
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Set up the risk-reward ratio plot
    ax2.set_title('Risk-Reward Ratio', pad=20, fontsize=14, fontweight='bold')
    ax2.set_xlabel('Category', fontsize=12)
    ax2.set_ylabel('Amount (₹)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Create risk-reward ratio bar chart
    bars2 = ax2.bar(['Average Win', 'Average Loss'], [avg_win, avg_loss], 
                    color=[COLORS['green'], COLORS['red']])
    
    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1000,
                f'₹{height:,.0f}', ha='center', va='bottom')
    
    # Add text annotations
    ax1.text(0.02, 0.95, f'Win Rate: {win_rate:.2f}%\n({winning_trades}/{total_trades} trades)', 
             transform=ax1.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    ax2.text(0.02, 0.95, f'R:R Ratio: {rr_ratio:.2f}', 
             transform=ax2.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('win_rate_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Win rate chart saved as 'win_rate_chart.png'")

# 5. Performance Metrics Dashboard
def create_performance_dashboard():
    print("Creating performance metrics dashboard...")
    # Calculate metrics
    total_trades = len(df)
    winning_trades = len(df[df['P&L'] > 0])
    win_rate = (winning_trades / total_trades) * 100
    
    # Calculate average win and loss
    avg_win = df[df['P&L'] > 0]['P&L'].mean() if winning_trades > 0 else 0
    avg_loss = abs(df[df['P&L'] < 0]['P&L'].mean()) if len(df[df['P&L'] < 0]) > 0 else 0
    rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    
    # Calculate drawdown
    max_drawdown = df['Drawdown'].min()
    
    # Calculate CAGR
    start_date = df['Date'].min()
    end_date = df['Date'].max()
    years = (end_date - start_date).days / 365.25
    initial_investment = 100000
    final_value = initial_investment + df['Cumulative_PnL'].iloc[-1]
    cagr = (final_value / initial_investment) ** (1 / years) - 1
    
    # Calculate Sharpe ratio
    daily_returns = df['P&L'] / initial_investment
    annual_return = daily_returns.mean() * 252
    annual_volatility = daily_returns.std() * np.sqrt(252)
    risk_free_rate = 0.05
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
    
    # Create figure
    fig = plt.figure(figsize=(15, 10))
    fig.patch.set_facecolor(COLORS['background'])
    
    # Create subplots
    gs = fig.add_gridspec(3, 3)
    
    # 1. Equity Curve
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(COLORS['background'])
    ax1.set_title('Equity Curve', pad=20, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Cumulative Profit & Loss (₹)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(FuncFormatter(money_formatter))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.plot(df['Date'], df['Cumulative_PnL'], color=COLORS['blue'], linewidth=2)
    
    # 2. Win Rate
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(COLORS['background'])
    ax2.set_title('Win Rate', pad=20, fontsize=14, fontweight='bold')
    ax2.pie([win_rate, 100-win_rate], labels=['Win', 'Loss'], autopct='%1.1f%%', 
            colors=[COLORS['green'], COLORS['red']], startangle=90)
    
    # 3. Risk-Reward Ratio
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor(COLORS['background'])
    ax3.set_title('Risk-Reward Ratio', pad=20, fontsize=14, fontweight='bold')
    ax3.bar(['Win', 'Loss'], [avg_win, avg_loss], color=[COLORS['green'], COLORS['red']])
    ax3.yaxis.set_major_formatter(FuncFormatter(money_formatter))
    
    # 4. Drawdown
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.set_facecolor(COLORS['background'])
    ax4.set_title('Maximum Drawdown', pad=20, fontsize=14, fontweight='bold')
    ax4.fill_between(df['Date'], df['Drawdown'], 0, color=COLORS['red'], alpha=0.3)
    ax4.plot(df['Date'], df['Drawdown'], color=COLORS['red'], linewidth=2)
    ax4.set_xlabel('Date', fontsize=12)
    ax4.set_ylabel('Drawdown (%)', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_locator(mdates.YearLocator())
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # 5. Performance Metrics
    ax5 = fig.add_subplot(gs[2, :])
    ax5.set_facecolor(COLORS['background'])
    ax5.set_title('Performance Metrics', pad=20, fontsize=14, fontweight='bold')
    ax5.axis('off')
    
    # Create a table with performance metrics
    metrics = [
        ['Total Trades', f'{total_trades}'],
        ['Win Rate', f'{win_rate:.2f}%'],
        ['Risk-Reward Ratio', f'{rr_ratio:.2f}'],
        ['Maximum Drawdown', f'{max_drawdown:.2f}%'],
        ['CAGR', f'{cagr*100:.2f}%'],
        ['Sharpe Ratio', f'{sharpe_ratio:.2f}'],
        ['Initial Investment', f'₹{initial_investment:,.0f}'],
        ['Final Value', f'₹{final_value:,.0f}'],
        ['Total Return', f'{((final_value/initial_investment)-1)*100:.2f}%']
    ]
    
    table = ax5.table(cellText=metrics, colLabels=['Metric', 'Value'], 
                     cellLoc='center', loc='center', colWidths=[0.4, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('performance_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Performance dashboard saved as 'performance_dashboard.png'")

# Execute all visualization functions
if __name__ == "__main__":
    try:
        print("Creating static visualizations...")
        create_equity_curve()
        create_drawdown_chart()
        create_monthly_heatmap()
        create_win_rate_chart()
        create_performance_dashboard()
        print("All static visualizations have been generated successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc() 