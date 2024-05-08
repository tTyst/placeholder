import streamlit as st
import pandas as pd
import plotly.express as px

# Main content
st.header("Vega Bryggeri Dashboard")
st.markdown("With this dashboard, the goal is to provide Vega Bryggeri with insights into various types of data.")

# Load data function
@st.cache_data()
def load_data(year):
    file_path = f"Artikellistan {year}.xlsx"  # Assuming the files are named by year
    data = pd.read_excel(file_path, header=4)
    return data

# Function to get top sales data for Vega Bryggeri
@st.cache_data()
def get_top_vega_bryggeri(data):
    filtered_data = data[data['Producentnamn'] == 'Vega Bryggeri']
    top_sales = filtered_data.sort_values(by='Försäljning i liter', ascending=False).head(50)
    return top_sales

# Function to prepare comparative data
def get_comparative_data():
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    frames = []
    for year in years:
        data = load_data(year)
        total_sales = data[data['Producentnamn'] == 'Vega Bryggeri']['Försäljning i liter'].sum()
        frames.append(pd.DataFrame({'Year': [year], 'Sales': [total_sales]}))
    return pd.concat(frames)

def get_combined_percentage_change_data():
    categories = ["Lageröl", "Säsongsöl", "Specialöl"]
    years = [2018, 2019, 2020, 2021, 2022, 2023]
    results = []

    previous_total_excl_vega = None
    previous_vega_sales = None

    for year in years:
        data = load_data(year)
        vega_sales_yearly = 0
        total_sales_yearly = 0
        
        for category in categories:
            category_data = data[data['Varugrupp detalj'] == category]
            total_sales = category_data['Försäljning i liter'].sum()
            vega_sales = category_data[category_data['Producentnamn'] == 'Vega Bryggeri']['Försäljning i liter'].sum()

            vega_sales_yearly += vega_sales
            total_sales_yearly += total_sales

        other_producers_sales = total_sales_yearly - vega_sales_yearly

        if previous_total_excl_vega is not None and previous_vega_sales is not None:
            total_market_change = ((other_producers_sales - previous_total_excl_vega) / previous_total_excl_vega * 100) if previous_total_excl_vega > 0 else 0
            vega_change = ((vega_sales_yearly - previous_vega_sales) / previous_vega_sales * 100) if previous_vega_sales > 0 else 0
        else:
            total_market_change = 0
            vega_change = 0

        results.append({
            'Year': year,
            'Vega Bryggeri Change %': vega_change,
            'Total Market Change %': total_market_change,
            'Vega Bryggeri Sales': vega_sales_yearly,
            'Other Producers Sales': other_producers_sales
        })

        previous_total_excl_vega = other_producers_sales
        previous_vega_sales = vega_sales_yearly

    return pd.DataFrame(results)







# Sidebar
st.sidebar.title("Menu")

# Tabs for analysis
tab1, tab2, tab3 = st.tabs(["Yearly Analysis", "Comparative Analysis", "Annual Percentage Change Comparison"])

with tab1:
    year = st.selectbox("Select Year", (2023, 2022, 2021, 2020, 2019, 2018))
    data = load_data(year)
    st.subheader("Top Most Sold Beverages by Vega Bryggeri")
    top_vega = get_top_vega_bryggeri(data)
    fig = px.bar(top_vega, x='Namn', y='Försäljning i liter',
                 labels={'Försäljning i liter': 'Försäljning i Liter', 'Namn': 'Produkt Namn'},
                 title="Top Produkter från Vega Bryggeri baserat på Försäljning i liter")
    st.plotly_chart(fig, use_container_width=True)
    top_vega = top_vega[['Kvittonamn', 'Producentnamn', 'Försäljning i liter', 'Varugrupp detalj']].reset_index(drop=True)
    # Increment the index to start from 1 instead of 0
    top_vega.index = top_vega.index + 1
    st.dataframe(top_vega)

with tab2:
    st.subheader("Comparative Sales Data Across Years")
    comparative_data = get_comparative_data()
    fig = px.line(comparative_data, x='Year', y='Sales',
                  labels={'Sales': 'Sales in Liters', 'Year': 'Year'},
                  title='Sales Comparison Over Years')
    st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.subheader("Annual Market Share Change Comparison")
    percentage_data = get_combined_percentage_change_data()

    fig = px.line(percentage_data, x='Year', y=['Vega Bryggeri Change %', 'Total Market Change %'],
                  labels={'value': 'Year-over-Year Change (%)', 'variable': 'Market Segment'},
                  title='Annual Market Share Change Percentage (Vega Bryggeri excluded)',
                  hover_data=['Vega Bryggeri Sales', 'Other Producers Sales'])
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(percentage_data[['Year', 'Vega Bryggeri Change %', 'Total Market Change %']])


# Footer
st.markdown("---")
st.markdown("Created by Algorithm Avengers with :heart: for Vega Bryggeri.")

if __name__ == "__main__":
    def main():
        pass  # Main function definition is empty as Streamlit runs script top-down

    main()
