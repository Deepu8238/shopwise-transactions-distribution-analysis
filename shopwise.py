import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Shop-wise Transaction Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the dataset
@st.cache_data
def load_data():
    file_path = 'shop-wise-trans-details_12_2024.csv'  # Adjust if required
    data = pd.read_csv(file_path)
    return data

# Load data
try:
    data = load_data()

    # Title and description
    st.title('🛒 Shop-wise Transaction Dashboard')
    st.markdown('---')
    
    if all(col in data.columns for col in ['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']):
        data['Total Items'] = data[['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']].sum(axis=1)
        
    # Key Metrics
    st.header('Key Metrics Overview')
    total_transactions = data['noOfTrans'].sum()
    total_sales = data['totalAmount'].sum()
    total_shops = len(data['distName'].unique())
    #total_items=len(data['Total Items'].unique())

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", f"{total_transactions:,}")
    col2.metric("Total Sales", f"{total_sales:,.2f}")
    col3.metric("Total Shops", f"{total_shops}")

    # Sales by Shop
    st.markdown('---')
    st.header('Sales by District')
    selected_metric_shop = st.radio("Select Metric to Display", ['totalAmount', 'noOfTrans'], horizontal=True)
    shop_sales_data = data.groupby('distName')[[selected_metric_shop]].sum().reset_index()
    fig = px.bar(shop_sales_data, x='distName', y=selected_metric_shop,
                 title=f'{selected_metric_shop} by District',
                 labels={selected_metric_shop: selected_metric_shop, 'distName': 'District'},
                 hover_data=['distName'])
    st.plotly_chart(fig, use_container_width=True)

    # Transactions by Region
    st.markdown('---')
    st.header('Transactions by Region')
    selected_metric_region = st.radio("Select Metric to Display for Regions", ['noOfTrans', 'totalAmount'], horizontal=True)
    region_data = data.groupby('distName')[[selected_metric_region]].sum().reset_index()
    fig = px.bar(region_data, x='distName', y=selected_metric_region,
                 title=f'{selected_metric_region} by District',
                 labels={selected_metric_region: selected_metric_region, 'distName': 'District'},
                 hover_data=['distName'])
    st.plotly_chart(fig, use_container_width=True)

    # Sales Distribution by Region
    st.markdown('---')
    st.header('Sales Distribution by Region')
    region_sales_data = data.groupby('distName')[['totalAmount']].sum().reset_index()
    fig = px.pie(region_sales_data, names='distName', values='totalAmount',
                 title='Sales Distribution by Region',
                 hover_data=['totalAmount'])
    st.plotly_chart(fig, use_container_width=True)

    # Shop-Level Details
    st.markdown('---')
    st.header('Shop-Level Details')
    selected_region = st.selectbox('Select Region', ['All'] + list(data['distName'].unique()))
    filtered_data = data if selected_region == 'All' else data[data['distName'] == selected_region]

    selected_sort_column = st.selectbox("Sort Table By", ['distName', 'noOfTrans', 'totalAmount'])
    shop_details = filtered_data[['distName', 'noOfTrans', 'totalAmount']].sort_values(by=selected_sort_column, ascending=False)
    st.dataframe(shop_details, use_container_width=True)
    
    
    st.markdown('---')
    st.header('Item Consumption by District')
    if 'distName' in data.columns and 'itemName' in data.columns:
        item_district_data = data.groupby(['distName', 'itemName'])['noOfTrans'].sum().reset_index()
        selected_district = st.selectbox('Select District', ['All'] + list(data['distName'].unique()))
        filtered_item_data = item_district_data if selected_district == 'All' else item_district_data[item_district_data['District'] == selected_district]

        fig = px.sunburst(filtered_item_data, path=['distName', 'itemName'], values='noOfTrans',
                          title=f'Consumption of Items in {selected_district} District' if selected_district != 'All' else 'Consumption of Items by District',
                          labels={'noOfTrans': 'noOfTrans', 'itemName': 'itemName'},
                          hover_data=['distName'])
        st.plotly_chart(fig, use_container_width=True)

    # Combined Item Consumption by District
    if all(col in data.columns for col in ['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']):
        data['Total Items'] = data[['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']].sum(axis=1)

        st.markdown('---')
        st.header('Combined Item Consumption by District')
        combined_item_district_data = data.groupby('distName')['Total Items'].sum().reset_index()
        selected_district_combined = st.selectbox('Select District for Combined Items', ['All'] + list(combined_item_district_data['distName'].unique()))
        filtered_combined_item_data = (
            combined_item_district_data if selected_district_combined == 'All'
            else combined_item_district_data[combined_item_district_data['distName'] == selected_district_combined]
        )

        fig = px.treemap(filtered_combined_item_data, path=['distName'], values='Total Items',
                         title=f'Total Consumption of Combined Items in {selected_district_combined} District' if selected_district_combined != 'All' else 'Total Consumption of Combined Items by District')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Columns for combining items (Salt, Wheat, Rgdal, Kerosene, Sugar) are missing in the dataset.")
    # Consumption of Each Item by District
    st.markdown('---')
    st.header('Consumption of Each Item by District')

    if 'distName' in data.columns and all(item in data.columns for item in ['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']):
        item_columns = ['salt', 'wheat', 'rgdal', 'kerosene', 'sugar']
        item_district_consumption = data.groupby('distName')[item_columns].sum().reset_index()
        
        st.dataframe(item_district_consumption, use_container_width=True)

        selected_item = st.selectbox('Select an Item to Visualize', item_columns)
        fig = px.bar(item_district_consumption, x='distName', y=selected_item,
                     title=f'Consumption of {selected_item} by District',
                     labels={selected_item: 'Quantity Consumed', 'distName': 'District'},
                     hover_data=['distName'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Required columns for items or district are missing in the dataset.")

    
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please ensure the dataset is correctly formatted and accessible.")
