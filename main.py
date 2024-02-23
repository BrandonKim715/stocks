#import libraries
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore", category=FutureWarning)

#Select Stocks
#Wouldn't recommend more than 5 just for clarity in graphs
#example: FAANG stocks
def symbols():
    stocks = input("Enter all stocks you want to add to your Portfolio.\nEnter legal Stock Ticker Symbols and separate each stock with a space(EX: META AMZN AAPL NFLX GOOG): ")
    stock_symbols = stocks.split(" ")
    return stock_symbols

#Set Time Period to explore
#Must be a valid time when stocks were traded
def time_period():
    start = input("Enter a valid date in the format of Year-Month-Day(EX: 2020-01-01): ")
    end = input("Enter a valid date in the format of Year-Month-Day(EX: 2021-01-01): ")
    start_date = start
    end_date = end
    return start_date, end_date

#Resample data to monthly frequency
#Drop empty rows
def monthly_returns(stock_symbols, start_date, end_date):
    stock_data = yf.download(stock_symbols, start=start_date, end=end_date)
    stock_data_monthly = stock_data['Adj Close'].resample('M').ffill()
    stock_returns = stock_data_monthly.ffill().pct_change().dropna()

    #Calculate return percentage
    #Add a row for start date where return value is 0
    returns_by_month = stock_returns.resample('MS').apply(lambda x: (1 + x).prod() - 1) * 100
    start_data = pd.DataFrame({stock: 0 for stock in stock_symbols}, index=[pd.Timestamp(start_date)])
    returns_by_month = pd.concat([start_data, returns_by_month]).sort_index()
    return stock_data,returns_by_month

def stock_returns(returns_by_month):
    #Calculate return percentage by Stock
    sums = []
    for stock in returns_by_month:
        total_return = 1
        for value in returns_by_month[stock]:
            total_return *= (1+value/100)
        sums.append([stock, round(((total_return-1)/1)*100,2)])
    sum_by_stock = pd.DataFrame(sums, columns=["Stock", "Return(%)"])
    return sum_by_stock

#Create a portfolio where each stock has equal weight
def portfolio(stock_symbols, start_date, end_date, returns_by_month):
    num_stocks = len(stock_symbols)
    weights = np.array([1 / num_stocks] * num_stocks)
    portfolio = pd.DataFrame(data=(returns_by_month * weights).sum(axis=1))
    total_return = 1
    for value in portfolio.get(0):
        total_return *= (1+value/100)
    return_percentage = ((total_return-1)/1)*100
    return portfolio, return_percentage

#Plot individual stocks on a line chart to compare performance
def plot_stocks(returns_by_month):
    #Initialize Stocks Plot
    plt.figure(figsize=(10,6))
    for column in returns_by_month.columns:
        plt.plot(returns_by_month.index, returns_by_month[column], label=column)

    #Set Titles/Labels
    plt.title('Stock Returns')
    plt.xlabel('Time(Months/Years)')
    plt.ylabel('Returns (%)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

#Plot portfolio performance
def plot_portfolio(portfolio):
    #Initalize Portfolio Plot
    plt.figure(figsize=(12, 6))
    ax = plt.subplot(111)
    portfolio.plot(ax=ax, marker='o', linestyle='-')
    plt.title('Portfolio Returns')
    plt.xlabel("Time(Months/Years)")
    plt.ylabel('Returns (%)')
    plt.legend().remove()
    plt.grid(True)
    for i, (date, return_value) in enumerate(zip(portfolio.index, portfolio.iloc[:, 0])):
        ax.annotate(f'{return_value:.2f}%', (date, return_value), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.show()

#Export Stock Info to a CSV File
#Use Data to find patterns/make predictions
def export_info(dataframe):
    change = input("Would you like the stock information as a csv file? (Yes/No) ")
    if change == 'Yes':
        dataframe.to_csv("stock_info.csv", index_label='Date')
        print("Done")
    else:
        end

if __name__ == "__main__":
    stock = symbols()
    start, end = time_period()
    data, returns = monthly_returns(stock, start, end)
    cumulative = stock_returns(returns)
    print(cumulative) #Get return percentage of stock over time
    plot_stocks(returns)
    port,return_per = portfolio(stock, start, end, returns)
    print("Total Portfolio Return: {:.2f}%".format(return_per))
    plot_portfolio(port)
    export_info(data)