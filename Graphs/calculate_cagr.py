import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file
df = pd.read_csv('Capvalis Exclusive.csv')

# Filter out monthly total rows
df = df[~df['Date'].str.contains('Monthly Total', na=False)]

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate cumulative P&L
df['Cumulative_PnL'] = df['P&L'].cumsum()

# Get the initial and final dates
start_date = df['Date'].min()
end_date = df['Date'].max()

# Calculate the number of years
years = (end_date - start_date).days / 365.25

# Initial investment
initial_investment = 100000

# Final value (initial investment + cumulative P&L)
final_value = initial_investment + df['Cumulative_PnL'].iloc[-1]

# Calculate CAGR
cagr = (final_value / initial_investment) ** (1 / years) - 1

print(f"Initial Investment: ₹{initial_investment:,.2f}")
print(f"Final Value: ₹{final_value:,.2f}")
print(f"Time Period: {years:.2f} years ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
print(f"CAGR: {cagr * 100:.2f}%")
print(f"Total Return: {((final_value / initial_investment) - 1) * 100:.2f}%") 