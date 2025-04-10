import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import time

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

# 1. Animated Equity Curve
def create_equity_curve_animation():
    print("Creating animated equity curve...")
    start_time = time.time()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # Set up the plot
    ax.set_title('Animated Equity Curve', pad=20, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Profit & Loss (₹)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(FuncFormatter(money_formatter))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Set x and y limits
    ax.set_xlim(df['Date'].min(), df['Date'].max())
    ax.set_ylim(df['Cumulative_PnL'].min() * 0.9, df['Cumulative_PnL'].max() * 1.1)
    
    # Initialize empty line
    line, = ax.plot([], [], color=COLORS['blue'], linewidth=2, label='Cumulative P&L')
    
    # Add a point marker that will move along the line
    point, = ax.plot([], [], 'o', color=COLORS['red'], markersize=8)
    
    # Add text annotation for current value
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, 
                  bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Animation update function
    def update(frame):
        # Get data up to current frame
        data = df.iloc[:frame+1]
        
        # Update line
        line.set_data(data['Date'], data['Cumulative_PnL'])
        
        # Update point
        if frame < len(df):
            point.set_data([data['Date'].iloc[-1]], [data['Cumulative_PnL'].iloc[-1]])
        
        # Update text
        if frame < len(df):
            current_value = data['Cumulative_PnL'].iloc[-1]
            text.set_text(f'Current Value: ₹{current_value:,.0f}')
        
        return line, point, text
    
    # Create animation with fewer frames for faster generation
    frames = min(len(df), 100)  # Limit to 100 frames
    step = max(1, len(df) // frames)
    frame_indices = list(range(0, len(df), step))
    if len(df) - 1 not in frame_indices:
        frame_indices.append(len(df) - 1)
    
    print(f"Generating {len(frame_indices)} frames for equity curve...")
    ani = animation.FuncAnimation(fig, update, frames=frame_indices, 
                                 interval=50, blit=True)
    
    # Save animation
    print("Saving equity curve animation...")
    ani.save('animated_equity_curve.gif', writer='pillow', fps=20)
    plt.close()
    
    elapsed_time = time.time() - start_time
    print(f"Animated equity curve saved as 'animated_equity_curve.gif' in {elapsed_time:.2f} seconds")

# 2. Animated Drawdown Chart
def create_drawdown_animation():
    print("Creating animated drawdown chart...")
    start_time = time.time()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # Set up the plot
    ax.set_title('Animated Drawdown Analysis', pad=20, fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Set x and y limits
    ax.set_xlim(df['Date'].min(), df['Date'].max())
    ax.set_ylim(df['Drawdown'].min() * 1.1, 1)
    
    # Initialize empty line and fill
    line, = ax.plot([], [], color=COLORS['red'], linewidth=2, label='Drawdown')
    
    # Add text annotation for current drawdown
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, 
                  bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Animation update function
    def update(frame):
        # Get data up to current frame
        data = df.iloc[:frame+1]
        
        # Update line
        line.set_data(data['Date'], data['Drawdown'])
        
        # Update fill
        ax.collections = []  # Clear previous fills
        ax.fill_between(data['Date'], data['Drawdown'], 0, color=COLORS['red'], alpha=0.3)
        
        # Update text
        if frame < len(df):
            current_dd = data['Drawdown'].iloc[-1]
            text.set_text(f'Current Drawdown: {current_dd:.2f}%')
        
        return line, text
    
    # Create animation with fewer frames for faster generation
    frames = min(len(df), 100)  # Limit to 100 frames
    step = max(1, len(df) // frames)
    frame_indices = list(range(0, len(df), step))
    if len(df) - 1 not in frame_indices:
        frame_indices.append(len(df) - 1)
    
    print(f"Generating {len(frame_indices)} frames for drawdown chart...")
    ani = animation.FuncAnimation(fig, update, frames=frame_indices, 
                                 interval=50, blit=False)
    
    # Save animation
    print("Saving drawdown animation...")
    ani.save('animated_drawdown.gif', writer='pillow', fps=20)
    plt.close()
    
    elapsed_time = time.time() - start_time
    print(f"Animated drawdown chart saved as 'animated_drawdown.gif' in {elapsed_time:.2f} seconds")

# 3. Animated Monthly Performance Heatmap
def create_monthly_heatmap_animation():
    print("Creating animated monthly heatmap...")
    start_time = time.time()
    
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
    ax.set_title('Animated Monthly Performance Heatmap', pad=20, fontsize=14, fontweight='bold')
    
    # Create custom diverging colormap
    cmap = LinearSegmentedColormap.from_list('custom', ['#F44336', 'white', '#4CAF50'])
    
    # Initialize empty heatmap
    heatmap = ax.imshow(np.zeros_like(monthly_pnl), cmap=cmap, aspect='auto')
    
    # Set up axes
    ax.set_xticks(np.arange(len(monthly_pnl.columns)))
    ax.set_yticks(np.arange(len(monthly_pnl.index)))
    ax.set_xticklabels(monthly_pnl.columns)
    ax.set_yticklabels(monthly_pnl.index)
    
    # Add colorbar
    cbar = fig.colorbar(heatmap, ax=ax, label='Profit/Loss (₹)')
    
    # Add text annotation for current month
    text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, 
                  bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Animation update function
    def update(frame):
        # Calculate how many months to show based on frame
        months_to_show = min(frame + 1, len(df))
        current_date = df['Date'].iloc[min(frame, len(df)-1)]
        
        # Create a copy of the monthly PnL matrix
        current_pnl = monthly_pnl.copy()
        
        # Zero out future months
        for year in current_pnl.index:
            for month in current_pnl.columns:
                month_num = current_pnl.columns.get_loc(month) + 1
                if year < current_date.year or (year == current_date.year and month_num <= current_date.month):
                    continue
                else:
                    current_pnl.loc[year, month] = 0
        
        # Update heatmap
        heatmap.set_data(current_pnl)
        
        # Update text
        text.set_text(f'Data up to: {current_date.strftime("%B %Y")}')
        
        # Update colorbar range
        vmin = min(monthly_pnl.min().min(), 0)
        vmax = max(monthly_pnl.max().max(), 0)
        heatmap.set_clim(vmin, vmax)
        
        return heatmap, text
    
    # Create animation with fewer frames for faster generation
    frames = min(len(df), 100)  # Limit to 100 frames
    step = max(1, len(df) // frames)
    frame_indices = list(range(0, len(df), step))
    if len(df) - 1 not in frame_indices:
        frame_indices.append(len(df) - 1)
    
    print(f"Generating {len(frame_indices)} frames for monthly heatmap...")
    ani = animation.FuncAnimation(fig, update, frames=frame_indices, 
                                 interval=50, blit=False)
    
    # Save animation
    print("Saving monthly heatmap animation...")
    ani.save('animated_monthly_heatmap.gif', writer='pillow', fps=20)
    plt.close()
    
    elapsed_time = time.time() - start_time
    print(f"Animated monthly heatmap saved as 'animated_monthly_heatmap.gif' in {elapsed_time:.2f} seconds")

# 4. Animated Win Rate and Risk-Reward Ratio
def create_win_rate_animation():
    print("Creating animated win rate chart...")
    start_time = time.time()
    
    # Calculate metrics over time
    df['Win'] = df['P&L'] > 0
    df['Cumulative_Wins'] = df['Win'].cumsum()
    df['Total_Trades'] = range(1, len(df) + 1)
    df['Win_Rate'] = df['Cumulative_Wins'] / df['Total_Trades'] * 100
    
    # Calculate average win and loss
    df['Cumulative_Win_Amount'] = df.apply(lambda x: x['P&L'] if x['P&L'] > 0 else 0, axis=1).cumsum()
    df['Cumulative_Loss_Amount'] = df.apply(lambda x: abs(x['P&L']) if x['P&L'] < 0 else 0, axis=1).cumsum()
    df['Winning_Trades'] = df['Win'].cumsum()
    df['Losing_Trades'] = (df['Win'] == False).cumsum()
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.patch.set_facecolor(COLORS['background'])
    ax1.set_facecolor(COLORS['background'])
    ax2.set_facecolor(COLORS['background'])
    
    # Set up the win rate plot
    ax1.set_title('Win Rate Over Time', pad=20, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Number of Trades', fontsize=12)
    ax1.set_ylabel('Win Rate (%)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    
    # Set up the risk-reward ratio plot
    ax2.set_title('Risk-Reward Ratio Over Time', pad=20, fontsize=14, fontweight='bold')
    ax2.set_xlabel('Number of Trades', fontsize=12)
    ax2.set_ylabel('Risk-Reward Ratio', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Initialize empty lines
    line1, = ax1.plot([], [], color=COLORS['blue'], linewidth=2, label='Win Rate')
    line2, = ax2.plot([], [], color=COLORS['purple'], linewidth=2, label='R:R Ratio')
    
    # Add text annotations
    text1 = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=12, 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    text2 = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=12, 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Add legends
    ax1.legend(loc='upper left', fontsize=10)
    ax2.legend(loc='upper left', fontsize=10)
    
    # Animation update function
    def update(frame):
        # Get data up to current frame
        data = df.iloc[:frame+1]
        
        # Update win rate line
        line1.set_data(data['Total_Trades'], data['Win_Rate'])
        ax1.set_xlim(0, len(df))
        
        # Update risk-reward ratio line
        if len(data) > 0 and data['Losing_Trades'].iloc[-1] > 0:
            rr_ratio = (data['Cumulative_Win_Amount'].iloc[-1] / data['Winning_Trades'].iloc[-1]) / \
                      (data['Cumulative_Loss_Amount'].iloc[-1] / data['Losing_Trades'].iloc[-1])
            line2.set_data(data['Total_Trades'], [rr_ratio] * len(data))
            ax2.set_xlim(0, len(df))
            ax2.set_ylim(0, max(3, rr_ratio * 1.2))
        
        # Update text
        if frame < len(df):
            text1.set_text(f'Win Rate: {data["Win_Rate"].iloc[-1]:.2f}%')
            if data['Losing_Trades'].iloc[-1] > 0:
                rr_ratio = (data['Cumulative_Win_Amount'].iloc[-1] / data['Winning_Trades'].iloc[-1]) / \
                          (data['Cumulative_Loss_Amount'].iloc[-1] / data['Losing_Trades'].iloc[-1])
                text2.set_text(f'R:R Ratio: {rr_ratio:.2f}')
            else:
                text2.set_text('R:R Ratio: N/A')
        
        return line1, line2, text1, text2
    
    # Create animation with fewer frames for faster generation
    frames = min(len(df), 100)  # Limit to 100 frames
    step = max(1, len(df) // frames)
    frame_indices = list(range(0, len(df), step))
    if len(df) - 1 not in frame_indices:
        frame_indices.append(len(df) - 1)
    
    print(f"Generating {len(frame_indices)} frames for win rate chart...")
    ani = animation.FuncAnimation(fig, update, frames=frame_indices, 
                                 interval=50, blit=False)
    
    # Save animation
    print("Saving win rate animation...")
    ani.save('animated_win_rate.gif', writer='pillow', fps=20)
    plt.close()
    
    elapsed_time = time.time() - start_time
    print(f"Animated win rate chart saved as 'animated_win_rate.gif' in {elapsed_time:.2f} seconds")

# Execute all animation functions
if __name__ == "__main__":
    try:
        print("Creating animated visualizations...")
        create_equity_curve_animation()
        create_drawdown_animation()
        create_monthly_heatmap_animation()
        create_win_rate_animation()
        print("All animated visualizations have been generated successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc() 