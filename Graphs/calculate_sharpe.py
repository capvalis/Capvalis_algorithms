import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file
df = pd.read_csv('Capvalis Exclusive.csv')

# Filter out monthly total rows
df = df[~df['Date'].str.contains('Monthly Total', na=False)]

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate daily returns
df['Daily_Return'] = df['P&L'] / 100000  # Using 100,000 as the initial investment

# Calculate annualized metrics
annual_return = df['Daily_Return'].mean() * 252  # 252 trading days in a year
annual_volatility = df['Daily_Return'].std() * np.sqrt(252)

# Risk-free rate (assuming 5% annual risk-free rate)
risk_free_rate = 0.05

# Calculate Sharpe ratio
sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

# Calculate other metrics
total_return = df['Daily_Return'].sum()
max_drawdown = (df['Daily_Return'].cumsum() - df['Daily_Return'].cumsum().expanding().max()).min()
win_rate = len(df[df['P&L'] > 0]) / len(df) * 100

print(f"Annualized Return: {annual_return * 100:.2f}%")
print(f"Annualized Volatility: {annual_volatility * 100:.2f}%")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Total Return: {total_return * 100:.2f}%")
print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
print(f"Win Rate: {win_rate:.2f}%") 