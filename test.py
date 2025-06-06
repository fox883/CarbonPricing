import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)


# Helper function to get today's prefix in YYMMDD format
def get_date_prefix():
    return datetime.now().strftime("%y%m%d")


# Function to generate next project ID
def get_next_project_id():
    try:
        today_prefix = datetime.now().strftime("%y%m%d")

        # Step 1: Get all projects with today's prefix
        response = supabase.table("projects").select("project_id") \
            .like("project_id", f"{today_prefix}%").execute()

        # Step 2: Count how many already exist
        count = len(response.data) if response.data else 0

        # Step 3: Add 1 to get the next number
        next_number = count + 1

        return f"{today_prefix}-req{next_number}"

    except Exception as e:
        st.error(f"Error generating project ID: {str(e)}")
        return f"{today_prefix}-req1"


# Function to save project with retry on duplicate key error
def save_project(data):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = supabase.table("projects").insert(data).execute()
            st.success(f"✅ Project `{data['project_id']}` saved successfully!")
            return True
        except Exception as e:
            error_msg = str(e)
            if "duplicate key value violates unique constraint" in error_msg:
                st.warning(f"Attempt {attempt + 1}: Duplicate ID detected. Regenerating...")
                new_id = get_next_project_id()
                if new_id:
                    st.info(f"New ID generated: `{new_id}`")
                    data["project_id"] = new_id
                    continue
                else:
                    st.error("Failed to regenerate a unique project ID.")
                    return False
            else:
                st.error(f"❌ Failed to save project after {attempt + 1} attempts: {error_msg}")
                return False
    return False


# Financial model functions
def calculate_npv(cash_flows, discount_rate):
    """Calculate Net Present Value of cash flows"""
    years = np.arange(len(cash_flows))
    discounted = cash_flows / (1 + discount_rate) ** years
    return np.sum(discounted)


def carbon_revenue_model(area_hectares, carbon_price_per_ton,
                         sequestration_rate, project_years):
    """Model carbon revenue based on project parameters"""
    yearly_sequestration = area_hectares * sequestration_rate
    revenues = [yearly_sequestration * carbon_price_per_ton for _ in range(project_years)]
    return np.array(revenues)


# Streamlit UI
st.set_page_config(page_title="🌿 Greenbridge Carbon Project Manager", layout="wide")
st.title("🌿 Greenbridge Capital - Carbon Project Financial Analysis")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🔍 Project Lookup", "🆕 New Project", "📊 Financial Modeling"])

# --- Page 1: Project Lookup ---
if page == "🔍 Project Lookup":
    st.subheader("Search Existing Projects")

    col1, col2 = st.columns([3, 1])
    with col1:
        project_id_input = st.text_input("Enter Project ID (e.g., 250406-req1)")
    with col2:
        fetch_button = st.button("🔍 Fetch Project")

    if fetch_button and project_id_input:
        try:
            response = supabase.table("projects").select("*").eq("project_id", project_id_input).execute()

            if response.data:
                project_data = response.data[0]
                st.success(f"✅ Project Found: {project_data['project_id']}")

                # Display basic info
                st.markdown("### 📋 Project Details")
                col1, col2, col3 = st.columns(3)
                col1.metric("Project Type", project_data["project_type_category"])
                col2.metric("Status", project_data["project_status"])
                col3.metric("Submission Date", project_data["project_submission_date"])

                # Financial data section (demo only)
                st.markdown("### 💰 Financial Summary")
                cash_flows = np.array([-1000000, 200000, 300000, 400000, 500000])
                discount_rate = 0.1
                npv = calculate_npv(cash_flows, discount_rate)

                fig = px.bar(x=["Year 0", "Year 1", "Year 2", "Year 3", "Year 4"],
                             y=cash_flows, title="Cash Flows")
                st.plotly_chart(fig)

                st.metric("Net Present Value", f"${npv:,.2f}")

            else:
                st.warning("⚠️ No project found with that ID.")
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")

# --- Page 2: Request New Project ---
elif page == "🆕 New Project":
    st.subheader("Request New Project ID")

    if st.button("📄 Generate New Project ID"):
        new_id = get_next_project_id()
        if new_id:
            st.session_state.new_project_id = new_id
            st.info(f"📌 Generated Project ID: `{new_id}`")

    if "new_project_id" in st.session_state:
        st.markdown(f"**Current New ID:** `{st.session_state.new_project_id}`")

        st.markdown("### 📝 Project Details")
        project_type = st.selectbox("Select Project Type", ["REDD+", "ARR", "PDD", "Other"])
        project_status = st.selectbox("Initial Status", ["Draft", "Submitted", "Approved"])

        if st.button("💾 Save to Database"):
            try:
                new_id = st.session_state.new_project_id
                data = {
                    "project_id": new_id,
                    "project_type_category": project_type,
                    "project_status": project_status
                }

                # Use the save_project function to save the project
                if save_project(data):
                    del st.session_state.new_project_id
            except Exception as e:
                st.error(f"❌ Failed to save project: {str(e)}")

# --- Page 3: Financial Modeling Demo ---
elif page == "📊 Financial Modeling":
    st.subheader("Carbon Project Financial Model Demo")

    st.markdown("""
    This interactive model demonstrates how we can analyze carbon project investments.
    Adjust the parameters below to see how they impact financial returns.
    """)

    col1, col2 = st.columns(2)

    with col1:
        area_hectares = st.slider("Project Area (hectares)", 100, 10000, 1000)
        carbon_price = st.slider("Carbon Price ($/ton)", 5, 50, 20)

    with col2:
        sequestration_rate = st.slider("Annual Sequestration Rate (tons/hectare)", 1.0, 10.0, 5.0, step=0.5)
        project_years = st.slider("Project Duration (years)", 5, 30, 10)

    # Calculate revenues
    revenues = carbon_revenue_model(area_hectares, carbon_price, sequestration_rate, project_years)
    cumulative_revenue = np.cumsum(revenues)

    # Create DataFrame for visualization
    df = pd.DataFrame({
        "Year": range(1, project_years + 1),
        "Annual Revenue ($)": revenues,
        "Cumulative Revenue ($)": cumulative_revenue
    })

    # Visualization
    fig1 = px.line(df, x="Year", y="Cumulative Revenue ($)", title="Cumulative Revenue Over Time")
    st.plotly_chart(fig1)

    fig2 = px.bar(df, x="Year", y="Annual Revenue ($)", title="Annual Revenue Projection")
    st.plotly_chart(fig2)

    # Key metrics
    total_revenue = np.sum(revenues)
    avg_annual_revenue = total_revenue / project_years

    st.markdown("### 📊 Key Financial Metrics")
    col1, col2 = st.columns(2)
    col1.metric("Total Project Revenue", f"${total_revenue:,.2f}")
    col2.metric("Average Annual Revenue", f"${avg_annual_revenue:,.2f}")

# Footer
st.markdown("---")
st.markdown("© Demo Climate Finance Analytics Platform")