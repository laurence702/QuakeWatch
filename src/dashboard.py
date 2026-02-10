import streamlit as st
import pandas as pd
import plotly.express as px
import os
from src.subscription_manager import add_subscriber

def run_dashboard():
    """
    Runs the Streamlit dashboard.
    """
    st.set_page_config(layout="wide")
    st.title("Earthquake Analysis Dashboard 🌎")

    # --- Load Data ---
    @st.cache_data
    def load_data():
        silver_dir = "data/silver"
        if not os.path.exists(silver_dir):
            return pd.DataFrame()
        silver_files = [f for f in os.listdir(silver_dir) if f.endswith('.parquet')]
        if not silver_files:
            return pd.DataFrame()
            
        latest_silver_file = max(silver_files, key=lambda f: os.path.getmtime(os.path.join(silver_dir, f)))
        file_path = os.path.join(silver_dir, latest_silver_file)
        df = pd.read_parquet(file_path)
        df = df.sort_values('time', ascending=False)
        return df

    df = load_data()

    # --- Sidebar ---
    st.sidebar.header("Filters")
    
    if not df.empty:
        min_mag = st.sidebar.slider("Minimum Magnitude", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
        filtered_df = df[df['magnitude'] >= min_mag]
    else:
        filtered_df = df
        st.sidebar.warning("No data loaded.")

    # --- Subscription Form in Sidebar ---
    st.sidebar.header("Subscribe to Alerts")
    with st.sidebar.form("subscription_form"):
        email = st.text_input("Email")
        location = st.text_input("Location (e.g., 'San Francisco, CA')")
        submitted = st.form_submit_button("Subscribe")
        
        if submitted:
            if email and location:
                try:
                    add_subscriber(email, location)
                    st.success(f"Successfully subscribed {email} for alerts near {location}!")
                except Exception as e:
                    st.error(f"Failed to subscribe: {e}")
            else:
                st.warning("Please provide both email and location.")


    # --- Main Page Layout ---
    if df.empty:
        st.warning("No data found. Please run the ingestion and processing scripts (`run.sh`) first.")
        return

    col1, col2 = st.columns((2, 1))

    with col1:
        st.header("Earthquake Map")
        if not filtered_df.empty:
            fig = px.scatter_geo(
                filtered_df,
                lat='latitude',
                lon='longitude',
                size='magnitude',
                color='magnitude',
                hover_name='place',
                projection="natural earth",
                title="Earthquakes around the World",
                color_continuous_scale=px.colors.sequential.Plasma
            )
            fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No earthquakes match the current filter settings.")

    with col2:
        st.header("Summary Statistics")
        st.metric("Total Earthquakes (Filtered)", len(filtered_df))
        if not filtered_df.empty:
            st.metric("Highest Magnitude", f"{filtered_df['magnitude'].max():.2f}")
            st.metric("Most Recent Earthquake", filtered_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S').iloc[0])

    st.header("Earthquake Data Table")
    st.dataframe(filtered_df[['time', 'place', 'magnitude', 'depth', 'tsunami']], use_container_width=True)


if __name__ == "__main__":
    run_dashboard()
