import pandas as pd
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.pyplot as plt
sns.set(style='dark')

st.markdown(
    """
    <style>
    body {
        background-color:
        color: white;
    }
    .metric-value {
        font-size: 12px !important; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def sales_by_product_category(df):
    category_value = df['product_category_name'].value_counts()
    sorted_sales = category_value.sort_values(ascending=False).reset_index()
    sorted_sales.columns = ['Product Category', 'Number of Sales']
    return sorted_sales

def top_category_by_review(df):
    category_avg_review = df.groupby("product_category_name")["review_score"].mean()
    sorted_categories = category_avg_review.sort_values(ascending=False).reset_index()
    return sorted_categories

def count_orders_by_city(df):
    order_count_by_city = df['customer_city'].value_counts().reset_index()
    order_count_by_city.columns = ['City', 'Order Count']
    return order_count_by_city

def count_orders_by_state(df):
    order_count_by_city = df['customer_state'].value_counts().reset_index()
    order_count_by_city.columns = ['State', 'Order Count']
    return order_count_by_city

def retrieving_satet_data(df):
    state = df['customer_state'].value_counts()
    return state

def shopping_data_state(df, i):
    state_df = df[df['customer_state']==retrieving_satet_data(df).index[i]]
    end_date = pd.to_datetime(state_df['order_purchase_timestamp']).max()
    start_date = end_date - pd.DateOffset(years=2)
    df_second_state_last_year = state_df[(state_df['order_purchase_timestamp'] >= start_date) & (state_df['order_purchase_timestamp'] <= end_date)]

    monthly_orders = df_second_state_last_year.groupby(pd.Grouper(key='order_purchase_timestamp', freq='M')).size()
    return monthly_orders

def rfm_analysis_state(df):
    df['Recency'] = (pd.Timestamp.now() - df['order_purchase_timestamp']).dt.days

    rfm_df = df.groupby('customer_state').agg({
        'Recency': 'min',  # Recency (R)
        'order_id': 'nunique',  # Frequency (F)
        'price': 'sum'  # Monetary (M)
    }).rename(columns={
        'order_id': 'Frequency',
        'price': 'Monetary'
    }).reset_index()

    return rfm_df

def rfm_analysis_city(df):
    df['Recency'] = (pd.Timestamp.now() - df['order_purchase_timestamp']).dt.days

    rfm_df = df.groupby('customer_city').agg({
        'Recency': 'min',  # Recency (R)
        'order_id': 'nunique',  # Frequency (F)
        'price': 'sum'  # Monetary (M)
    }).rename(columns={
        'order_id': 'Frequency',
        'price': 'Monetary'
    }).reset_index()

    return rfm_df


all_df = pd.read_csv("all_data.csv")

st.markdown(
    f"<h1 style='text-align:center;'>Project Dashboard Danu</h3>", 
    unsafe_allow_html=True
)

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()


col1, col2 = st.columns(2)
with col1:
    start_date, end_date = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
    )

    main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]
 
with col2:
    col1, col2 = st.columns(2)
    daily_orders_df = create_daily_orders_df(main_df)
    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.markdown(f'<h1 style="font-size: 24px;">Total orders: {total_orders}</h1>', unsafe_allow_html=True)
    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
        st.markdown(f'<h1 style="font-size: 24px;">Total Revenue: {total_revenue}</h1>', unsafe_allow_html=True)


top_products = sales_by_product_category(main_df)
top_review  =  top_category_by_review(main_df)
top_review.columns = ['Product Category', 'Average Review score']
top_city =  count_orders_by_city(main_df)
top_state = count_orders_by_state(main_df)
rfm_state = rfm_analysis_state(main_df)
rfm_city = rfm_analysis_city(main_df)
top_one_state = shopping_data_state(main_df, 0)
top_second_state = shopping_data_state(main_df, 1)
top_third_state = shopping_data_state(main_df, 2)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)   
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.markdown(
    f"<h3 style='text-align:center;'>Best Performing Product</h3>", 
    unsafe_allow_html=True
)
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 25))
 
colors = ["#90CAF9","#90CAF9","#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="Number of Sales", y="Product Category", data=top_products.head(30), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="Average Review score", y="Product Category", data=top_review.head(30), palette="viridis")
plt.xlabel("Average Review score", fontsize=25)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Average Review score", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Top 10  Product By Review Score", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.markdown(
    f"<h3 style='text-align:center;'>Top 5 Most Purchased Cities and States</h3>", 
    unsafe_allow_html=True
)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 

sns.barplot(x="City", y="Order Count", data=top_city.head(5), palette="YlGnBu", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_ylabel("Number of Order", fontsize=30)
ax[0].set_title("Top 5 Purchased City", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="State", y="Order Count", data=top_state.head(5), palette="plasma")
ax[1].set_ylabel(None)
ax[1].set_ylabel("Number of Order", fontsize=30)
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Top 5 Purchhased State", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)
st.title('Statistics of The Number of Order 3 States Sith The Largest Order')
tab1, tab2, tab3 = st.tabs(["Top 1", "Top 2", "Top 3"])
 
with tab1:
    plt.figure(figsize=(10, 6))
    top_one_state.plot(kind='bar')
    plt.title(f'Purchasing pattern in satet SP (Last 2 years)')
    plt.xlabel('Month')
    plt.ylabel('Number of Order')
    plt.xticks(rotation=90)
    st.pyplot(plt)
 
with tab2:
    plt.figure(figsize=(10, 6))
    top_second_state.plot(kind='bar')
    plt.title(f'Purchasing pattern in satet RJ (Last 2 years)')
    plt.xlabel('Month')
    plt.ylabel('Number of Order')
    plt.xticks(rotation=90)
    st.pyplot(plt)
 
 
with tab3:
    plt.figure(figsize=(10, 6))
    top_third_state.plot(kind='bar')
    plt.title(f'Purchasing pattern in satet MG (Last 2 years)')
    plt.xlabel('Month')
    plt.ylabel('Number of Order')
    plt.xticks(rotation=90)
    st.pyplot(plt)
 


st.subheader("RFM Analysis by Customer State")
 
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_state.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_state.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_state.Monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="Recency", x="customer_state", data=rfm_state.sort_values(by="Recency", ascending=True).head(3), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("State", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="Frequency", x="customer_state", data=rfm_state.sort_values(by="Frequency", ascending=False).head(3), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("State", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="Monetary", x="customer_state", data=rfm_state.sort_values(by="Monetary", ascending=False).head(3), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("State", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

st.subheader("RFM Analysis by Customer City")
 
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_city.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_city.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_city.Monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="Recency", x="customer_city", data=rfm_city.sort_values(by="Recency", ascending=True).head(3), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("City", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=25)
 
sns.barplot(y="Frequency", x="customer_city", data=rfm_city.sort_values(by="Frequency", ascending=False).head(3), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("City", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)
 
sns.barplot(y="Monetary", x="customer_city", data=rfm_city.sort_values(by="Monetary", ascending=False).head(3), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("City", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)