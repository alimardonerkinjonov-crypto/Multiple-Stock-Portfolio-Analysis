import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

# Fetch historical data for JPMorgan Chase & Co. (JPM)
data = yf.download("JPM", start="2017-07-14", end="2022-12-16", multi_level_index=False, auto_adjust=False)
data["Daily Return"] = data["Adj Close"].pct_change(1) * 100
data["Daily Return"] = data["Daily Return"].fillna(0)

# 2. Flatten the multi-row headers
data.columns = data.columns.get_level_values(0)

# 3. ADD THIS LINE: Moves Date to Column 1 and adds Index Numbers to Column 0
data = data.reset_index()
# Plot the trading volume for JPMorgan Chase & Co. stock during the same time period using Plotly Express Library.
def plot_finance_data(df, title):
    # Set x explicitly to 'Date'. 
    # y=df.columns[1:] will plot all columns passed to the function except 'Date'
    fig = px.line(df, x='Date', y=df.columns[1:], title=title)
    
    fig.update_traces(line=dict(width=2))
    fig.update_layout({"plot_bgcolor": "white"})
    filename = f"{title.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png"
    fig.write_image(filename, width=1200, height=600, scale=3)
    print(f" Saved chart image locally as: {filename}")
    fig.show()
# This passes a DataFrame containing only the 'Date' and 'Volume' columns
plot_finance_data(data.iloc[:, [0, 6]], "JPM Stock Trading Volume")

plot_finance_data(data.iloc[:, [0, 7]], "JPM Stock Daily Return")
 # This graph depicts the adjusted closing price, closing price, high, low, and opening price of JPM stock over the specified time period.
plot_finance_data(data.iloc[:, [0, 1, 2, 3, 4, 5]], "JPM Stock Price Data (Close, Adj Close, High, Low, Open)")
print(data.head())

data.describe().round(2)

# Define a funcation that classifies the return based on the magnitude
def percentage_return_classifier(percentage_return):
    if percentage_return > -0.3 and percentage_return < 0.3:
        return "Insignificant Change"
    elif percentage_return > 0.3 and percentage_return <= 3:
        return "Positive Change"
    elif percentage_return > -3 and percentage_return <= -0.3:
        return "Negative Change"
    elif percentage_return > 3 and percentage_return <= 7:
        return "Large Positive Change"
    elif percentage_return > -7 and percentage_return <= -3:
        return "Large Negative Change"
    elif percentage_return > 7:
        return "Bull Run"
    elif percentage_return <= -7:
        return "Bear Selloff"

# Apply the function to the "Daily Return" column and place the results in "Trend" Column
data["Trend"] = data["Daily Return"].apply(percentage_return_classifier)
print(data.head())

# Count the number of occurrences of each trend category
trend_summary = data["Trend"].value_counts()
print(trend_summary)

# Create the figure
plt.figure(figsize=(10, 10))

# Clean up overlaps: This function hides percentages smaller than 2%
def clean_labels(pct):
    return f'{pct:.1f}%' if pct > 2 else ''

# Plot the pie chart using matplotlib directly for better control
plt.pie(
    trend_summary, 
    labels=trend_summary.index, 
    autopct=clean_labels, # Cleans up overlapping text
    startangle=140,
    pctdistance=0.85      # Pushes the percentage text slightly outward
)

plt.title("Distribution of Trend Categories")
plt.tight_layout()     # Automatically adjusts spacing to prevent clipping

# Save the image before showing it
# bbox_inches='tight' ensures labels on the edges don't get cut off
plt.savefig("trend_distribution_pie_chart.png", bbox_inches='tight', dpi=300)
print("Saved pie chart image locally as: trend_distribution_pie_chart.png")

plt.show()

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Calculate the moving average directly using Pandas
data["30-day SMA"] = data["Close"].rolling(window=30).mean()
data["100-day SMA"] = data["Close"].rolling(window=100).mean()

#Create the interactive figure
fig = go.Figure()

#Add the candlestick trace for the stock price (Open, High, Low, Close)
fig.add_trace(go.Candlestick(x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='JPM Candlestick',
                increasing_line_color='green', decreasing_line_color='red'))


# Add the moving average traces
fig.add_trace(go.Scatter(x=data['Date'], y=data['30-day SMA'], mode='lines', name='30-day SMA', line=dict(color='magenta', width=1.5)))
fig.add_trace(go.Scatter(x=data['Date'], y=data['100-day SMA'], mode='lines', name='100-day SMA', line=dict(color='green', width=1.5)))
# Clean up the layout to match the style of the other charts
fig.update_layout(title='JPM Stock Interactive Candlestick Chart with Moving Averages',
                  xaxis_title='Date', yaxis_title='Price ($)', plot_bgcolor='white', xaxis_rangeslider_visible=True)

#Save the Candlestick chart as html file
fig.write_html("jpm_stock_candlestick_chart.html")
print("Saved candlestick chart as HTML locally as: jpm_stock_candlestick_chart.html")

#Display the interactive chart
fig.show()

#Diplay the Bolligner bands on a new candlestick graph. Bollinger bands are powerful technical analysis tool that contains 3 lines: (1) a simmple moving average (middle band, (2) an upper and (3) a lower band. Choose a window length of 20 period and 2 standard deviations for the upper and lower bands. Choose a window length of 20 period and 2 standard deviations.
data["20-day SMA"] = data["Close"].rolling(window=20).mean()
data["20-day STD"] = data["Close"].rolling(window=20).std()
data["Upper Band"] = data["20-day SMA"] + (data["20-day STD"] * 2)
data["Lower Band"] = data["20-day SMA"] - (data["20-day STD"] * 2) 
fig_bb = go.Figure()
fig_bb.add_trace(go.Candlestick(
    x=data['Date'],
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name='JPM Candlestick',
    increasing_line_color='green', 
    decreasing_line_color='red'
))

# Add the Bollinger Bands traces
fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['20-day SMA'], mode='lines', name='20-day SMA', line=dict(color='blue', width=1.5)))
fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['Upper Band'], mode='lines', name='Upper Band', line=dict(color='red', width=1.5)))
fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['Lower Band'], mode='lines', name='Lower Band', line=dict(color='red', width=1.5)))

# Clean up the layout
fig_bb.update_layout(
    title='JPM Stock Interactive Candlestick Chart with Bollinger Bands',
    xaxis_title='Date', 
    yaxis_title='Price ($)', 
    plot_bgcolor='white', 
    xaxis_rangeslider_visible=True
)

# Save the Bollinger Bands chart as an HTML file
fig_bb.write_html("jpm_stock_bollinger_bands.html")
print("Saved Bollinger Bands chart as HTML locally as: jpm_stock_bollinger_bands.html")

# Display the interactive chart
# %%
fig_bb.show()

#data = pd.DataFrame(data)
#data.to_csv("jpm_stock_data.csv", index=False)