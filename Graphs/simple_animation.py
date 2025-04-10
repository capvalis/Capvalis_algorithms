import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import time

print("Loading data...")
# Read the CSV file
df = pd.read_csv('Capvalis Exclusive.csv')

# Filter out monthly total rows
df = df[~df['Date'].str.contains('Monthly Total', na=False)]

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate cumulative P&L
df['Cumulative_PnL'] = df['P&L'].cumsum()

# Money formatter for y-axis
def money_formatter(x, p):
    return f'₹{x:,.0f}'

print("Creating a simple animated equity curve...")
start_time = time.time()

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

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
line, = ax.plot([], [], color='blue', linewidth=2, label='Cumulative P&L')

# Add a point marker that will move along the line
point, = ax.plot([], [], 'o', color='red', markersize=8)

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
frames = min(len(df), 50)  # Limit to 50 frames
step = max(1, len(df) // frames)
frame_indices = list(range(0, len(df), step))
if len(df) - 1 not in frame_indices:
    frame_indices.append(len(df) - 1)

print(f"Generating {len(frame_indices)} frames...")
ani = animation.FuncAnimation(fig, update, frames=frame_indices, 
                             interval=50, blit=True)

# Save animation
print("Saving animation...")
ani.save('simple_equity_curve.gif', writer='pillow', fps=20)
plt.close()

elapsed_time = time.time() - start_time
print(f"Animation saved as 'simple_equity_curve.gif' in {elapsed_time:.2f} seconds") 