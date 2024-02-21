import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime


st.set_page_config(
    page_title="Financial Planning Calculator")

st.title("Financial Planning Calculator")

st.header("**Monthly Income**")
st.subheader("Salary")
colAnnualSal, colTax = st.columns(2)

with colAnnualSal:
    salary = st.number_input("Enter your annual salary($): ", min_value=0.0, format='%f')
with colTax:
    tax_rate = st.number_input("Enter your tax rate(%): ", min_value=0.0, format='%f')

tax_rate = tax_rate / 100.0
salary_after_taxes = salary * (1 - tax_rate)
monthly_takehome_salary = round(salary_after_taxes / 12.0, 2)

st.header("**Monthly Expenses**")
colExpenses1, colExpenses2 = st.columns(2)

with colExpenses1:
    st.subheader("Monthly Rental")
    monthly_rental = st.number_input("Enter your monthly rental($): ", min_value=0.0,format='%f' )

    st.subheader("Daily Food Budget")
    daily_food = st.number_input("Enter your daily food budget ($): ", min_value=0.0,format='%f' )
    monthly_food = daily_food * 30

    st.subheader("Monthly Unforeseen Expenses")
    monthly_unforeseen = st.number_input("Enter your monthly unforeseen expenses ($): ", min_value=0.0,format='%f' )

with colExpenses2:
    st.subheader("Monthly Transport")
    monthly_transport = st.number_input("Enter your monthly transport fee ($): ", min_value=0.0,format='%f' )

    st.subheader("Monthly Utilities Fees")
    monthly_utilities = st.number_input("Enter your monthly utilities fees ($): ", min_value=0.0,format='%f' )

    st.subheader("Monthly Entertainment Budget")
    monthly_entertainment = st.number_input("Enter your monthly entertainment budget ($): ", min_value=0.0,format='%f' )

monthly_expenses = monthly_rental + monthly_food + monthly_transport + monthly_entertainment + monthly_utilities + monthly_unforeseen
monthly_savings = monthly_takehome_salary - monthly_expenses

st.header("**Savings**")
st.subheader("Monthly Take Home Salary: $" + str(round(monthly_takehome_salary,2)))
st.subheader("Monthly Expenses: $" + str(round(monthly_expenses, 2)))
st.subheader("Monthly Savings: $" + str(round(monthly_savings, 2)))

st.markdown("---")

st.header("**Forecast Savings**")
colForecast1, colForecast2 = st.columns(2)
with colForecast1:
    st.subheader("Forecast Year")
    forecast_year = st.number_input("Enter your forecast year (Min 1 year): ", min_value=0,format='%d')
    forecast_months = 12 * forecast_year

    st.subheader("Annual Inflation Rate")
    annual_inflation = st.number_input("Enter annual inflation rate (%): ", min_value=0.0,format='%f')
    monthly_inflation = (1+annual_inflation)**(1/12) - 1
    cumulative_inflation_forecast = np.cumprod(np.repeat(1 + monthly_inflation, forecast_months))
    forecast_expenses = monthly_expenses*cumulative_inflation_forecast
with colForecast2:
    st.subheader("Annual Salary Growth Rate")
    annual_growth = st.number_input("Enter your expected annual salary growth (%): ", min_value=0.0,format='%f')
    monthly_growth = (1 + annual_growth) ** (1/12) - 1
    cumulative_salary_growth = np.cumprod(np.repeat(1 + monthly_growth, forecast_months))
    forecast_salary = monthly_takehome_salary * cumulative_salary_growth

forecast_savings = forecast_salary - forecast_expenses
cumulative_savings = np.cumsum(forecast_savings)

x_values = np.arange(forecast_year + 1)

fig = go.Figure()
fig.add_trace(
        go.Scatter(
            x=x_values,
            y=forecast_salary,
            name="Forecast Salary"
        )
    )

fig.add_trace(
        go.Scatter(
            x=x_values,
            y=forecast_expenses,
            name= "Forecast Expenses"
        )
    )

fig.add_trace(
        go.Scatter(
                x=x_values,
                y=cumulative_savings,
                name= "Forecast Savings"
            )
    )
fig.update_layout(title='Forecast Salary, Expenses & Savings Over the Years',
                   xaxis_title='Year',
                   yaxis_title='Amount($)')

st.plotly_chart(fig, use_container_width=True)

# Display pie chart for Expenses or Savings breakdown
selected_chart = "Expenses Breakdown"

if selected_chart == "Expenses Breakdown":
    labels = ['Rent', 'Food', 'Transport', 'Utilities', 'Entertainment', 'Unforeseen']
    values = [monthly_rental, monthly_food, monthly_transport, monthly_utilities, monthly_entertainment, monthly_unforeseen]
    chart_title = "Monthly Expenses Breakdown"

fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])

fig_pie.update_layout(title=chart_title)

st.plotly_chart(fig_pie, use_container_width=True)


st.markdown("---")
st.header("**Investments**")
def get_historical_data(ticker):
    try:
        if not ticker:
            return None
        stock_data = yf.download(ticker, period="10y")
        if stock_data.empty:
            st.error(f"No data available for {ticker}. Please enter a valid ticker.")
            return None
        elif 'Adj Close' in stock_data.columns:
            return stock_data['Adj Close']
        else:
            st.error(f"Data for {ticker} is not available.")
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching data for {ticker}")
        return None

def calculate_average_annual_return(ticker2):
    closing_prices = get_historical_data(ticker2)
    if closing_prices is None:
        return None
    log_returns = np.log(closing_prices / closing_prices.shift(1)).dropna()
    average_daily_return = log_returns.mean()
    average_annual_return = average_daily_return * 252
    return average_annual_return * 100

def visualize_returns(tickers):
    fig = go.Figure()
    for ticker in tickers:
        data = get_historical_data(ticker)
        if data is not None:
            fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', name=ticker))
    fig.update_layout(title="Historical Adjusted Close Prices", xaxis_title="Date", yaxis_title="Adjusted Close Price")
    st.plotly_chart(fig, use_container_width=True)

# Dynamic Ticker Input
tickers = []
while True:
    new_ticker = st.text_input("Enter Ticker:", key=len(tickers))
    if not new_ticker:
        break
    tickers.append(new_ticker)

valid_tickers = []
individual_returns = []

for ticker in tickers:
    average_annual_return = calculate_average_annual_return(ticker)
    if average_annual_return is not None:
        annual_return = average_annual_return
        individual_returns.append(annual_return)
        valid_tickers.append(ticker)
        st.write(f"Average Annual Return for {ticker} is: {annual_return:.2f}%")
    else:
        st.write(f"")

if individual_returns:
    overall_average_return = sum(individual_returns) / len(individual_returns)
    st.write(f"\nOverall Average Annual Return for the Portfolio is: {overall_average_return:.2f}%")
    visualize_returns(valid_tickers)
else:
    st.write("No valid tickers entered. Please enter at least one valid ticker.")


st.markdown("---")
st.header("**Net Worth Projection**")

projection_years = st.number_input("Enter the number of years for net worth projection:", min_value=1, format='%d', key="projection_years")
monthly_contribution = st.number_input("Enter your monthly contribution to the portfolio ($):", min_value=0.0, format='%f', key="monthly_portfolio_contribution")

# Initializing variables for net worth projection calculations
# These should be calculated based on user inputs from previous sections of the app
initial_savings = 0  # This is a placeholder, replace with actual calculation if available
average_return = overall_average_return if individual_returns else .01  # Use calculated return or a default
# Define the current year as the start year
start_year = datetime.now().year

def project_net_worth(projection_years, monthly_contribution, average_return,):
    months = projection_years * 12
    savings_projection = np.zeros(months)
    investment_projection = np.zeros(months)

    annual_return_rate = average_return / 100 # /100 gets rid of percentage

    investment_balance = 0

    for i in range(months):
        # Calculate new monthly savings based on the salary growth

        # Update savings projection

        # Update investment balance with monthly contribution and apply monthly return
        investment_balance = (investment_balance + monthly_contribution * 12 ) * (1 + annual_return_rate)
        investment_projection[i] = investment_balance

    # Total net worth is the sum of savings and investments
    total_net_worth = investment_projection
    return investment_projection


# Calculate projections
investment_projection = project_net_worth(
    projection_years,
    monthly_contribution,
    average_return,
)

# Visualization with corrected x-axis values
x_values = np.arange(start_year, start_year + projection_years)
fig = go.Figure()
fig.add_trace(go.Bar(x=x_values, y=investment_projection, name='Investment Contribution', marker_color='rgb(26, 118, 255)'))

# Rest of the plot configuration
fig.update_layout(
    title='Projected Portfolio Value Over Time',
    xaxis=dict(
        title='Year',
        tickmode='array',
        tickvals=x_values,
        ticktext=[str(year) for year in x_values]
    ),
    yaxis=dict(
        title='Net Worth ($)',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    barmode='stack',
    bargap=0.15,
    bargroupgap=0.1
)

st.plotly_chart(fig, use_container_width=True)

final_portfolio_value = investment_projection[projection_years - 1]
annual_inflation_rate = annual_inflation / 100
portfolio_present_value = final_portfolio_value / (1 + annual_inflation_rate) ** projection_years

st.subheader(f"Portfolio value in {projection_years} years is ${final_portfolio_value:,.0f}")
st.subheader(f"Present value of portfolio is ${portfolio_present_value:,.0f}")
