# app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import requests
import json
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import time
import pydeck as pdk




# Set Streamlit layout
st.set_page_config(page_title="PhonePe Dashboard", layout="wide")

# ✅ Title
st.title(" PhonePe Dashboard")

# ✅ Setup PostgreSQL engine
engine = create_engine("postgresql+psycopg2://postgres:san24@localhost/demo")

# ✅ Run SQL Query Function
def run_query(sql_query):
    return pd.read_sql_query(sql_query, engine)

# ✅ Query 1: Total Transaction Amount by State
business_case = st.sidebar.selectbox(
    "Choose a Business Case",
    [
        "User Registration Analysis",
        "User Engagement & Growth Strategy",
        "Decoding Transaction Dynamics on PhonePe",
        "Device Dominance and User Engagement",
        "Insurance Penetration & Growth Potential"
    ]
)
if business_case == "User Registration Analysis":
    
    st.header("📈 User Registration Analysis")

    # Query 1 - Top 10 States by Registered Users
    query1 = '''
    SELECT "State", SUM("Total_Registered_Users") AS total_users 
    FROM agg_user_data 
    GROUP BY "State" 
    ORDER BY total_users DESC 
    LIMIT 10;
    '''
    df1 = pd.read_sql(query1, engine)
    st.subheader("Top 10 States by Registered Users")
    fig1 = px.bar(df1, x="State", y="total_users", color="State", title="Top 10 States by Total Registered Users")
    st.plotly_chart(fig1)
    with st.expander("Show Raw Data"):
        st.dataframe(df1)

    # Query 2 - Consistent Registration Across Quarters
    query2 = '''
    SELECT 
        "State", 
        COUNT(DISTINCT CONCAT("Year", '-', "Quater")) AS active_quarters,
        SUM("Total_Registered_Users") AS total_registrations
    FROM agg_user_data
    GROUP BY "State"
    HAVING COUNT(DISTINCT CONCAT("Year", '-', "Quater")) >= 4
    ORDER BY total_registrations DESC;
    '''
    df2 = pd.read_sql(query2, engine)
    st.subheader("States with Consistent Quarterly Registrations")
    fig2 = px.bar(df2, x="State", y="total_registrations", color="State",
                  title="States with High Registrations Across 4+ Quarters")
    st.plotly_chart(fig2)
    with st.expander("Show Raw Data"):
        st.dataframe(df2)

    # Query 3 - States with >50% Spike in Registrations
    query3 = '''
    WITH quarter_data AS (
        SELECT 
            "State", 
            "Year", 
            "Quater",
            SUM("Total_Registered_Users") AS users,
            ROW_NUMBER() OVER (PARTITION BY "State" ORDER BY "Year", "Quater") AS rn
        FROM agg_user_data
        GROUP BY "State", "Year", "Quater"
    ),
    curr_prev AS (
        SELECT 
            curr."State",
            curr.users AS current_users,
            prev.users AS previous_users,
            ROUND(100.0 * (curr.users - prev.users) / NULLIF(prev.users, 0), 2) AS growth_percent
        FROM quarter_data curr
        JOIN quarter_data prev 
            ON curr."State" = prev."State" AND curr.rn = prev.rn + 1
    )
    SELECT * FROM curr_prev
    WHERE growth_percent > 50
    ORDER BY growth_percent DESC
    LIMIT 10;
    '''
    df3 = pd.read_sql(query3, engine)
    st.subheader("States with >50% Spike in Registrations")
    fig3 = px.bar(df3, x="State", y="growth_percent", color="State",
                  title="States with >50% Registration Growth", 
                  hover_data=["current_users", "previous_users"])
    st.plotly_chart(fig3)
    with st.expander("Show Raw Data"):
        st.dataframe(df3)

    # Query 4 - Repeated Top Registration States 
    query4 = '''
    SELECT 
        "State", 
        SUM("Total_Registered_Users") AS total_users
    FROM agg_user_data
    GROUP BY "State"
    ORDER BY total_users DESC
    LIMIT 10;
    '''
    df4 = pd.read_sql(query4, engine)
    st.subheader("Repeat - Top States by Total Registrations")
    fig4 = px.bar(df4, x="State", y="total_users", color="State", 
                  title="Repeat: Top States by Total Users")
    st.plotly_chart(fig4)
    with st.expander("Show Raw Data"):
        st.dataframe(df4)

    # Query 5 - High Registration but Low Engagement
    query5 = '''
    SELECT 
        "State",
        SUM("Total_Registered_Users") AS total_registrations,
        SUM("Total_App_Opens") AS total_opens,
        ROUND(1.0 * SUM("Total_App_Opens") / NULLIF(SUM("Total_Registered_Users"), 0), 2) AS opens_per_user
    FROM agg_user_data
    GROUP BY "State"
    ORDER BY opens_per_user ASC
    LIMIT 10;
    '''
    df5 = pd.read_sql(query5, engine)
    st.subheader("States with High Registrations but Low App Engagement")
    fig5 = px.bar(df5, x="State", y="opens_per_user", color="State", 
                  title="States with Low App Opens per Registered User", 
                  hover_data=["total_registrations", "total_opens"])
    st.plotly_chart(fig5)
    with st.expander("Show Raw Data"):
        st.dataframe(df5)


    
if business_case == "User Engagement & Growth Strategy":
    st.header("📈 User Engagement & Growth Strategy")

    # Query 1 - States with Highest Registered Users
    query1 = '''
    SELECT "State", SUM("Registered_Users") AS total_users
    FROM map_us_df
    GROUP BY "State"
    ORDER BY total_users DESC;
    '''
    df1 = pd.read_sql(query1, engine)
    st.subheader("States with Highest Registered Users")
    fig1 = px.bar(df1, x="State", y="total_users", color="State", 
                  title="Total Registered Users by State")
    st.plotly_chart(fig1)
    with st.expander("Show Raw Data"):
        st.dataframe(df1)

    # Query 2 - App Opens per User Ratio
    query2 = '''
    SELECT "State", 
           SUM("App_Opens") AS opens, 
           SUM("Registered_Users") AS users,
           ROUND(SUM("App_Opens") / NULLIF(SUM("Registered_Users"), 0), 2) AS engagement_ratio
    FROM map_us_df
    GROUP BY "State"
    ORDER BY engagement_ratio DESC;
    '''
    df2 = pd.read_sql(query2, engine)
    st.subheader("App Opens per User Ratio")
    fig2 = px.bar(df2, x="State", y="engagement_ratio", color="State",
                  title="User Engagement Ratio by State",
                  hover_data=["opens", "users"])
    st.plotly_chart(fig2)
    with st.expander("Show Raw Data"):
        st.dataframe(df2)

    # Query 3 - Fastest Growing User Base by Quarter
    query3 = '''
    SELECT "Year", "Quater", SUM("Total_Registered_Users") AS total_users
    FROM agg_user_data
    GROUP BY "Year", "Quater"
    ORDER BY "Year", "Quater";
    '''
    df3 = pd.read_sql(query3, engine)
    st.subheader("Fastest Growing User Base by Quarter")
    fig3 = px.line(df3, x="Quater", y="total_users", color="Year", markers=True,
                   title="User Growth Trend by Quarter")
    st.plotly_chart(fig3)
    with st.expander("Show Raw Data"):
        st.dataframe(df3)

    # Query 4 - Top 5 Districts with Most Registered Users
    query4 = '''
    SELECT "District", "Registered_Users"
    FROM top_user_df
    ORDER BY "Registered_Users" DESC
    LIMIT 5;
    '''
    df4 = pd.read_sql(query4, engine)
    st.subheader("Top 5 Districts with Most Registered Users")
    fig4 = px.bar(df4, x="District", y="Registered_Users", color="District",
                  title="Top 5 Districts by Registered Users")
    st.plotly_chart(fig4)
    with st.expander("Show Raw Data"):
        st.dataframe(df4)

    # Query 5 - States with Consistent App Engagement Across Quarters
    query5 = '''
    SELECT "State", "Year", "Quater", SUM("Total_App_Opens") AS opens
    FROM agg_user_data
    GROUP BY "State", "Year", "Quater"
    ORDER BY "State", "Year", "Quater";
    '''
    df5 = pd.read_sql(query5, engine)
    st.subheader("States with Consistent App Engagement (Across Quarters)")
    fig5 = px.line(df5, x="Quater", y="opens", color="State", line_group="State",
                   title="Quarterly App Engagement by State", markers=True)
    st.plotly_chart(fig5)
    with st.expander("Show Raw Data"):
        st.dataframe(df5)


if business_case == "Decoding Transaction Dynamics on PhonePe":
    st.header("📊 Decoding Transaction Dynamics on PhonePe")

    # Query 1 - Total Transaction Amount by State
    query1 = '''
    SELECT "State", SUM("Transaction_Amount") AS total_amount
    FROM agg_transcation_data
    GROUP BY "State"
    ORDER BY total_amount DESC;
    '''
    df1 = pd.read_sql(query1, engine)
    st.subheader("Total Transaction Amount by State")
    fig1 = px.bar(df1, x="State", y="total_amount", color="State", 
                  title="Total Transaction Volume by State (₹)")
    st.plotly_chart(fig1)
    with st.expander("Show Raw Data"):
        st.dataframe(df1)

    # Query 2 - Transaction Growth Trend by Year and Quarter
    query2 = '''
    SELECT "Year", "Quater", SUM("Transaction_Count") AS total_transactions
    FROM agg_transcation_data
    GROUP BY "Year", "Quater"
    ORDER BY "Year", "Quater";
    '''
    df2 = pd.read_sql(query2, engine)
    st.subheader("Transaction Growth Trend by Year & Quarter")
    fig2 = px.line(df2, x="Quater", y="total_transactions", color="Year", markers=True,
                   title="Quarterly Transaction Count Growth")
    st.plotly_chart(fig2)
    with st.expander("Show Raw Data"):
        st.dataframe(df2)

    # ✅ Query 3 - Payment Categories by Transaction Volume
    query3 = '''
    SELECT "Category" AS transaction_type, 
        SUM("Transaction_Count") AS total_count
    FROM agg_transcation_data
    GROUP BY transaction_type
    ORDER BY total_count DESC;
    '''
    df3 = pd.read_sql(query3, engine)

    st.subheader("📊 Payment Categories by Transaction Volume")
    fig3 = px.bar(df3, x="transaction_type", y="total_count", color="transaction_type",
                title="Transaction Volume by Category")
    st.plotly_chart(fig3)

    with st.expander("🔍 Show Raw Data"):
        st.dataframe(df3)

    # Query 4 - Top 5 States with Declining Transaction Amounts Over Quarters
    query4 = '''
    WITH ordered_data AS (
        SELECT 
            "State", 
            "Year", 
            "Quater",
            SUM("Transaction_Amount") AS total_amount,
            ROW_NUMBER() OVER (PARTITION BY "State" ORDER BY "Year", "Quater") AS rn
        FROM agg_transcation_data
        GROUP BY "State", "Year", "Quater"
    ),
    trend_data AS (
        SELECT 
            curr."State",
            curr.total_amount AS current_amount,
            prev.total_amount AS previous_amount,
            (curr.total_amount - prev.total_amount) AS diff
        FROM ordered_data curr
        JOIN ordered_data prev
            ON curr."State" = prev."State" AND curr.rn = prev.rn + 1
    ),
    decline_counts AS (
        SELECT 
            "State",
            COUNT(*) FILTER (WHERE diff < 0) AS declining_quarters
        FROM trend_data
        GROUP BY "State"
    )
    SELECT * 
    FROM decline_counts
    ORDER BY declining_quarters DESC
    LIMIT 5;
    '''
    df4 = pd.read_sql(query4, engine)
    st.subheader("Top 5 States with Declining Transaction Amounts")
    fig4 = px.bar(df4, x="State", y="declining_quarters", color="State",
                  title="States with Most Declining Quarters in Transaction Amount")
    st.plotly_chart(fig4)
    with st.expander("Show Raw Data"):
        st.dataframe(df4)

    # ✅ Query 5 - Average Transaction Value by State
    query5 = '''
    SELECT "State", 
        ROUND(SUM("Transaction_Amount")::numeric / NULLIF(SUM("Transaction_Count"), 0), 2) AS avg_transaction_value
    FROM agg_transcation_data
    GROUP BY "State"
    ORDER BY avg_transaction_value DESC;
    '''
    df5 = pd.read_sql(query5, engine)

    st.subheader("📈 Average Transaction Value by State")
    fig5 = px.bar(df5, x="State", y="avg_transaction_value", color="State",
                title="State-wise Average Value per Transaction (₹)")
    st.plotly_chart(fig5)

    with st.expander("🔍 Show Raw Data"):
        st.dataframe(df5)




if business_case == "Device Dominance and User Engagement":
    st.header("📱 Device Dominance and User Engagement")

    # Query 1 - Registered Users by Device Brand
    query1 = '''
    SELECT "Brand" AS device_brand, SUM("Total_Registered_Users") AS total_users
    FROM agg_user_data
    GROUP BY device_brand
    ORDER BY total_users DESC;
    '''
    df1 = pd.read_sql(query1, engine)
    st.subheader("Registered Users by Device Brand")
    fig1 = px.bar(df1, x="device_brand", y="total_users", color="device_brand",
                  title="Total Registered Users by Device Brand")
    st.plotly_chart(fig1)
    with st.expander("Show Raw Data"):
        st.dataframe(df1)

        # ✅ Query 2 - Average Insurance Transaction Value by State
    query2 = '''
        SELECT "State", 
            ROUND((SUM("Transaction_Amount") / NULLIF(SUM("Transaction_Count"), 0))::numeric, 2) AS avg_value
        FROM agg_insurance_data
        GROUP BY "State"
        ORDER BY avg_value DESC;
    '''
    df2 = pd.read_sql(query2, engine)

    # ✅ Streamlit Visualization
    st.subheader("💰 Average Insurance Transaction Value by State")
    fig2 = px.bar(df2, x="State", y="avg_value", color="State",
                title="Average Insurance Transaction Value (INR)",
                labels={"avg_value": "Avg Transaction Value"},
                height=500)
    st.plotly_chart(fig2)

    with st.expander("🔍 Show Raw Data"):
        st.dataframe(df2)


    # # --- Get GeoJSON from GitHub ---
    # geo_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    # response = requests.get(geo_url)
    # geojson_data = response.json()

    # # --- SQL Query to Get State-wise Registered Users ---
    # query = '''
    # SELECT "State" AS state, SUM("Total_Registered_Users") AS total_users
    # FROM agg_user_data
    # GROUP BY state
    # ORDER BY total_users DESC;
    # '''
    # df = pd.read_sql(query, engine)

    # # --- Choropleth Map Visualization ---
    # fig = go.Figure(data=go.Choropleth(
    #     geojson=geojson_data,
    #     featureidkey='properties.ST_NM',
    #     locationmode='geojson-id',
    #     locations=df['state'],               # Must match ST_NM values
    #     z=df['total_users'],                # Value to be color coded

    #     autocolorscale=False,
    #     colorscale='Blues',
    #     marker_line_color='white',

    #     colorbar=dict(
    #         title={'text': "Registered Users"},
    #         thickness=15,
    #         len=0.35,
    #         bgcolor='rgba(255,255,255,0.6)',
    #         xanchor='left',
    #         x=0.01,
    #         yanchor='bottom',
    #         y=0.05
    #     )
    # ))

    # fig.update_geos(
    #     visible=False,
    #     projection=dict(
    #         type='conic conformal',
    #         parallels=[12.472944444, 35.172805555556],
    #         rotation={'lat': 24, 'lon': 80}
    #     ),
    #     lonaxis={'range': [68, 98]},
    #     lataxis={'range': [6, 38]}
    # )

    # fig.update_layout(
    #     title=dict(
    #         text="PhonePe Registered Users by State",
    #         xanchor='center',
    #         x=0.5,
    #         yref='paper',
    #         yanchor='bottom',
    #         y=1,
    #         pad={'b': 10}
    #     ),
    #     margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
    #     height=600,
    #     width=900
    # )

    # # --- Streamlit Display ---
    # st.subheader("📍 Registered Users by State (Map View)")
    # st.plotly_chart(fig)

    # --- Expand Raw Data ---
    # with st.expander("Show Raw Data"):
    #     st.dataframe(df)
    #  st.dataframe(df3)





  
# ✅ SQL Query for State-wise Total Users
    # ✅ Fetch data from SQL
    #     # ✅ Query to fetch state-wise registered users
    # query3 = '''
    # SELECT "State" AS state, SUM("Total_Registered_Users") AS total_users
    # FROM agg_user_data
    # GROUP BY state
    # ORDER BY total_users DESC;
    # '''

    # df3 = pd.read_sql(query3, engine)

    # # ✅ Hardcoded coordinates for Indian states (centroids)
    # state_coordinates = {
    #     'andhra-pradesh': (15.9129, 79.7400), 'arunachal-pradesh': (28.2180, 94.7278),
    #     'assam': (26.2006, 92.9376), 'bihar': (25.0961, 85.3131), 'chhattisgarh': (21.2787, 81.8661),
    #     'goa': (15.2993, 74.1240), 'gujarat': (22.2587, 71.1924), 'haryana': (29.0588, 76.0856),
    #     'himachal-pradesh': (31.1048, 77.1734), 'jharkhand': (23.6102, 85.2799), 'karnataka': (15.3173, 75.7139),
    #     'kerala': (10.8505, 76.2711), 'madhya-pradesh': (22.9734, 78.6569), 'maharashtra': (19.7515, 75.7139),
    #     'manipur': (24.6637, 93.9063), 'meghalaya': (25.4670, 91.3662), 'mizoram': (23.1645, 92.9376),
    #     'nagaland': (26.1584, 94.5624), 'odisha': (20.9517, 85.0985), 'punjab': (31.1471, 75.3412),
    #     'rajasthan': (27.0238, 74.2179), 'sikkim': (27.5330, 88.5122), 'tamil-nadu': (11.1271, 78.6569),
    #     'telangana': (18.1124, 79.0193), 'tripura': (23.9408, 91.9882), 'uttar-pradesh': (26.8467, 80.9462),
    #     'uttarakhand': (30.0668, 79.0193), 'west-bengal': (22.9868, 87.8550), 'delhi': (28.7041, 77.1025),
    #     'jammu-and-kashmir': (33.7782, 76.5762), 'ladakh': (34.1526, 77.5770), 'puducherry': (11.9416, 79.8083),
    #     'chandigarh': (30.7333, 76.7794), 'andaman-and-nicobar-islands': (11.7401, 92.6586),
    #     'dadra-and-nagar-haveli-and-daman-and-diu': (20.4283, 72.8397)
    # }

    # # ✅ Clean state names for coordinate matching
    # df3["state_cleaned"] = df3["state"].str.lower().str.replace(" ", "-")
    # df3["lat"] = df3["state_cleaned"].map(lambda x: state_coordinates.get(x, (None, None))[0])
    # df3["lon"] = df3["state_cleaned"].map(lambda x: state_coordinates.get(x, (None, None))[1])

    # # ✅ Drop states without coordinates
    # df3 = df3.dropna(subset=["lat", "lon"])

    # # ✅ Plotly Geo Map
    # fig = px.scatter_geo(
    #     df3,
    #     lat="lat",
    #     lon="lon",
    #     text="state",
    #     size="total_users",
    #     size_max=60,
    #     color="total_users",
    #     hover_name="state",
    #     color_continuous_scale="blues",
    #     title="📍 State-wise Registered Users on PhonePe (India)"
    # )

    # fig.update_geos(
    #     scope="asia",
    #     resolution=50,
    #     showcountries=True,
    #     showsubunits=True,
    #     countrycolor="Black"
    # )

    # st.plotly_chart(fig, use_container_width=True)

    # # ✅ Expandable raw data
    # with st.expander("📄 Raw Data"):
    #     st.dataframe(df3)



    # ✅ SQL Query to Fetch Registered Users by State
    query3 = '''
        SELECT "State" AS state, SUM("Total_Registered_Users") AS total_users
        FROM agg_user_data
        GROUP BY state
        ORDER BY total_users DESC;
    '''
    df3 = pd.read_sql(query3, engine)

    # ✅ Hardcoded Coordinates for Indian States
    state_coordinates = {
        'andhra-pradesh': (15.9129, 79.7400), 'arunachal-pradesh': (28.2180, 94.7278),
        'assam': (26.2006, 92.9376), 'bihar': (25.0961, 85.3131), 'chhattisgarh': (21.2787, 81.8661),
        'goa': (15.2993, 74.1240), 'gujarat': (22.2587, 71.1924), 'haryana': (29.0588, 76.0856),
        'himachal-pradesh': (31.1048, 77.1734), 'jharkhand': (23.6102, 85.2799), 'karnataka': (15.3173, 75.7139),
        'kerala': (10.8505, 76.2711), 'madhya-pradesh': (22.9734, 78.6569), 'maharashtra': (19.7515, 75.7139),
        'manipur': (24.6637, 93.9063), 'meghalaya': (25.4670, 91.3662), 'mizoram': (23.1645, 92.9376),
        'nagaland': (26.1584, 94.5624), 'odisha': (20.9517, 85.0985), 'punjab': (31.1471, 75.3412),
        'rajasthan': (27.0238, 74.2179), 'sikkim': (27.5330, 88.5122), 'tamil-nadu': (11.1271, 78.6569),
        'telangana': (18.1124, 79.0193), 'tripura': (23.9408, 91.9882), 'uttar-pradesh': (26.8467, 80.9462),
        'uttarakhand': (30.0668, 79.0193), 'west-bengal': (22.9868, 87.8550), 'delhi': (28.7041, 77.1025),
        'jammu-and-kashmir': (33.7782, 76.5762), 'ladakh': (34.1526, 77.5770), 'puducherry': (11.9416, 79.8083),
        'chandigarh': (30.7333, 76.7794), 'andaman-and-nicobar-islands': (11.7401, 92.6586),
        'dadra-and-nagar-haveli-and-daman-and-diu': (20.4283, 72.8397)
    }

    # ✅ Clean State Names and Map Coordinates
    df3["state_cleaned"] = df3["state"].str.lower().str.replace(" ", "-")
    df3["lat"] = df3["state_cleaned"].map(lambda x: state_coordinates.get(x, (None, None))[0])
    df3["lon"] = df3["state_cleaned"].map(lambda x: state_coordinates.get(x, (None, None))[1])
    df3 = df3.dropna(subset=["lat", "lon"])  # Drop states with missing coordinates

    # ✅ Create Geo Plot Focused on India
    fig = px.scatter_geo(
        df3,
        lat="lat",
        lon="lon",
        text="state",
        size="total_users",
        size_max=60,
        color="total_users",
        color_continuous_scale="blues",
        hover_name="state",
        title="📍 State-wise Registered Users on PhonePe (India)"
    )

    # ✅ Limit Geo Scope to India Region
    fig.update_geos(
        center={"lat": 22.0, "lon": 80.0},
        projection_scale=5.5,  # Zoom level
        fitbounds="locations",
        showcountries=True,
        countrycolor="black",
        visible=False
    )

    # ✅ Show Plotly Chart
    st.plotly_chart(fig, use_container_width=True)

    # ✅ Expandable Raw Data View
    with st.expander("📄 Raw Data"):
        st.dataframe(df3)


    # Query 4 - Devices with Low Engagement but High Registrations
    query4 = '''
    SELECT "Brand" AS device_brand, 
           SUM("Total_Registered_Users") AS users, 
           SUM("Total_App_Opens") AS opens
    FROM agg_user_data
    GROUP BY device_brand
    HAVING SUM("Total_Registered_Users") > 1 AND SUM("Total_App_Opens") < 1
    ORDER BY users DESC;
    '''
    df4 = pd.read_sql(query4, engine)
    st.subheader("Devices with Low Engagement but High Registrations")
    fig4 = px.bar(df4, x="device_brand", y="users", color="device_brand",
                  title="Low Engagement Devices (High Registrations, Low App Opens)",
                  hover_data=["opens"])
    st.plotly_chart(fig4)
    with st.expander("Show Raw Data"):
        st.dataframe(df4)

    # # Query 5 - Most Popular Device per State
    # query5 = '''
    # SELECT "State", "Brand", "Total_Registered_Users"
    # FROM (
    #   SELECT "State", "Brand", "Total_Registered_Users",
    #          RANK() OVER (PARTITION BY "State" ORDER BY "Total_Registered_Users" DESC) AS rnk
    #   FROM agg_user_data
    # ) AS ranked
    # WHERE rnk = 1;
    # '''
    # df5 = pd.read_sql(query5, engine)
    # st.subheader("Most Popular Device per State")
    # fig5 = px.treemap(df5, path=['State', 'Brand'], values='Total_Registered_Users',
    #                   title="Most Popular Device by State")
    # st.plotly_chart(fig5)
    # with st.expander("Show Raw Data"):
    #     st.dataframe(df5)


    # Step 1: Read Data
    query5 = '''
        SELECT "State", "Brand", "Total_Registered_Users"
        FROM (
            SELECT "State", "Brand", "Total_Registered_Users",
                RANK() OVER (PARTITION BY "State" ORDER BY "Total_Registered_Users" DESC) AS rnk
            FROM agg_user_data
        ) AS ranked
        WHERE rnk = 1;
    '''
    df5 = pd.read_sql(query5, engine)

    # Step 2: Dropdown for Brand Selection
    brand_list = df5['Brand'].unique().tolist()
    selected_brand = st.selectbox("🔍 Select a Brand to View Its State-wise Dominance", brand_list)

    # Step 3: Filtered DataFrame
    filtered_df = df5[df5['Brand'] == selected_brand]

    # Step 4: Display Summary
    st.markdown(f"### 📱 {selected_brand} is the most popular in **{len(filtered_df)}** states.")

    # Step 5: Bar Chart
    fig = px.bar(
        filtered_df.sort_values("Total_Registered_Users", ascending=False),
        x='State',
        y='Total_Registered_Users',
        title=f"📊 States where {selected_brand} is Most Popular",
        text='Total_Registered_Users',
        labels={'Total_Registered_Users': 'Registered Users'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    # Step 6: Raw Data View
    with st.expander("📄 Show Filtered Data"):
        st.dataframe(filtered_df)




if business_case == "Insurance Penetration & Growth Potential":
    st.header("🛡️ Insurance Penetration & Growth Potential")

    # Query 1 - Total Insurance Count and Amount by State
    query1 = '''
    SELECT "State", SUM("Transaction_Count") AS total_count, SUM("Transaction_Amount") AS total_value
    FROM agg_insurance_data
    GROUP BY "State"
    ORDER BY total_value DESC;
    '''
    df1 = pd.read_sql(query1, engine)
    st.subheader("Total Insurance Count and Amount by State")
    fig1 = px.bar(df1, x="State", y="total_value", color="State",
                  title="Insurance Value by State",
                  hover_data=["total_count"])
    st.plotly_chart(fig1)
    with st.expander("Show Raw Data"):
        st.dataframe(df1)

    # ✅ Query 2 - State-wise Average Insurance Value
    query2 = '''
    SELECT "State", 
        ROUND((SUM("Transaction_Amount") / NULLIF(SUM("Transaction_Count"), 0))::numeric, 2) AS avg_value
    FROM agg_insurance_data
    GROUP BY "State"
    ORDER BY avg_value DESC;
    '''
    df2 = pd.read_sql(query2, engine)

    # ✅ Streamlit Visualization
    st.subheader("📊 State-wise Average Insurance Value")
    fig2 = px.bar(df2, x="State", y="avg_value", color="State",
                title="Average Insurance Value per Transaction by State",
                labels={"avg_value": "Avg Transaction Value (₹)"},
                height=500)
    st.plotly_chart(fig2)

    # ✅ Expandable Raw Data
    with st.expander("🔍 Show Raw Data"):
        st.dataframe(df2)


    # Query 3 - Quarterly Insurance Growth
    query3 = '''
    SELECT "Year", "Quater", SUM("Transaction_Count") AS total_insurance
    FROM agg_insurance_data
    GROUP BY "Year", "Quater"
    ORDER BY "Year", "Quater";
    '''
    df3 = pd.read_sql(query3, engine)
    st.subheader("Quarterly Insurance Growth")
    fig3 = px.line(df3, x="Quater", y="total_insurance", color="Year", markers=True,
                   title="Quarterly Insurance Transaction Count")
    st.plotly_chart(fig3)
    with st.expander("Show Raw Data"):
        st.dataframe(df3)

    # Query 4 - Top 5 Underperforming States (Lowest Insurance Count)
    query4 = '''
    SELECT "State", SUM("Transaction_Count") AS total_insurance
    FROM agg_insurance_data
    GROUP BY "State"
    ORDER BY total_insurance ASC
    LIMIT 5;
    '''
    df4 = pd.read_sql(query4, engine)
    st.subheader("Top 5 Underperforming States (Lowest Insurance Count)")
    fig4 = px.bar(df4, x="State", y="total_insurance", color="State",
                  title="Lowest Insurance Adoption by State")
    st.plotly_chart(fig4)
    with st.expander("Show Raw Data"):
        st.dataframe(df4)

    # Query 5 - High Transaction States with Low Insurance Penetration
    query5 = '''
    SELECT t."State", SUM(t."Transaction_Amount") AS txn_amount, 
           COALESCE(i.insurance_count, 0) AS insurance_count
    FROM agg_transcation_data t
    LEFT JOIN (
      SELECT "State", SUM("Transaction_Amount") AS insurance_count
      FROM agg_insurance_data
      GROUP BY "State"
    ) i ON t."State" = i."State"
    GROUP BY t."State", i.insurance_count
    ORDER BY txn_amount DESC, insurance_count ASC
    LIMIT 10;
    '''
    df5 = pd.read_sql(query5, engine)
    st.subheader("High Transaction States with Low Insurance Penetration")
    fig5 = px.bar(df5, x="State", y="txn_amount", color="State",
                  title="States with High Transactions but Low Insurance Coverage",
                  hover_data=["insurance_count"])
    st.plotly_chart(fig5)
    with st.expander("Show Raw Data"):
        st.dataframe(df5)



