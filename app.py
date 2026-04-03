import streamlit as st
import pandas as pd
import plotly.express as px
import os
st.write("Working directory:", os.getcwd())
st.write("Files here:", os.listdir())
st.set_page_config(
    page_title="Nike Sales Dashboard",
    layout="wide"
)

st.image("Logo.png", width=500)

# -------------------------
# Load Data
# -------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_Data.csv") 
    return df

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------

st.sidebar.title("🔎 Filters")

# Region & Product Filters
if st.sidebar.checkbox("🌍 Show Region & Product Filters", value=True):
    region_filter = st.sidebar.multiselect(
        "Select Region",
        options=df["Region"].unique(),
        default=df["Region"].unique()
    )

    product_line_filter = st.sidebar.multiselect(
        "🏷️ Select Product Line",
        options=df["Product_Line"].unique(),
        default=df["Product_Line"].unique()
    )
else:
    region_filter = df["Region"].unique()
    product_line_filter = df["Product_Line"].unique()

st.sidebar.divider()

# Time Filters
if st.sidebar.checkbox("📅 Show Time Filters", value=True):
    year_filter = st.sidebar.multiselect(
        "Select Year",
        options=df["Year"].unique(),
        default=df["Year"].unique()
    )

    quarter_filter = st.sidebar.slider(
        "🗓️ Year Quarter Range",
        min_value=int(df["Year_Quarter"].min()),
        max_value=int(df["Year_Quarter"].max()),
        value=(int(df["Year_Quarter"].min()), int(df["Year_Quarter"].max()))
    )
else:
    year_filter = df["Year"].unique()
    quarter_filter = (int(df["Year_Quarter"].min()), int(df["Year_Quarter"].max()))

st.sidebar.divider()

# Sales Channel Filters
if st.sidebar.checkbox("🛒 Show Sales Channel Filters", value=True):
    sales_channel_filter = st.sidebar.multiselect(
        "Select Channel",
        options=df["Sales_Channel"].unique(),
        default=df["Sales_Channel"].unique()
    )
else:
    sales_channel_filter = df["Sales_Channel"].unique()

st.sidebar.divider()

# Customer  Filters
if st.sidebar.checkbox("👤 Show Customer Related Filters", value=True):
    gender_filter = st.sidebar.multiselect(
        "Select Gender Category",
        options=df["Gender_Category"].unique(),
        default=df["Gender_Category"].unique()
    )

    size_filter = st.sidebar.multiselect(
        "📏 Select Size",
        options=df["Size"].unique(),
        default=df["Size"].unique()
    )
else:
    gender_filter = df["Gender_Category"].unique()
    size_filter = df["Size"].unique()


# -------------------------
# Apply Filters
# -------------------------

filtered_df = df[
    (df["Region"].isin(region_filter)) &
    (df["Product_Line"].isin(product_line_filter)) &
    (df["Year"].isin(year_filter)) &
    (df["Year_Quarter"].between(quarter_filter[0], quarter_filter[1])) &
    (df["Sales_Channel"].isin(sales_channel_filter)) &
    (df["Gender_Category"].isin(gender_filter)) &
    (df["Size"].isin(size_filter))
]

# -------------------------
# Page Navigation
# -------------------------
st.sidebar.title("📂 Navigation:")
page = st.sidebar.radio(
    "",
    [
        "Main Dashboard",
        "Analysis",
        "Final Insights"
    ]
)

st.sidebar.title("📝 By:")
st.sidebar.markdown("Eng. Amal Mohamed-Khair")
st.sidebar.markdown("Email: amal4khair@gmail.com")
# =================================================
# MAIN PAGE
# =================================================

if page == "Main Dashboard":


    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head())

    st.divider()

    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)

    Number_Orders = filtered_df["Order_ID"].nunique()
    Units_Sold = filtered_df["Units_Sold"].sum()
    Total_Revenue = filtered_df["Revenue"].sum()
    Total_Profit = filtered_df["Profit"].sum()
    # Find top product by profit
    top_product = (
        filtered_df.groupby("Product_Name")["Profit"]
        .sum()
        .reset_index()
        .sort_values(by="Profit", ascending=False)
        .head(1)
    )
    best_product_name = top_product["Product_Name"].values[0]
    best_product_profit = top_product["Profit"].values[0]


    col1.metric("🛒 Orders", Number_Orders)
    col2.metric("📦 Units Sold", int(Units_Sold))
    col3.metric("💰 Total Revenue", round(Total_Revenue, 2))
    col4.metric("💵 Total Profit", round(Total_Profit, 2,))
    col5.metric("🏆 Top Product", f"{best_product_name}", f"Profit: {round(best_product_profit,2)}")

# =================================================
# ANALYSIS PAGE
# =================================================

elif page == "Analysis":

    st.title("📊 Exploratory Data Analysis")

    tab1, tab2, tab3 = st.tabs([
        "Univariate Analysis",
        "Bivariate Analysis",
        "Multivariate Analysis"
    ])

    with tab1:
        st.subheader("Univariate Analysis")
        # Product Line Distribution
        st.subheader("🏷️ Distribution of Product Lines")
        st.bar_chart(filtered_df["Product_Line"].value_counts())

        # Profit Distribution
        fig = px.histogram(filtered_df, x="Profit",title="💵 Profit Distribution")
        st.plotly_chart(fig)

        # Gender Category
        gender_counts = filtered_df["Gender_Category"].value_counts().reset_index()
        fig_gender = px.pie(gender_counts, names="Gender_Category",values="count",title="👤 Orders by Gender Category")
        st.plotly_chart(fig_gender)
        # Units Sold 
        fig_units = px.box(filtered_df, y="Units_Sold", title="📦 Units Sold Distribution")
        st.plotly_chart(fig_units)


    with tab2:
        st.subheader("Bivariate Analysis")

        # Profit Trend Line
        filtered_df['Order_Date'] = pd.to_datetime(filtered_df['Order_Date'], errors='coerce')
        sales_trend = filtered_df.groupby(filtered_df['Order_Date'].dt.to_period("M"))['Profit'].sum().reset_index()
        sales_trend['Order_Date'] = sales_trend['Order_Date'].dt.to_timestamp()
        fig_trend = px.line(sales_trend, x='Order_Date', y='Profit', title="📈 Monthly Profit Trend")
        st.plotly_chart(fig_trend)

        # Profit by Product Name
        profit_by_product = filtered_df.groupby("Product_Name")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False)
        fig_product = px.bar(profit_by_product,x="Product_Name",y="Profit", title="📦 Profit by Product Name",text_auto=True,color="Profit",color_continuous_scale="Blues")
        st.plotly_chart(fig_product)

        #Profit by Region
        profit_by_region = (filtered_df.groupby("Region")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False))
        fig_region = px.pie(profit_by_region,names="Region",values="Profit",title="🌍Profit by Region")
        st.plotly_chart(fig_region, use_container_width=True)

        # Sales Channel vs Day Type (Grouped Bar)
        channel_counts = filtered_df.groupby(['Sales_Channel','Day_Type']).size().reset_index(name='Count')
        fig_channel_day = px.bar(channel_counts, x='Day_Type', y='Count', color='Sales_Channel', barmode='group', text='Count', title="🗓️ Sales Channel by Day Type")
        st.plotly_chart(fig_channel_day)


    with tab3:
        st.subheader("Multivariate Analysis")

        # Profit by Region and Product Line
        profit_by_region_line = filtered_df.groupby(["Region", "Product_Line"])["Profit"].sum().reset_index()
        fig_region_line = px.bar(profit_by_region_line, x="Region", y="Profit", color="Product_Line", barmode="group", title="🌍 Profit by Region and Product Line")
        st.plotly_chart(fig_region_line)

        # Sales by Gender and Product Line
        profit_gender_line = filtered_df.groupby(["Gender_Category", "Product_Line"])["Units_Sold"].sum().reset_index().sort_values(by="Units_Sold", ascending=False)
        fig_gender_line = px.bar(profit_gender_line, x="Gender_Category", y="Units_Sold", color="Product_Line", barmode="group", title="👤 Seales by Gender and Product Line")
        st.plotly_chart(fig_gender_line)

        # Profit Heatmap (Region vs Sales Channel)
        profit_heatmap = filtered_df.groupby(["Region", "Sales_Channel"])["Profit"].sum().reset_index()
        fig_heatmap = px.density_heatmap(profit_heatmap, x="Region", y="Sales_Channel", z="Profit", color_continuous_scale="Viridis", title="🌍 Profit Heatmap by Region & Sales Channel")
        st.plotly_chart(fig_heatmap)



# =================================================
# FINAL INSIGHTS PAGE
# =================================================



elif page == "Final Insights":

    st.title("🧠 Key Insights")

    st.markdown("""
    ### 📌 Main Findings

    - 📈 **Seasonal Trends**: Profits peak in Q4 (September–December), with noticeable dips in 
       off-season months.  
    - 🏷️ **Product Line Performance**: Kids’ Lifestyle and Women’s Training products consistently
       generate the highest profits.  
    - 🌍 **Regional Insights**: Delhi, Kolkata, and Mumbai are strong profit centers, while other
       regions underperform.  
    - 🛒 **Sales Channel Behavior**: Retail dominates during weekdays, while Online sales gain 
     traction on weekends.  
    - ⚠️ **Data Quality Issues**: Some product sizes are recorded as “UNKNOWN,” ,beside more than 
       50 percent of records have zero sush as units sold, revenue and others.  

    ### 💡 Business Recommendations

    - 📅 **Seasonal Strategy**:  
      Intensify marketing planning for Q4 to maximize peak season profits.  
      Develop off-season promotions to stabilize revenue during low months.  

    - 🎯 **Product Strategy**:  
      Launch targeted campaigns for Kids’ Lifestyle and Women’s Training products.  
      Explore bundling and upselling opportunities in these high-profit categories.  

    - 🏢 **Regional Focus**:  
      Prioritize Delhi, Kolkata, and Mumbai with localized promotions and supply chain support.  
      Investigate underperforming regions to identify barriers and growth opportunities.  

    - 🔀 **Channel Optimization**:  
      Boost Online promotions during weekends to capture demand spikes.  
      Maintain Retail engagement during weekdays with in-store campaigns and loyalty programs.  

    - 🧹 **Data Quality Improvement**:  
      Standardize data entries and eliminate “UNKNOWN” values.   
    """)
