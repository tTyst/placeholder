import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# CSS to import the font from Google Fonts and apply it
font_url = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap'
css_code = f"""
<link href='{font_url}' rel='stylesheet'>
<style>
    html, body, h1, h2, h3, h4, h5, h6, p, div {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 400;  // Regular weight for body text
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 700;  // Bold weight for headings
    }}
</style>
"""

# Inject the CSS with the font into the Streamlit app
st.markdown(css_code, unsafe_allow_html=True)


# Initialize the session state for page management if not already set
if 'page' not in st.session_state:
    st.session_state.page = 'Home page'

# Main content
st.header("Vega Bryggeri Dashboard")
st.markdown("With this dashboard, the goal is to provide Vega Bryggeri with insights into various types of data.")

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
    data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce', infer_datetime_format=True)
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
st.sidebar.title("Menu")
# Buttons for page navigation
if st.sidebar.button("Home page"):
    st.session_state.page = 'Home page'
if st.sidebar.button("Placeholder 2"):
    st.session_state.page = 'Placeholder 2'
if st.sidebar.button("Systembolaget data"):
    st.session_state.page = 'Systembolaget data'
if st.sidebar.button("Placeholder 3"):
    st.session_state.page = 'Placeholder 3'

# Display content based on the current page
if st.session_state.page == "Systembolaget data":
    st.subheader("Systembolaget data Dashboard")
    tab1, tab2, tab3 = st.tabs(["Yearly statistics", "Comparsion by year", "Annual Percentage Change Comparison"])

    with tab1:
        year = st.selectbox("Select Year", (2023, 2022, 2021, 2020, 2019, 2018))
        data = load_data(year)
        
        # Slider to select the number of top beers to display
        number_of_beers = st.slider("Select number of top beers to display", min_value=1, max_value=50, value=10)
        
        top_vega = get_top_vega_bryggeri(data, top_n=number_of_beers)
        fig = px.bar(top_vega, x='Namn', y='Försäljning i liter',
                    title=f"Top {number_of_beers} Products from Vega Bryggeri by Sales Volume",
                    color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca']
                    )
        st.plotly_chart(fig, use_container_width=True)
        top_vega = top_vega[['Kvittonamn', 'Producentnamn', 'Försäljning i liter', 'Varugrupp detalj']].reset_index(drop=True)
        # Increment the index to start from 1 instead of 0
        top_vega.index = top_vega.index + 1
        st.dataframe(top_vega)


    with tab2:
        comparative_data = get_comparative_data()
        fig2 = px.line(comparative_data, x='Year', y='Sales in liters', title='Sales Comparison Over Years',
                       color_discrete_sequence=['#1f77b4', '#ff6b6b', '#ffc13b', '#30e3ca'])
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        percentage_data = get_combined_percentage_change_data()
        fig3 = px.line(
        percentage_data,
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
                range=[2018, 2023.],  # Extend range beyond your actual data for padding
                tickvals=[2018, 2019, 2020, 2021, 2022, 2023],  # Explicitly set tick values to ensure they appear
            ),
            width=965  # Adjust width to your preference
)



        st.plotly_chart(fig3, use_container_width=False)  # Set use_container_width to False to use manual width
        st.dataframe(percentage_data[['Year', 'Vega Bryggeri Change %', 'Total Market Change %', 'Similar Gothenburg Breweries Change %', 'Non-Gothenburg Breweries Change %']])


if st.session_state.page == "Home page":
    st.write("Information about Vega Bryggeri.")

if st.session_state.page == "Placeholder 2":
    st.subheader("Job Data Analysis")

    tab1, tab2 = st.tabs(["Employment type Timeline", "Other Analysis"])

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

        # Create a line chart for the clusters over time
        fig = px.line(full_cluster_counts, x='Year-Quarter', y='Count', color='Employment type', 
                      title='Employment type Timeline Over Quarters',
                      labels={'Year-Quarter': 'Year-Quarter', 'Count': 'Count', 'Employment type': 'Employment type'})

        fig.update_xaxes(
            tickangle=45,
            nticks=20,
            tickformat='%Y-Q%q'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Sort the years before displaying in the selectbox
        years = sorted(data['Year'].unique())
        selected_year = st.selectbox('Select Year to Filter Monthly Data', years)
        filtered_data = data[data['Year'] == selected_year]

        # Display the month-wise data in a pie chart
        st.write("Monthly Data")
        monthly_counts = filtered_data.groupby(['Year-Month', 'Employment type']).size().reset_index(name='Count')
        selected_month = st.selectbox('Select Month to Filter Data', monthly_counts['Year-Month'].unique())
        month_filtered_data = monthly_counts[monthly_counts['Year-Month'] == selected_month]

        # Create pie chart
        pie_fig = go.Figure(data=[go.Pie(labels=month_filtered_data['Employment type'], values=month_filtered_data['Count'], textinfo='label+percent', insidetextorientation='radial')])
        pie_fig.update_layout(title_text=f'Distribution of Employment Types for {selected_year}-{selected_month}')

        st.plotly_chart(pie_fig, use_container_width=True)


    with tab2:
        st.write("Other analyses can go here.")

if st.session_state.page == "Placeholder 3":
    st.write("Contact information.")

# Footer
st.markdown("---")
st.markdown("Created by Algorithm Avengers with :heart: for Vega Bryggeri.")

if __name__ == "__main__":
    def main():
        pass  # Main function definition is empty as Streamlit runs script top-down

    main()
