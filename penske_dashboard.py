import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Penske Spend Visualizer", layout="wide")

# File uploader
uploaded_file = st.file_uploader("Upload the Penske Spend CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().replace(" ", "_").replace(":", "") for col in df.columns]
    df['Total'] = pd.to_numeric(df['Total'].astype(str).str.replace(',', ''), errors='coerce')
    df['Invoice_Date'] = pd.to_datetime(df['Invoice_Date'], errors='coerce')
    df['Month'] = df['Invoice_Date'].dt.to_period('M')

    st.sidebar.header("Filters")
    accounts = st.sidebar.multiselect("Account Name", options=sorted(df['Account_Name'].unique()), default=list(df['Account_Name'].unique()))
    products = st.sidebar.multiselect("Product Name", options=sorted(df['Product_Product_Name'].unique()), default=list(df['Product_Product_Name'].unique()))
    pricebooks = st.sidebar.multiselect("Price Book", options=sorted(df['Price_Book_Price_Book_Name'].unique()), default=list(df['Price_Book_Price_Book_Name'].unique()))
    date_range = st.sidebar.date_input("Date Range", [df['Invoice_Date'].min(), df['Invoice_Date'].max()])

    filtered = df[
        df['Account_Name'].isin(accounts) &
        df['Product_Product_Name'].isin(products) &
        df['Price_Book_Price_Book_Name'].isin(pricebooks) &
        (df['Invoice_Date'] >= pd.to_datetime(date_range[0])) &
        (df['Invoice_Date'] <= pd.to_datetime(date_range[1]))
    ]

    st.title("Penske Spend Visualizer")
    st.write(f"Showing {len(filtered)} records.")

    tab1, tab2, tab3, tab4 = st.tabs(["Spend Over Time", "Spend by Account", "Spend by Product", "Month/Month by Dealer+PriceBook"])

    with tab1:
        st.header("Monthly Spend by Account and Product")
        # Add account selector
        account_for_time = st.selectbox("Select Account for Spend Over Time", options=["All Accounts"] + sorted(filtered['Account_Name'].unique()), key="account_tab1")
        filtered['Month'] = filtered['Invoice_Date'].dt.to_period('M').astype(str)
        import plotly.express as px
        if account_for_time != "All Accounts":
            filtered_time = filtered[filtered['Account_Name'] == account_for_time]
        else:
            filtered_time = filtered
        # Group by Month and Product
        spend_time = filtered_time.groupby(['Month', 'Product_Product_Name'])['Total'].sum().reset_index()
        fig = px.bar(spend_time, x='Month', y='Total', color='Product_Product_Name', barmode='group',
                     title='Monthly Spend by Product', labels={'Total':'Total Spend (USD)', 'Month':'Month', 'Product_Product_Name':'Product'})
        fig.update_traces(hovertemplate='Month: %{x}<br>Product: %{legendgroup}<br>Total: $%{y:,.2f}')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Total Spend by Account")
        account_for_account_tab = st.selectbox("Select Account to View Spend", options=["All Accounts"] + sorted(filtered['Account_Name'].unique()), key="account_tab2")
        import plotly.express as px
        if account_for_account_tab != "All Accounts":
            spend_account = filtered[filtered['Account_Name'] == account_for_account_tab].groupby('Account_Name')['Total'].sum().sort_values(ascending=False).reset_index()
        else:
            spend_account = filtered.groupby('Account_Name')['Total'].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(spend_account, x='Account_Name', y='Total', title='Total Spend by Account', labels={'Total':'Total Spend (USD)', 'Account_Name':'Account Name'})
        fig.update_traces(hovertemplate='Account: %{x}<br>Total: $%{y:,.2f}')
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("Total Spend by Product (Top 20)")
        import plotly.express as px
        spend_product = filtered.groupby('Product_Product_Name')['Total'].sum().sort_values(ascending=False).head(20).reset_index()
        fig = px.bar(spend_product, x='Product_Product_Name', y='Total', title='Total Spend by Product (Top 20)', labels={'Total':'Total Spend (USD)', 'Product_Product_Name':'Product Name'})
        fig.update_traces(hovertemplate='Product: %{x}<br>Total: $%{y:,.2f}')
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("Month-over-Month Spend by Account (by Price Book)")
        filtered['Month'] = filtered['Invoice_Date'].dt.to_period('M').astype(str)
        import plotly.express as px
        for account in filtered['Account_Name'].unique():
            sub = filtered[filtered['Account_Name'] == account]
            pivot = sub.pivot_table(index='Month', columns='Price_Book_Price_Book_Name', values='Total', aggfunc='sum', fill_value=0)
            pivot = pivot.reset_index().melt(id_vars='Month', var_name='Price Book', value_name='Total')
            fig = px.bar(pivot, x='Month', y='Total', color='Price Book', title=f"Month-over-Month Spend for {account} (by Price Book)", labels={'Total':'Total Spend (USD)', 'Month':'Month'})
            fig.update_traces(hovertemplate='Month: %{x}<br>Price Book: %{legendgroup}<br>Total: $%{y:,.2f}')
            st.plotly_chart(fig, use_container_width=True)

    st.header("YTD Spend Summary Table")
    year = st.selectbox("Year", options=sorted(filtered['Invoice_Date'].dt.year.dropna().unique()), index=0)
    ytd = filtered[filtered['Invoice_Date'].dt.year == year]
    summary = ytd.groupby(['Account_Name', 'Price_Book_Price_Book_Name'])['Total'].sum().unstack(fill_value=0)
    st.dataframe(summary.round(2))

    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered.to_csv(index=False),
        file_name="filtered_spend_data.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload the Penske Spend CSV file to begin.")
