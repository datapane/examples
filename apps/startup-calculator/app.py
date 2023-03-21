import altair as alt
import pandas as pd
import datapane as dp

def required_growth_rate(current_cash, initial_revenue, monthly_burn):
    weeks = 24 * 4  # 2 years * 12 months * 4 weeks
    weekly_burn = monthly_burn / 4.345  # Convert the monthly burn to weekly burn

    for growth_rate in range(0, 101):  # Check growth rates between 0% and 100%
        cash_left = current_cash
        is_profitable = True
        for week in range(weeks):
            revenue = initial_revenue * ((1 + growth_rate / 100) ** week)
            cash_left += revenue - weekly_burn

            if cash_left < 0:
                is_profitable = False
                break

        if is_profitable:
            return growth_rate

    return None  # No growth rate found that leads to profitability without running out of money

  
def calculate_runway(
    current_cash: float,
    initial_revenue: float,
    monthly_burn: float,
    weekly_growth_percent: float,
) -> dp.Blocks:
  
    weeks = 104  # 2 years * 52 weeks
    data = []

    for week in range(weeks):
        revenue = initial_revenue * ((1 + weekly_growth_percent / 100) ** week)
        if week == 0:
            cash_left = current_cash + revenue - (monthly_burn / 4)
        else:
            cash_left = data[-1]['Cash_Left'] + revenue - (monthly_burn / 4)
        
        data.append({'Week': week + 1, 'Revenue': revenue, 'Cash_Left': cash_left})

    forecast_df = pd.DataFrame(data)
    
    required_growth = required_growth_rate(current_cash, initial_revenue, monthly_burn)

    # Convert weekly data to monthly data
    forecast_df['Month'] = (forecast_df['Week'] + 3) // 4
    monthly_forecast = forecast_df.groupby('Month').agg({'Revenue': 'sum', 'Cash_Left': 'last'}).reset_index()
    
    # Define a shared base for both charts
    base = alt.Chart(monthly_forecast).encode(
        x=alt.X('Month:Q', title='Month'),
        tooltip=['Month']
    ).properties(title='Revenue and Cash Left Forecast (Monthly)')
    
    # Create a line chart for Revenue using the shared base
    revenue_chart = base.mark_line(color='blue').encode(
        y=alt.Y('Revenue:Q', title='Amount'),
        tooltip=['Month', 'Revenue']
    )
    
    # Create an area chart for Cash Left using the shared base
    cash_chart = base.mark_area(opacity=0.3, color='green').encode(
        y=alt.Y('Cash_Left:Q', title='Amount'),
        tooltip=['Month', 'Cash_Left']
    )
    
    # Combine both charts and make them interactive
    combined_chart = alt.layer(revenue_chart, cash_chart).interactive()
  
    return [
        dp.BigNumber(value=f"{required_growth}%", heading="Required weekly growth rate"),
        combined_chart,
        forecast_df
    ]

# main view and controls
controls = dict(
    current_cash=dp.NumberBox(initial=350000),
    weekly_growth_percent=dp.NumberBox(initial=7),
    initial_revenue=dp.NumberBox(initial=500),
    monthly_burn=dp.NumberBox(initial=35000),
)

v = dp.View(
    "## Finance growth calculator",
    dp.Group(
        dp.Form(
            controls=controls,
            on_submit=calculate_runway,
            target="result"
        ),
        dp.Group(
          dp.Text("Enter your inputs on the left. Your results will appear here."),
          *calculate_runway(current_cash=350000, weekly_growth_percent=7, initial_revenue=500, monthly_burn=35000),
          name='result'
        ),
        columns=2,
        widths=[1, 3],
    ),
)

dp.serve_app(v)
