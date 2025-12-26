
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8001")

st.set_page_config(
    page_title="Brand Intelligence Dashboard",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Brand Intelligence Dashboard")
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Brand Discovery", "Signals Feed", "Content Feed", "Create Brand", "Create Signal"]
)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Brands", "0", "Loading...")
    with col2:
        st.metric("Recent Signals", "0", "Loading...")
    with col3:
        st.metric("Content Items", "0", "Loading...")
    
    st.subheader("Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ API Status: {data['status']}")
            st.write(f"Service: {data['service']}")
        else:
            st.error("❌ API is down")
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")


# ============================================================================
# BRAND DISCOVERY PAGE
# ============================================================================
elif page == "Brand Discovery":
    st.header("🔍 Brand Discovery")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_name = st.text_input("Search by brand name")
        industry = st.selectbox("Industry", ["", "Tech", "Fashion", "Beauty", "Food", "Other"])
    
    with col2:
        market = st.selectbox("Market/Region", ["", "US", "EU", "Asia", "Global"])
        tier = st.selectbox("Tier", ["", "Luxury", "Premium", "Standard"])
    
    if st.button("Search Brands"):
        try:
            params = {
                "limit": 20,
                "offset": 0
            }
            if search_name:
                params["search"] = search_name
            if industry:
                params["industry"] = industry
            if market:
                params["market"] = market
            if tier:
                params["tier"] = tier
            
            response = requests.get(f"{API_BASE_URL}/v1/brands", params=params)
            
            if response.status_code == 200:
                data = response.json()
                brands = data.get("data", [])
                
                if brands:
                    df = pd.DataFrame(brands)
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Found {data['meta']['total']} brands")
                else:
                    st.warning("No brands found")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")


# ============================================================================
# SIGNALS FEED PAGE
# ============================================================================
elif page == "Signals Feed":
    st.header("📡 Intelligence Signals Feed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        signal_type = st.selectbox(
            "Signal Type",
            ["", "launch", "style_shift", "overperformance", "underperformance"]
        )
    
    with col2:
        brand_id = st.text_input("Filter by Brand ID (optional)")
    
    if st.button("Get Signals"):
        try:
            params = {
                "limit": 20,
                "offset": 0
            }
            if signal_type:
                params["signal_type"] = signal_type
            if brand_id:
                params["brand_id"] = brand_id
            
            response = requests.get(f"{API_BASE_URL}/v1/signals", params=params)
            
            if response.status_code == 200:
                data = response.json()
                signals = data.get("data", [])
                
                if signals:
                    for signal in signals:
                        with st.container():
                            st.subheader(f"📌 {signal.get('signal_type', 'Unknown')}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Confidence", f"{signal.get('confidence', 0):.2%}")
                            col2.write(f"**Brand ID:** {signal.get('brand_id')}")
                            col3.write(f"**Detected:** {signal.get('detected_at')}")
                            if signal.get('reason'):
                                st.write(f"**Reason:** {signal.get('reason')}")
                            st.divider()
                else:
                    st.warning("No signals found")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")


# ============================================================================
# CONTENT FEED PAGE
# ============================================================================
elif page == "Content Feed":
    st.header("📸 Content Feed")
    
    brand_id = st.text_input("Enter Brand ID")
    
    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Platform", ["", "instagram", "tiktok", "twitter"])
    with col2:
        content_type = st.selectbox("Content Type", ["", "post", "reel", "video", "story"])
    
    if st.button("Get Content"):
        try:
            if not brand_id:
                st.warning("Please enter a Brand ID")
            else:
                params = {
                    "limit": 20,
                    "offset": 0
                }
                if platform:
                    params["platform"] = platform
                if content_type:
                    params["content_type"] = content_type
                
                response = requests.get(
                    f"{API_BASE_URL}/v1/brands/{brand_id}/content",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("data", [])
                    
                    if content:
                        for item in content:
                            with st.container():
                                st.subheader(f"📱 {item.get('platform', 'Unknown').upper()}")
                                col1, col2 = st.columns(2)
                                col1.write(f"**Type:** {item.get('content_type')}")
                                col2.write(f"**Created:** {item.get('created_at')}")
                                st.write(f"**URL:** {item.get('url')}")
                                if item.get('caption'):
                                    st.write(f"**Caption:** {item.get('caption')[:200]}...")
                                st.divider()
                    else:
                        st.warning("No content found")
                else:
                    st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}")


# ============================================================================
# CREATE BRAND PAGE
# ============================================================================
elif page == "Create Brand":
    st.header("➕ Create New Brand")
    
    with st.form("create_brand_form"):
        name = st.text_input("Brand Name *")
        logo_url = st.text_input("Logo URL")
        industry = st.text_input("Industry")
        market = st.text_input("Market/Region")
        tier = st.selectbox("Tier", ["", "Luxury", "Premium", "Standard"])
        aesthetic = st.multiselect("Aesthetic Tags", ["Minimalist", "Bold", "Playful", "Elegant", "Modern"])
        
        submit = st.form_submit_button("Create Brand")
        
        if submit:
            if not name:
                st.error("Brand name is required")
            else:
                try:
                    payload = {
                        "name": name,
                        "logo_url": logo_url or None,
                        "industry": industry or None,
                        "market": market or None,
                        "tier": tier or None,
                        "aesthetic": aesthetic or None
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/v1/brands", json=payload)
                    
                    if response.status_code == 201:
                        brand = response.json()
                        st.success(f"✅ Brand created successfully!")
                        st.json(brand)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")


# ============================================================================
# CREATE SIGNAL PAGE
# ============================================================================
elif page == "Create Signal":
    st.header("➕ Create New Signal")
    
    with st.form("create_signal_form"):
        brand_id = st.text_input("Brand ID *")
        signal_type = st.selectbox(
            "Signal Type *",
            ["launch", "style_shift", "overperformance", "underperformance", "collaboration"]
        )
        confidence = st.slider("Confidence", 0.0, 1.0, 0.5)
        reason = st.text_area("Reason (optional)")
        
        submit = st.form_submit_button("Create Signal")
        
        if submit:
            if not brand_id or not signal_type:
                st.error("Brand ID and Signal Type are required")
            else:
                try:
                    payload = {
                        "brand_id": brand_id,
                        "signal_type": signal_type,
                        "confidence": confidence,
                        "reason": reason or None,
                        "detected_at": datetime.now().isoformat()
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/v1/signals", json=payload)
                    
                    if response.status_code == 201:
                        signal = response.json()
                        st.success(f"✅ Signal created successfully!")
                        st.json(signal)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")