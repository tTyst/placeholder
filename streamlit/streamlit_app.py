import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import calendar

st.set_page_config(
    page_title="Vega Bryggeri Dashboard",
    page_icon=":beers:",
    initial_sidebar_state="expanded",
)

# CSS to import the font from Google Fonts and apply it
css_code = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    @import url('https://fonts.cdnfonts.com/css/helvetica-neue-5?styles=103502');
    
    html, body, p, div {
        font-family: 'Montserrat', sans-serif;
        font-weight: 400;  // Regular weight for body text
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;  // Bold weight for headings;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Ensure all h3 elements with IDs and their nested spans use the correct font */
    h3[id], h3[id] span {
        font-family: 'Helvetica Neue', sans-serif !important;
    }
    
 
    #vega-bryggeri-dashboard {
        position: relative;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 57px;
        font-weight: 700;
        margin: 0;
        color: transparent; /* Hide the original text */
    }
    
    #vega-bryggeri-dashboard::before {
        content: 'Vega Bryggeri Dashboard';
        position: absolute;
        top: 55px;
        left: 0;
        background: linear-gradient(-135deg, #f670c1, #ffcc90);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
    }
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)



# Initialize the session state for page management if not already set
if 'page' not in st.session_state:
    st.session_state.page = 'Home page'


# Load data function
@st.cache_data()
def load_data(year):
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Build the file path using os.path.join
    file_path = os.path.join(dir_path, f"Artikellistan {year}.xlsx")
    
    # Load the data
    data = pd.read_excel(file_path, header=4)
    return data


# Function to get top sales data for Vega Bryggeri
@st.cache_data()
def get_top_vega_bryggeri(data, top_n=50):
    filtered_data = data[data['Producentnamn'] == 'Vega Bryggeri']
    top_sales = filtered_data.sort_values(by='Försäljning i liter', ascending=False).head(top_n)
    return top_sales


@st.cache_data()
def load_combined_job_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "CCC_datechange.csv")
    data = pd.read_csv(file_path)
    data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
    data['year_month'] = data['publication_date'].dt.to_period('M').astype(str)
    return data


# Function to prepare comparative data
def get_comparative_data():
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    frames = []
    for year in years:
        data = load_data(year)
        total_sales = data[data['Producentnamn'] == 'Vega Bryggeri']['Försäljning i liter'].sum()
        frames.append(pd.DataFrame({'Year': [year], 'Sales in liters': [total_sales]}))
    return pd.concat(frames)

def get_combined_percentage_change_data():
    categories = ["Lageröl", "Säsongsöl", "Specialöl"]
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    results = []

    # Dictionary for Similar Gothenburg Breweries with possible alternate names
    gothenburg_brewery_aliases = {
        "Dugges Bryggeri": ["Dugges Bryggeri", "Dugges Bryggeri AB"],
        "O/O Brewing": ["O/O Brewing", "O/O Brewing AB"],
        "Poppels Bryggeri": ["Poppels Bryggeri", "Poppels Bryggeri AB"],
        "Spike Brewery": ["Spike Brewery", "Spike Brewery AB"],
        "Stigbergets Bryggeri": ["Stigbergets Bryggeri", "Stigbergets Gbg Beer Week"],
        "Beerbliotek": ["Beerbliotek", "Beerbliotek AB"]
    }

    # Dictionary of Non-Gothenburg Breweries with possible alternate names
    non_gbg_brewery_aliases = {
        "Omnipollo": ["Omnipollo", "Omnipollo AB"],
        "Apex Brewing CO": ["Apex Brewing CO"],
        "Brekeriet Beer": ["Brekeriet Beer", "Brekeriet Beer AB"],
        "Oppigårds Bryggeri": ["Oppigårds Bryggeri", "Oppigårds Bryggeri AB"],
        "Brewski": ["Brewski", "Brewski AB"],
        "Nils Oscar": ["Nils Oscar", "Nils Oscar AB"],
        "Hyllie Bryggeri": ["Hyllie Bryggeri", "Hyllie Bryggeri AB"]
    }
    
    # Generate a list of all alternate names for Gothenburg and non-Gothenburg breweries
    similar_breweries = [alias for aliases in gothenburg_brewery_aliases.values() for alias in aliases]
    non_gbg_breweries = [alias for aliases in non_gbg_brewery_aliases.values() for alias in aliases]

    previous_total_excl_vega = None
    previous_vega_sales = None
    previous_similar_sales = None
    previous_non_gbg_sales = None

    for year in years:
        data = load_data(year)
        vega_sales_yearly = 0
        total_sales_yearly = 0
        similar_sales_yearly = 0
        non_gbg_sales_yearly = 0
        
        for category in categories:
            category_data = data[data['Varugrupp detalj'] == category]
            total_sales = category_data['Försäljning i liter'].sum()
            vega_sales = category_data[category_data['Producentnamn'] == 'Vega Bryggeri']['Försäljning i liter'].sum()
            similar_sales = category_data[category_data['Producentnamn'].isin(similar_breweries)]['Försäljning i liter'].sum()
            non_gbg_sales = category_data[category_data['Producentnamn'].isin(non_gbg_breweries)]['Försäljning i liter'].sum()

            vega_sales_yearly += vega_sales
            total_sales_yearly += total_sales
            similar_sales_yearly += similar_sales
            non_gbg_sales_yearly += non_gbg_sales

        other_producers_sales = total_sales_yearly - vega_sales_yearly - similar_sales_yearly - non_gbg_sales_yearly

        if previous_total_excl_vega is not None and previous_vega_sales is not None and previous_similar_sales is not None and previous_non_gbg_sales is not None:
            total_market_change = ((other_producers_sales - previous_total_excl_vega) / previous_total_excl_vega * 100) if previous_total_excl_vega > 0 else 0
            vega_change = ((vega_sales_yearly - previous_vega_sales) / previous_vega_sales * 100) if previous_vega_sales > 0 else 0
            similar_change = ((similar_sales_yearly - previous_similar_sales) / previous_similar_sales * 100) if previous_similar_sales > 0 else 0
            non_gbg_change = ((non_gbg_sales_yearly - previous_non_gbg_sales) / previous_non_gbg_sales * 100) if previous_non_gbg_sales > 0 else 0
        else:
            total_market_change = 0
            vega_change = 0
            similar_change = 0
            non_gbg_change = 0

        results.append({
            'Year': year,
            'Vega Bryggeri Change %': vega_change,
            'Total Market Change %': total_market_change,
            'Similar Gothenburg Breweries Change %': similar_change,
            'Non-Gothenburg Breweries Change %': non_gbg_change,
            'Vega Bryggeri Sales': vega_sales_yearly,
            'Other Producers Sales': other_producers_sales,
            'Similar Gothenburg Breweries Sales': similar_sales_yearly,
            'Non-Gothenburg Breweries Sales': non_gbg_sales_yearly
        })

        previous_total_excl_vega = other_producers_sales
        previous_vega_sales = vega_sales_yearly
        previous_similar_sales = similar_sales_yearly
        previous_non_gbg_sales = non_gbg_sales_yearly

    return pd.DataFrame(results)


# Sidebar
st.sidebar.title("Category menu")
# Buttons for page navigation
if st.sidebar.button("Home page"):
    st.session_state.page = 'Home page'
if st.sidebar.button("Job Postings Data"):
    st.session_state.page = 'Job Postings Data'
if st.sidebar.button("Systembolaget data"):
    st.session_state.page = 'Systembolaget data'
if st.sidebar.button("CCI Data"):
    st.session_state.page = 'CCI Data'

# Display content based on the current page
if st.session_state.page == "CCI Data":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'CCI_kategorier.xlsx')

    # Load the CCI Data provided by the user
    cci_data_cleaned = pd.read_excel(file_path)

    # Rename columns for clarity
    cci_data_cleaned.columns = ['Indicator'] + pd.to_datetime(cci_data_cleaned.columns[1:]).tolist()

    # Melt the dataframe to a long format
    cci_data_long = cci_data_cleaned.melt(id_vars=['Indicator'], var_name='Date', value_name='Value')

    # Convert the Date column to datetime format
    cci_data_long['Date'] = pd.to_datetime(cci_data_long['Date'])

    # Remove any leading/trailing spaces in the Indicator names
    cci_data_long['Indicator'] = cci_data_long['Indicator'].str.strip()

    # Filter out rows with missing 'Value' and 'Indicator'
    cci_data_long = cci_data_long.dropna(subset=['Value', 'Indicator'])

    # Convert 'Value' to numeric
    cci_data_long['Value'] = pd.to_numeric(cci_data_long['Value'], errors='coerce')

    # Add a quarter column and convert to string format
    cci_data_long['Quarter'] = cci_data_long['Date'].dt.to_period('Q').astype(str)


if st.session_state.page == "Systembolaget data":
    st.subheader("Systembolaget data Dashboard")
    tab1, tab2, tab3 = st.tabs(["Yearly statistics", "Comparison by year", "Annual Percentage Change Comparison"])

    with tab1:
        st.markdown("""
                ### Top Products from Vega Bryggeri by Sales Volume
                This graph shows the top products from Vega Bryggeri based on their sales volume for the selected year. 
                Use the slider to adjust the number of top products displayed. The sales volume is measured in liters.
                """)

        year = st.selectbox("Select Year", (2023, 2022, 2021, 2020, 2019, 2018))
        data = load_data(year)
        
        # Slider to select the number of top beers to display
        number_of_beers = st.slider("Select number of top beers to display", min_value=1, max_value=50, value=10)
        
        top_vega = get_top_vega_bryggeri(data, top_n=number_of_beers)
        
        fig = px.bar(top_vega, x='Kvittonamn', y='Försäljning i liter',
                    title=f"Top {number_of_beers} Products from Vega Bryggeri by Sales Volume",
                    color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca']
                    )
        st.plotly_chart(fig, use_container_width=True)

        # Rename the columns for display and select only the desired columns
        top_vega_display = top_vega.rename(columns={
            'Kvittonamn': 'Product Name',
            'Producentnamn': 'Producer Name',
            'Försäljning i liter': 'Sales in Liters',
            'Varugrupp detalj': 'Product Group'
        })[['Product Name','Sales in Liters', 'Product Group']]

        top_vega_display = top_vega_display.reset_index(drop=True)
        top_vega_display.index = top_vega_display.index + 1
        st.dataframe(top_vega_display)


    with tab2:
        st.markdown("""
                ### Sales Comparison Over Years
                This line chart compares the sales volume over different years. It helps to visualize the trend in sales volume across the years.
                """)

        comparative_data = get_comparative_data()
        fig2 = px.line(comparative_data, x='Year', y='Sales in liters', title='Sales Comparison Over Years',
                       color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca'])
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("""
                ### Annual Market Share Change Percentage
                This line chart shows the annual percentage change in market share compared to the previous year. It includes Vega Bryggeri, the total market, similar Gothenburg breweries, and non-Gothenburg breweries.
                """)

        percentage_data = get_combined_percentage_change_data()
        
        # Filter out the year 2018
        percentage_data_filtered = percentage_data[percentage_data['Year'] != 2018]
        
        fig3 = px.line(
            percentage_data_filtered,
            x='Year',
            y=['Vega Bryggeri Change %', 'Total Market Change %', 'Similar Gothenburg Breweries Change %', 'Non-Gothenburg Breweries Change %'],
            title='Annual Market Share Change Percentage compared to previous year',
            color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca']  # Cerulean Blue, Coral Red, Mustard Yellow, Teal
        )
        # Adjust figure size and x-axis range
        fig3.update_layout(
            legend=dict(
                title='Click to hide/show:',  # Adding a title to the legend
            ),
            yaxis=dict(
                zeroline=True,  # Ensure the zero line is visible
                zerolinewidth=1,  # Make the zero line more visible
                zerolinecolor='grey',  # Set zero line color
                gridcolor="grey"
            ),
            xaxis=dict(
                range=[2019, 2023],  # Extend range beyond your actual data for padding
                tickvals=[2019, 2020, 2021, 2022, 2023],  # Explicitly set tick values to ensure they appear
            ),
            width=965  # Adjust width to your preference
        )

        st.plotly_chart(fig3, use_container_width=False)  # Set use_container_width to False to use manual width
        st.dataframe(percentage_data_filtered[['Year', 'Vega Bryggeri Change %', 'Total Market Change %', 'Similar Gothenburg Breweries Change %', 'Non-Gothenburg Breweries Change %']])



if st.session_state.page == "Home page":
    st.title("Vega Bryggeri Dashboard")
    st.write("Welcome to the Vega Bryggeri Dashboard! This dashboard provides insights into the sales data of Vega Bryggeri and other breweries in the region.")

if st.session_state.page == "Job Postings Data":
    st.subheader("Job Data Analysis")

    tab1, tab2 = st.tabs(["Employment type Timeline", "Job Listings Prognosis"])

    with tab1:
        data = load_combined_job_data()
        data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
        data['year_quarter'] = data['publication_date'].dt.to_period('Q').astype(str)
        data['year_month'] = data['publication_date'].dt.to_period('M').astype(str)
        data['year'] = data['publication_date'].dt.year

        data.rename(columns={
            'cluster': 'Employment type',
            'publication_date': 'Publication Date',
            'year_quarter': 'Year-Quarter',
            'year_month': 'Year-Month',
            'year': 'Year'
        }, inplace=True)

        data.dropna(subset=['Employment type', 'Publication Date'], inplace=True)

        # Group by year_quarter and cluster, and count the number of rows for each group
        cluster_counts = data.groupby(['Year-Quarter', 'Employment type']).size().reset_index(name='Count')

        # Create a full range of Year-Quarters
        all_quarters = pd.period_range(start=cluster_counts['Year-Quarter'].min(), end=cluster_counts['Year-Quarter'].max(), freq='Q').astype(str)
        
        # Create a dataframe with all possible combinations of Year-Quarters and Employment types
        all_combinations = pd.MultiIndex.from_product([all_quarters, cluster_counts['Employment type'].unique()], names=['Year-Quarter', 'Employment type'])
        full_cluster_counts = cluster_counts.set_index(['Year-Quarter', 'Employment type']).reindex(all_combinations, fill_value=0).reset_index()
        
        # Add context text
        st.markdown("""
        ### Employment type Timeline Over Quarters
        This line chart illustrates the distribution of different employment types over the quarters.
        It helps in understanding hiring trends and the demand for various types of employment over time.
        Use the chart to identify seasonal patterns or shifts in employment types.
        """)

        # Create a line chart for the clusters over time
        fig = px.line(full_cluster_counts, x='Year-Quarter', y='Count', color='Employment type', 
                      title='Employment type Timeline Over Quarters',
                      labels={'Year-Quarter': 'Year-Quarter', 'Count': 'Count', 'Employment type': 'Employment type'},
                      color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca'])

        fig.update_xaxes(
            tickangle=45,
            nticks=20,
            tickformat='%Y-Q%q'
        )
        
        double_tick_vals = np.arange(0, 25, 1)

        fig.update_layout(
            legend=dict(
                title='Click to hide/show:',  # Adding a title to the legend
            ),
            yaxis=dict(
                zerolinewidth=1,  # Make the zero line more visible
                zerolinecolor='grey',  # Set zero line color
                gridcolor="rgba(128, 128, 128, 0.5)"  # Set grid line color with 50% opacity
            ),
            xaxis=dict(
                showgrid=True,  # Enable grid lines for the x-axis
                gridcolor="rgba(128, 128, 128, 0.5)",  # Set the grid line color with 50% opacity
                gridwidth=1,  # Set the grid line width
                tickvals=double_tick_vals,  # Set custom tick positions
            )
        )
      
        st.plotly_chart(fig, use_container_width=True)

        # Sort the years before displaying in the selectbox
        years = sorted(data['Year'].unique())
        selected_year = st.selectbox('Select Year to Filter Monthly Data', years)
        filtered_data = data[data['Year'] == selected_year]

        # Display the month-wise data in a pie chart
        st.write("Monthly Data")
        monthly_counts = filtered_data.groupby(['Year-Month', 'Employment type']).size().reset_index(name='Count')

        # Create a dictionary to map "YYYY-MM" to the month name
        monthly_counts['Month'] = monthly_counts['Year-Month'].apply(lambda x: calendar.month_name[int(x[-2:])])

        selected_month = st.selectbox('Select Month to Filter Data', monthly_counts['Month'].unique())
        month_filtered_data = monthly_counts[monthly_counts['Month'] == selected_month]

        # Create pie chart
        pie_fig = go.Figure(data=[go.Pie(labels=month_filtered_data['Employment type'], values=month_filtered_data['Count'], textinfo='label+percent', insidetextorientation='radial')])
        pie_fig.update_layout(title_text=f'Distribution of Employment Types for {selected_month}', title_y=0.98)

        st.plotly_chart(pie_fig, use_container_width=True)




    with tab2:
        st.write("""
        ### Job Listings and Forecasts Over Time
        This graph presents the job listings and forecasts for all job postings, including a specific focus on the restaurant industry. 
        Shaded areas around the forecast lines indicate the confidence intervals, showing the range within which the ***actual values are expected to fall.***
        """)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_all_jobs = os.path.join(base_dir, 'forecast_data.csv')
        file_restaurant_jobs = os.path.join(base_dir, 'forecast_data_restaurant.csv')

        # Manually specify the correct columns and ignore extraneous columns
        correct_columns = ['publication_date', 'job_listings', 'forecast', 'lower', 'upper']
        df_all_jobs = pd.read_csv(file_all_jobs, usecols=[0, 1, 2, 3, 4], names=correct_columns, header=0)
        df_restaurant_jobs = pd.read_csv(file_restaurant_jobs, usecols=[0, 1, 2, 3, 4], names=correct_columns, header=0)

        # Convert publication_date to datetime
        df_all_jobs['publication_date'] = pd.to_datetime(df_all_jobs['publication_date'], errors='coerce')
        df_restaurant_jobs['publication_date'] = pd.to_datetime(df_restaurant_jobs['publication_date'], errors='coerce')

        # Filter the data within the specified date range
        start_date = '2023-12-01'
        end_date = '2024-06-30'

        # Create the figure
        fig_with_forecast_range_corrected = go.Figure()

        # Add traces for all job listings and Industry Related Job Listing with markers
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_all_jobs['publication_date'],
            y=df_all_jobs['job_listings'],
            mode='lines',
            name='All Job Listings',
            line=dict(color='red', dash='solid'),
        ))

        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_restaurant_jobs['publication_date'],
            y=df_restaurant_jobs['job_listings'],
            mode='lines',
            name='Industry Related Job Listing',
            line=dict(color='green', dash='solid'),
        ))

        # Add traces for all job listings forecast and Industry Related Job Listing forecast with different line styles
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_all_jobs['publication_date'],
            y=df_all_jobs['forecast'],
            mode='lines',
            name='All Job Listings Forecast',
            line=dict(dash='dash', color='indianred'),
        ))

        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_restaurant_jobs['publication_date'],
            y=df_restaurant_jobs['forecast'],
            mode='lines',
            name='Industry Related Job Listing Forecast',
            line=dict(dash='dash', color='lightgreen'),
        ))

        # Add confidence interval for all job listings
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_all_jobs['publication_date'].tolist() + df_all_jobs['publication_date'].tolist()[::-1],
            y=df_all_jobs['upper'].tolist() + df_all_jobs['lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='Confidence Interval All Jobs',
            hoverinfo='skip',
            showlegend=False,
        ))

        # Add lower and upper bounds for all job listings with hover info
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_all_jobs['publication_date'],
            y=df_all_jobs['lower'],
            mode='lines',
            line=dict(color='rgba(255, 0, 0, 0.2)'),
            name='Lower Bound All Jobs',
            showlegend=False,
            hoverinfo='y+name',
        ))

        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_all_jobs['publication_date'],
            y=df_all_jobs['upper'],
            mode='lines',
            line=dict(color='rgba(255, 0, 0, 0.2)'),
            name='Upper Bound All Jobs',
            showlegend=False,
            hoverinfo='y+name',
        ))

        # Add confidence interval for industry related job listings
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_restaurant_jobs['publication_date'].tolist() + df_restaurant_jobs['publication_date'].tolist()[::-1],
            y=df_restaurant_jobs['upper'].tolist() + df_restaurant_jobs['lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 255, 0, 0.2)',
            line=dict(color='rgba(0, 255, 0, 0)'),
            name='Confidence Interval Industry Jobs',
            hoverinfo='skip',
            showlegend=False,
        ))

        # Add lower and upper bounds for industry related job listings with hover info
        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_restaurant_jobs['publication_date'],
            y=df_restaurant_jobs['lower'],
            mode='lines',
            line=dict(color='rgba(0, 255, 0, 0.2)'),
            name='Lower Bound Industry Jobs',
            showlegend=False,
            hoverinfo='y+name',
        ))

        fig_with_forecast_range_corrected.add_trace(go.Scatter(
            x=df_restaurant_jobs['publication_date'],
            y=df_restaurant_jobs['upper'],
            mode='lines',
            line=dict(color='rgba(0, 255, 0, 0.2)'),
            name='Upper Bound Industry Jobs',
            showlegend=False,
            hoverinfo='y+name',
        ))

        # Update layout with the specified date range and log scale for y-axis
        fig_with_forecast_range_corrected.update_layout(
            title='Job Listings and Forecasts Over Time',
            xaxis_title='Publication Date',
            yaxis_title='Job Listings',
            legend_title='Job Type',
            xaxis=dict(
                tickangle=-45,
                dtick="M1",  # setting the tick interval to monthly for the specific range
                tickformat="%Y-%m",
                range=[start_date, end_date],
                showgrid=True,  # Show gridlines for x-axis
                gridwidth=1,
            ),
            yaxis=dict(
                type='log',  # Set the y-axis to a log scale
                tickformat=",d",
                title='Job Listings',
                showgrid=True,  # Show gridlines for y-axis
                gridwidth=2,
            ),
            hovermode='x unified'  # Set hover mode to 'x unified'
        )

        st.plotly_chart(fig_with_forecast_range_corrected)



if st.session_state.page == "CCI Data":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'CCI_kategorier.xlsx')

    # Load the CCI Data provided by the user
    cci_data_cleaned = pd.read_excel(file_path)

    # Rename columns for clarity
    cci_data_cleaned.columns = ['Indicator'] + pd.to_datetime(cci_data_cleaned.columns[1:]).tolist()

    # Melt the dataframe to a long format
    cci_data_long = cci_data_cleaned.melt(id_vars=['Indicator'], var_name='Date', value_name='Value')

    # Convert the Date column to datetime format
    cci_data_long['Date'] = pd.to_datetime(cci_data_long['Date'])

    # Remove any leading/trailing spaces in the Indicator names
    cci_data_long['Indicator'] = cci_data_long['Indicator'].str.strip()

    # Filter out rows with missing 'Value' and 'Indicator'
    cci_data_long = cci_data_long.dropna(subset=['Value', 'Indicator'])

    # Convert 'Value' to numeric
    cci_data_long['Value'] = pd.to_numeric(cci_data_long['Value'], errors='coerce')

    # Add a quarter column and convert to string format
    cci_data_long['Quarter'] = cci_data_long['Date'].dt.to_period('Q').astype(str)

    # Add context text
    st.markdown("""
    ### Consumer Confidence Index Data
    The Consumer Confidence Index (CCI) measures the level of optimism that consumers feel about the overall state of the economy 
    and their personal financial situation. This data is crucial for understanding consumer behavior and economic trends.
    Below are analyses based on the CCI data. **100** is the baseline value for the index, with values above 100 indicating optimism.
    """)

    # Create the line plot
    fig_trend = px.line(cci_data_long, 
                        x='Quarter', y='Value',
                        color='Indicator', 
                        title='Consumer Confidence Index Over Time by Indicator',
                        color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca'])

    # Add a trace for the 100 baseline to make it interactive
    fig_trend.add_trace(go.Scatter(
        x=cci_data_long['Quarter'],
        y=[100] * len(cci_data_long),
        mode='lines',
        line=dict(color="LightSeaGreen", width=2, dash="dash"),
        name='Baseline (100)'
    ))

    st.plotly_chart(fig_trend)

    # 2. Category Comparison
    st.markdown("""
    #### Category Comparison
    Select a year and quarter to compare the Consumer Confidence Index across different categories. 
    This bar chart provides a snapshot of consumer confidence in various sectors for the selected period.
    """)

    # Extract unique years and quarters
    cci_data_long['Year'] = cci_data_long['Date'].dt.year
    cci_data_long['Quarter'] = cci_data_long['Date'].dt.quarter

    unique_years = cci_data_long['Year'].unique()
    unique_quarters = ['Q1', 'Q2', 'Q3', 'Q4']

    # Dropdown menus for year and quarter
    selected_year = st.selectbox('Select Year for Category Comparison', sorted(unique_years))
    selected_quarter = st.selectbox('Select Quarter for Category Comparison', unique_quarters)

    # Map quarter names back to integers for filtering
    quarter_mapping = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
    selected_quarter_int = quarter_mapping[selected_quarter]

    # Filter the data for the selected year and quarter
    filtered_data = cci_data_long[(cci_data_long['Year'] == selected_year) & 
                                (cci_data_long['Quarter'] == selected_quarter_int)]

    # Create the bar chart
    fig_category_comparison = px.bar(
        filtered_data, 
        x='Indicator', 
        y='Value', 
        title=f'Consumer Confidence Index by Category for {selected_quarter} {selected_year}',
        color='Indicator',  # Use different colors for each bar
        color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b']  # Your specified colors
    )
    st.plotly_chart(fig_category_comparison)


# Footer
st.markdown("---")
st.markdown("Created by Algorithm Avengers with :heart: for Vega Bryggeri.")

if __name__ == "__main__":
    def main():
        pass  # Main function definition is empty as Streamlit runs script top-down

    main()
