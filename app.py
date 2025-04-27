# ---------------------------------------------------
# 📦 Inventory Management Dashboard Project (Final)
# ---------------------------------------------------

# Install required libraries (if not installed)
# pip install pandas matplotlib seaborn streamlit

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# 1. Load the Data
@st.cache_data
def load_data():
    df = pd.read_csv('inventory_data.csv')  # Load sample CSV file
    df['Last_Ordered_Date'] = pd.to_datetime(df['Last_Ordered_Date'])
    return df

df = load_data()

# 2. Data Cleaning and Feature Engineering
def stock_status(row):
    if row['Current_Stock'] < row['Reorder_Level']:
        return 'Low Stock'
    elif row['Current_Stock'] > 1.5 * row['Monthly_Sales_Avg']:
        return 'Overstock'
    else:
        return 'Healthy'

df['Stock_Status'] = df.apply(stock_status, axis=1)

# 3. Streamlit App Layout
st.title('📦 Inventory Management Dashboard')

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    category_filter = st.multiselect(
        "Select Category", 
        options=df['Category'].unique(), 
        default=df['Category'].unique()
    )
    supplier_filter = st.multiselect(
        "Select Supplier", 
        options=df['Supplier_Name'].unique(), 
        default=df['Supplier_Name'].unique()
    )

# Apply Filters
filtered_df = df[
    (df['Category'].isin(category_filter)) &
    (df['Supplier_Name'].isin(supplier_filter))
]

# 4. Display KPIs
total_products = filtered_df['Product_ID'].nunique()
low_stock_pct = (filtered_df[filtered_df['Stock_Status'] == 'Low Stock'].shape[0] / filtered_df.shape[0]) * 100
avg_lead_time = filtered_df['Lead_Time_Days'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Products", total_products)
col2.metric("Low Stock (%)", f"{low_stock_pct:.2f}%")
col3.metric("Average Lead Time (Days)", f"{avg_lead_time:.1f}")

# 5. Visualizations

# Stock Status Pie Chart
st.subheader('📊 Stock Status Distribution')
stock_status_counts = filtered_df['Stock_Status'].value_counts()

fig1, ax1 = plt.subplots()
ax1.pie(
    stock_status_counts,
    labels=stock_status_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=sns.color_palette("pastel")
)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig1)

# Low Stock Products Bar Chart
st.subheader('📉 Low Stock Products')
low_stock = filtered_df[filtered_df['Stock_Status'] == 'Low Stock']

if not low_stock.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=low_stock,
        x='Product_Name',
        y='Current_Stock',
        hue='Supplier_Name',
        dodge=False,
        ax=ax2
    )
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.info("No low stock products found.")

# Full Inventory Data Table
st.subheader('📋 Inventory Data')
st.dataframe(filtered_df)

# 6. Insights and Recommendations
st.subheader('💡 Insights')
st.write(f"✅ {low_stock.shape[0]} products are running low on stock.")
st.write(f"✅ The average lead time for suppliers is around {avg_lead_time:.1f} days.")

if low_stock.shape[0] > 0:
    st.write("⚠️ Consider reordering the following products urgently:")
    st.table(low_stock[['Product_Name', 'Current_Stock', 'Reorder_Level', 'Supplier_Name']])
