import streamlit as st
import pandas as pd
import plotly.express as px

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
    df = pd.read_csv("cleaned_data.csv") 
    return df

df = load_data()
# -------------------------
# Page Navigation
# -------------------------
st.sidebar.title("📍Navigation")
page = st.sidebar.radio(
    "",
    [
        "Main Dashboard",
        "Analysis",
        "Recommendations"
    ]
)
# -------------------------
# Sidebar Filters
# -------------------------

st.sidebar.title("🔎 Filters")

# Region & Product Filters
if st.sidebar.checkbox("Show Region & Product Filters", value=False):
    region_filter = st.sidebar.multiselect(
        "-Select Region",
        options=df["Region"].unique(),
        default=df["Region"].unique()
    )

    product_line_filter = st.sidebar.multiselect(
        "-Select Product Line",
        options=df["Product_Line"].unique(),
        default=df["Product_Line"].unique()
    )
else:
    region_filter = df["Region"].unique()
    product_line_filter = df["Product_Line"].unique()

st.sidebar.divider()

# Time Filters
if st.sidebar.checkbox("Show Time Filters", value=False):
    year_filter = st.sidebar.multiselect(
        "-Select Year",
        options=df["Year"].unique(),
        default=df["Year"].unique()
    )

    quarter_filter = st.sidebar.slider(
        "-Year Quarter Range",
        min_value=int(df["Year_Quarter"].min()),
        max_value=int(df["Year_Quarter"].max()),
        value=(int(df["Year_Quarter"].min()), int(df["Year_Quarter"].max()))
    )
else:
    year_filter = df["Year"].unique()
    quarter_filter = (int(df["Year_Quarter"].min()), int(df["Year_Quarter"].max()))

st.sidebar.divider()

# Sales Channel Filters
if st.sidebar.checkbox("Show Sales Channel Filters", value=False):
    sales_channel_filter = st.sidebar.multiselect(
        "Select Channel",
        options=df["Sales_Channel"].unique(),
        default=df["Sales_Channel"].unique()
    )
else:
    sales_channel_filter = df["Sales_Channel"].unique()

st.sidebar.divider()

# Customer  Filters
if st.sidebar.checkbox("Show Customer Related Filters", value=False):
    gender_filter = st.sidebar.multiselect(
        "Select Gender Category",
        options=df["Gender_Category"].unique(),
        default=df["Gender_Category"].unique()
    )

    size_filter = st.sidebar.multiselect(
        "Select Size",
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

# =================================================
# MAIN PAGE
# =================================================

if page == "Main Dashboard":

    tab1, tab2= st.tabs([
            "Dataset Preview",
            "About Data"
        ])

    with tab1:
        st.subheader("Dataset Preview")
        st.dataframe(filtered_df.head())

        st.divider()

        st.subheader("Key Performance Indicators")

        col1, col2, col3= st.columns(3)
        col4, col5,col6 = st.columns(3)

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
        if not top_product.empty:
            best_product_name = top_product.iloc[0]["Product_Name"]
            best_product_profit = top_product.iloc[0]["Profit"]
        else:
            best_product_name = "No product found"
            best_product_profit = 0
        # Find top product Line  by profit
        top_product_line = (
            filtered_df.groupby("Product_Line")["Profit"]
            .sum()
            .reset_index()
            .sort_values(by="Profit", ascending=False)
            .head(1)
        )
        if not top_product_line.empty:
            best_product_line = top_product_line.iloc[0]["Product_Line"]
            best_product_line_profit = top_product_line.iloc[0]["Profit"]
        else:
            best_product_line = "No Product Line found"
            best_product_line_profit = 0


        # Define a helper function for framed KPIs
        def framed_metric(label, value, tooltip=None):
            st.markdown(
                f"""
                <div style="border:1px solid #ccc; border-radius:0px; padding:12px; text-align:center; background-color:#f9f9f9;" title="{tooltip if tooltip else ''}">
                    <h4 style="margin:0;">{label}</h4>
                    <p style="font-size:22px; font-weight:bold; margin:0;">{value}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        # Display KPIs inside frames
        with col1:
            framed_metric("🛒 Orders", Number_Orders)
        with col2:
            framed_metric("🏆 Top Product", best_product_name, f"Profit: {round(best_product_profit,2)}")
        with col3:
            formatted_profit = f"{Total_Profit:,.2f}"
            framed_metric("💵 Total Profit", formatted_profit)
        with col4:
            framed_metric("📦 Units Sold", int(Units_Sold))
        with col5:
            framed_metric("🏷️ Top Product Line", best_product_line, f"Profit: {round(best_product_line_profit,2)}")
        with col6:
            formatted_revenue = f"{Total_Revenue:,.2f}"
            framed_metric("💰 Total Revenue", formatted_revenue)

    with tab2:
            st.subheader(" Nike Sales Data")
            st.markdown("""This dataset contant sales transactions of Nike products from both Retail Stores and Online Channels.""")
            st.subheader("Data Dictionary")
            data_dict = {
                "Order_ID": "Unique identifier for each order",
                "Units_Sold": "Number of units sold in the order",
                "Revenue": "Total revenue generated from the order",
                "Profit": "Profit earned from the order",
                "Region": "Geographical region of the sale",
                "Product_Line": "Category of the product",
                "Product_Name": "Specific product name",
                "Sales_Channel": "Channel through which the sale occurred (Retail/Online)",
                "Gender_Category": "Customer gender category",
                "Size": "Product size purchased",
                "Order_Date": "Date of the order"
            }
            dict_df = pd.DataFrame(list(data_dict.items()), columns=["Column", "Description"])
            st.table(dict_df)
            # Optional: Show original dataset preview
            df1 = pd.read_csv("Nike_Sales_Uncleaned.csv")
            if st.checkbox("Show Original Data"):
                st.dataframe(df1.head(10))

# =================================================
# ANALYSIS PAGE
# =================================================

elif page == "Analysis":

    st.title("📊 Exploratory Data Analysis")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Univariate Analysis",
        "Bivariate Analysis",
        "Multivariate Analysis",
        "Insights Q&A"
    ])

    with tab1:
        st.subheader("Univariate Analysis")
        # Product Line Distribution
        st.subheader("Distribution of Product Lines")
        # Sort product lines by count (descending)
        product_counts = filtered_df["Product_Line"].value_counts().sort_values(ascending=True)
        st.bar_chart(product_counts)
        st.markdown("➡️ This chart highlights which product lines dominate sales volume.")
        # Profit Distribution
        fig = px.histogram(filtered_df, x="Profit",title="Profit Distribution")
        st.plotly_chart(fig)
        st.markdown("➡️ The profit distribution shows variability across orders.")
        # Units Sold 
        fig_units = px.box(filtered_df, y="Units_Sold", title="Units Sold Distribution")
        st.plotly_chart(fig_units)
        st.markdown("➡️ The chart reveals purchasing behavior — most customers buy 1–2 units.")



    with tab2:
        st.subheader("Bivariate Analysis")

        # Profit Trend Line
        filtered_df['Order_Date'] = pd.to_datetime(filtered_df['Order_Date'], errors='coerce')
        sales_trend = filtered_df.groupby(filtered_df['Order_Date'].dt.to_period("M"))['Profit'].sum().reset_index()
        sales_trend['Order_Date'] = sales_trend['Order_Date'].dt.to_timestamp()
        fig_trend = px.line(sales_trend, x='Order_Date', y='Profit', title="Monthly Profit Trend")
        st.plotly_chart(fig_trend)
        st.markdown("➡️ This line chart uncovers seasonal profit peaks (Q4) and off-season dips.")


        # Profit by Product Name
        profit_by_product = (filtered_df.groupby("Product_Name")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False).head(10))
        fig_product = px.bar(profit_by_product,x="Product_Name",y="Profit", title="Top 10 Products",text_auto=True,color="Profit",color_continuous_scale="Blues")
        st.plotly_chart(fig_product)
        st.markdown("➡️ Identifies top 10-performing products by profit.")

        #Profit by Region
        profit_by_region = (filtered_df.groupby("Region")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False))
        fig_region = px.pie(profit_by_region,names="Region",values="Profit",title="Profit by Region")
        st.plotly_chart(fig_region, use_container_width=True)
        st.markdown("➡️ Shows which regions drive the most profit.")

        # Sales Channel vs Day Type (Grouped Bar)
        channel_counts = filtered_df.groupby(['Sales_Channel','Day_Type']).size().reset_index(name='Count')
        fig_channel_day = px.bar(channel_counts, x='Day_Type', y='Count', color='Sales_Channel', barmode='group', text='Count', title="Sales Channel by Day Type")
        st.plotly_chart(fig_channel_day)
        st.markdown("➡️ Reveals channel behavior: retail dominates weekdays, while online sales spike on weekends.")


    with tab3:
        st.subheader("Multivariate Analysis")

        # Profit by Region and Product Line
        profit_by_region_line = filtered_df.groupby(["Region", "Product_Line"])["Profit"].sum().reset_index()
        fig_region_line = px.bar(profit_by_region_line, x="Region", y="Profit", color="Product_Line", barmode="group", title="Profit by Region and Product Line")
        st.plotly_chart(fig_region_line)
        st.markdown("➡️ Breaks down profit by region and product line, showing which combinations are most profitable.")

        # Sales by Gender and Product Line
        profit_gender_line = filtered_df.groupby(["Gender_Category", "Product_Line"])["Units_Sold"].sum().reset_index().sort_values(by="Units_Sold", ascending=False)
        fig_gender_line = px.bar(profit_gender_line, x="Gender_Category", y="Units_Sold", color="Product_Line", barmode="group", title="Seales by Gender and Product Line")
        st.plotly_chart(fig_gender_line)
        st.markdown("➡️ Highlights product preferences by gender.")

        # Profit Heatmap (Region vs Sales Channel)
        profit_heatmap = filtered_df.groupby(["Region", "Sales_Channel"])["Profit"].sum().reset_index()
        fig_heatmap = px.density_heatmap(profit_heatmap, x="Region", y="Sales_Channel", z="Profit", color_continuous_scale="Viridis", title="Profit Heatmap by Region & Sales Channel")
        st.plotly_chart(fig_heatmap)
        st.markdown("➡️ The heatmap shows profit intensity across regions and channels.")
    # -------------------------
    # Insights Q&A Tab
    # -------------------------
    with tab4:
        st.subheader("Insights Q&A")

        question = st.selectbox(
            "Select a business question:",
            [
                "Which Top product per region?",
                "Which regions generate the most orders?",
                "Gender distribution per region?",
                "What percentage of 'UNKNOWN' size from total size sold?"
            ]
        )

        if question == "Which Top product per region?":

            # Group by Region and Product, sum profits
            region_product = (filtered_df.groupby(["Region", "Product_Name"])["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False))
            # Select top  product per region
            top1_per_region = region_product.groupby("Region").head(1)

            # Plot
            fig_top1_region = px.bar(top1_per_region, x="Region",y="Profit",color="Product_Name",text="Product_Name",title="Top Product per Region",)
            st.plotly_chart(fig_top1_region)

            # Business insight
            st.markdown("➡️ This chart shows the single most profitable product in each region.")
        elif question == "Which regions generate the most orders?":
            orders_by_region = filtered_df.groupby("Region")["Order_ID"].nunique().reset_index().sort_values(by="Order_ID", ascending=False)
            fig_orders_region = px.bar(orders_by_region, x="Region", y="Order_ID", title="Orders by Region", text_auto=True, color="Order_ID")
            st.plotly_chart(fig_orders_region)
            st.markdown("➡️ Regions with the highest order counts represent strong demand centers.")
        elif question == "Gender distribution per region?":
            gender_region = (
                filtered_df.groupby(["Region", "Gender_Category"])["Units_Sold"]
                .sum()
                .reset_index()
            )
            fig_gender_region = px.bar(gender_region, x="Region", y="Units_Sold", color="Gender_Category",
                                       barmode="group", title="Gender Distribution per Region", text_auto=True)
            st.plotly_chart(fig_gender_region)
            st.markdown("➡️ Gender-based demand varies across regions — tailor regional marketing strategies accordingly.")

        elif question == "What percentage of 'UNKNOWN' size from total size sold?":
            total_units = filtered_df["Units_Sold"].sum()
            unknown_units = filtered_df[filtered_df["Size"] == "UNKNOWN"]["Units_Sold"].sum()
            percentage_unknown = (unknown_units / total_units * 100) if total_units > 0 else 0
            st.metric("Percentage of 'UNKNOWN' Size", f"{percentage_unknown:.2f}%")
            st.markdown("➡️ A significant share of sales records have 'UNKNOWN' sizes.")

# =================================================
# FINAL INSIGHTS PAGE
# =================================================



elif page == "Recommendations":


    st.markdown("""
    ### 💡 Business Recommendations

    - **Seasonal Strategy**:  
      Intensify marketing planning for Q4 to maximize peak season profits.  Develop off-season 
      promotions to stabilize revenue during low months.  

    - **Product Strategy**:  
      Launch targeted campaigns for Kids’ Lifestyle and Women’s Training products.Explore bundling 
      and upselling opportunities in these high-profit categories.  

    - **Regional Focus**:  
      Prioritize Bangalore,Delhi, andKolkata with localized promotions and supply chain support.Investigate 
      underperforming regions to identify barriers and growth opportunities.  

    - **Channel Optimization**:  
       Boost Online promotions during weekends to capture demand spikes.Maintain Retail engagement during
       weekdays with in-store campaigns and loyalty programs. 

    - **Bundle/upsell strategy**: 
       Since most customers buy only 1–2 units, encourage multi-unit purchases through discounts 
       (e.g., “Buy 3, get 1 free”) or product bundles.


    """)

# =================================================
# GLOBAL FOOTER
# =================================================

st.markdown(
    """
    <hr style="margin-top:30px; margin-bottom:10px;">
    <div style="text-align:center; color:gray; font-size:14px;">
        © 2026 Nike Sales Dashboard | Developed by Eng.Amal Mohamed-Khair | Email: amal4khair@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)
