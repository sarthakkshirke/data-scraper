import pandas as pd
import streamlit as st
import requests
import time
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

api_key = "AIzaSyBwaVRIyDN-rfYpFj7LxVDmzS-MYKO5BUw"

# Set page config
st.set_page_config(
    page_title="Oman Business Search",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Oman Governorates and Wilayat data structure
OMAN_STRUCTURE = {
    "Muscat Governorate (محافظة مسقط)": [
        "Muscat (مسقط)", "Muttrah (مطرح)", "Bawshar (بوشر)", 
        "Seeb (السيب)", "Al Amerat (العامرات)", "Qurayyat (قريات)"
    ],
    "Dhofar Governorate (محافظة ظفار)": [
        "Salalah (صلالة)", "Taqah (طاقة)", "Mirbat (مرباط)", 
        "Sadah (سدح)", "Rakhyut (رخيوت)", "Dhalkut (ضلكوت)",
        "Thumrait (ثمريت)", "Al Mazyunah (المزيونة)", 
        "Shalim and Hallaniyat Islands (شليم وجزر الحلانيات)", "Muqshin (مقشن)"
    ],
    "Musandam Governorate (محافظة مسندم)": [
        "Khasab (خصب)", "Bukha (بخا)", "Dibba Al-Baya (دبا البيعة)", "Madha (مدحاء)"
    ],
    "Al Batinah North Governorate (محافظة شمال الباطنة)": [
        "Sohar (صحار)", "Shinas (شناص)", "Liwa (لوى)", 
        "Saham (صحم)", "Al Khaburah (الخابورة)", "Suwaiq (السويق)"
    ],
    "Al Batinah South Governorate (محافظة جنوب الباطنة)": [
        "Rustaq (الرستاق)", "Al Awabi (العوابي)", "Nakhal (نخل)", 
        "Wadi Al Maawil (وادي المعاول)", "Barka (بركاء)", "Musannah (المصنعة)"
    ],
    "Al Dhahirah Governorate (محافظة الظاهرة)": [
        "Ibri (عبري)", "Yanqul (ينقل)", "Dhank (ضنك)"
    ],
    "Al Buraimi Governorate (محافظة البريمي)": [
        "Al Buraimi (البريمي)", "Mahdah (محضة)", "Al Sunaynah (السنينة)"
    ],
    "Ad Dakhiliyah Governorate (محافظة الداخلية)": [
        "Nizwa (نزوى)", "Bahla (بهلاء)", "Manah (منح)", 
        "Al Hamra (الحمراء)", "Adam (أدم)", "Izki (إزكي)",
        "Samail (سمائل)", "Bidbid (بدبد)"
    ],
    "Ash Sharqiyah North Governorate (محافظة شمال الشرقية)": [
        "Ibra (إبراء)", "Al Mudhaibi (المضيبي)", "Bidiya (بدية)", 
        "Wadi Bani Khalid (وادي بني خالد)", "Dima Wa Al Taeen (دماء والطائيين)"
    ],
    "Ash Sharqiyah South Governorate (محافظة جنوب الشرقية)": [
        "Sur (صور)", "Jalan Bani Bu Ali (جعلان بني بو علي)", 
        "Jalan Bani Bu Hassan (جعلان بني بو حسن)", "Masirah (مصيرة)"
    ],
    "Al Wusta Governorate (محافظة الوسطى)": [
        "Haima (هيما)", "Duqm (الدقم)", "Mahout (محوت)", "Al Jazir (الجازر)"
    ]
}

# Session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

# Functions
def get_places(query, location_info, api_key):
    """Search for places using location info containing coordinates and names"""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Split location info into components
    parts = location_info.split("|")
    coordinates = parts[0]  # lat,lng
    governorate = parts[1] if len(parts) > 1 else "Unknown Governorate"
    wilayat = parts[2] if len(parts) > 2 else "Unknown Wilayat"
    
    params = {
        "query": query,
        "location": coordinates,
        "radius": 25000,
        "key": api_key
    }
    
    businesses = []
    next_page_token = None

    while True:
        if next_page_token:
            params["pagetoken"] = next_page_token
            time.sleep(2)  # Required for page tokens

        response = requests.get(url, params=params)
        data = response.json()

        for place in data.get("results", []):
            place_id = place.get("place_id")
            details = get_place_details(place_id, api_key)
            
            business_info = {
                "Name": place.get("name"),
                "Address": place.get("formatted_address"),
                "Phone Number": details.get("formatted_phone_number", "Not Available"),
                "Website": details.get("website", "Not Available"),
                "Business Status": details.get("business_status", "Unknown"),
                "Rating": float(details.get("rating")) if details.get("rating") else None,
                "Total Reviews": details.get("user_ratings_total", 0),
                "Category": ", ".join(details.get("types", [])),
                "Governorate": governorate,
                "Wilayat": wilayat,
                "LatLng": coordinates
            }
            businesses.append(business_info)

        next_page_token = data.get("next_page_token")
        if not next_page_token or len(businesses) >= 60:
            break

    return businesses

def get_place_details(place_id, api_key):
    """Get detailed information about a specific place"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id, 
        "fields": "name,formatted_address,formatted_phone_number,website,business_status,rating,user_ratings_total,types",
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json().get("result", {})

def get_city_location(wilayat_full_name, api_key):
    """Get latitude & longitude for a given wilayat and return with full location info"""
    # Extract clean wilayat name (without Arabic part if present)
    wilayat_name = wilayat_full_name.split(" (")[0].strip()
    
    # Find which governorate this wilayat belongs to
    governorate_name = None
    for gov, wilayats in OMAN_STRUCTURE.items():
        if wilayat_full_name in wilayats:
            governorate_name = gov.split(" (")[0].strip()
            break
    
    if not governorate_name:
        governorate_name = "Unknown Governorate"
    
    # Get coordinates from Google API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": f"{wilayat_name}, Oman", "key": api_key}
    
    response = requests.get(url, params=params).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        # Return format: "lat,lng|governorate_name|wilayat_name"
        return f"{location['lat']},{location['lng']}|{governorate_name}|{wilayat_name}"
    return None

def remove_duplicates(data):
    """Removes duplicate businesses based on Name & Address"""
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["Name", "Address"], keep="first", inplace=True)
    return df

def main():
    st.title("🏢 Oman Business Search")
    st.markdown("Search for businesses across Oman using Google Places API")
    
    with st.sidebar:
        
        st.session_state.api_key = api_key
        st.header("Search Settings")
        query = st.text_input("Search Query", placeholder="e.g., Cement Suppliers")
        
        # Governorate and Wilayat selection
        st.subheader("Location Selection")
        select_all_gov = st.checkbox("Select All Governorates", value=True)
        
        if select_all_gov:
            selected_governorates = list(OMAN_STRUCTURE.keys())
        else:
            selected_governorates = st.multiselect(
                "Select Governorates",
                options=list(OMAN_STRUCTURE.keys()),
                default=list(OMAN_STRUCTURE.keys())[:2]
            )
        
        # Wilayat selection
        selected_wilayat = []
        if selected_governorates:
            st.subheader("Wilayat Selection")
            select_all_wil = st.checkbox("Select All Wilayat in Selected Governorates", value=True)
            
            if select_all_wil:
                for gov in selected_governorates:
                    selected_wilayat.extend(OMAN_STRUCTURE[gov])
            else:
                for gov in selected_governorates:
                    with st.expander(f"Wilayat in {gov.split(' (')[0]}"):
                        selected = st.multiselect(
                            f"Select wilayat in {gov.split(' (')[0]}",
                            options=OMAN_STRUCTURE[gov],
                            default=OMAN_STRUCTURE[gov][:1],
                            key=f"wil_{gov}"
                        )
                        selected_wilayat.extend(selected)
        
        max_results = st.slider("Max Results per Wilayat", 10, 100, 30)
        
        if st.button("Search"):
            if not api_key:
                st.error("Please enter a valid Google Places API Key")
                return
            if not query:
                st.error("Please enter a search query")
                return
            if not selected_governorates:
                st.error("Please select at least one governorate")
                return
            if not selected_wilayat:
                st.error("Please select at least one wilayat")
                return
            
            with st.spinner("Searching for businesses..."):
                all_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, wilayat in enumerate(selected_wilayat):
                    status_text.text(f"🔍 Searching in {wilayat.split(' (')[0]}... ({i+1}/{len(selected_wilayat)})")
                    location = get_city_location(wilayat, api_key)
                    
                    if location:
                        results = get_places(query, location, api_key)
                        all_results.extend(results[:max_results])
                    
                    progress_bar.progress((i + 1) / len(selected_wilayat))
                
                if all_results:
                    df = remove_duplicates(all_results)
                    st.session_state.results_df = df
                    st.session_state.search_complete = True
                    status_text.success(f"✅ Search complete! Found {len(df)} unique businesses")
                else:
                    status_text.error("❌ No business details found.")
                    st.session_state.search_complete = False
    
    # Results Display Section
    if st.session_state.search_complete and not st.session_state.results_df.empty:
        # Initialize with full results
        filtered_df = st.session_state.results_df.copy()
        
        # Show summary stats
        st.subheader("Search Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Businesses", len(filtered_df))
        col2.metric("Governorates Covered", filtered_df['Governorate'].nunique())
        col3.metric("Wilayat Covered", filtered_df['Wilayat'].nunique())
        avg_rating = filtered_df['Rating'].mean() if not filtered_df['Rating'].isnull().all() else None
        col4.metric("Average Rating", f"{avg_rating:.1f}" if avg_rating is not None else "N/A")
        
        # Filters
        with st.expander("🔍 Filter Results"):
            col1, col2 = st.columns(2)
            with col1:
                min_rating = st.slider("Minimum Rating", 1.0, 5.0, 3.0, 0.5)
            with col2:
                selected_governorates_filter = st.multiselect(
                    "Filter by Governorate",
                    options=filtered_df['Governorate'].unique(),
                    default=filtered_df['Governorate'].unique()
                )
            
            col3, col4 = st.columns(2)
            with col3:
                selected_wilayat_filter = st.multiselect(
                    "Filter by Wilayat",
                    options=filtered_df['Wilayat'].unique(),
                    default=filtered_df['Wilayat'].unique()
                )
            with col4:
                status_filter = st.selectbox(
                    "Business Status",
                    options=["All"] + list(filtered_df['Business Status'].unique()),
                    index=0
                )
        
        # Apply filters
        filtered_df = filtered_df[filtered_df['Governorate'].isin(selected_governorates_filter)]
        filtered_df = filtered_df[filtered_df['Wilayat'].isin(selected_wilayat_filter)]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Business Status'] == status_filter]
        
        if 'Rating' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['Rating'].isna()) | 
                (filtered_df['Rating'] >= min_rating)
            ]
        
        # Display filtered results
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Website": st.column_config.LinkColumn(),
                "Rating": st.column_config.ProgressColumn(
                    format="%.1f",
                    min_value=0,
                    max_value=5
                )
            }
        )
        
        # Visualizations
        if not filtered_df.empty:
            st.subheader("Data Visualization")
            
            tab1, tab2, tab3 = st.tabs(["By Governorate", "By Wilayat", "Ratings Distribution"])
            
            with tab1:
                gov_counts = filtered_df['Governorate'].value_counts().reset_index()
                gov_counts.columns = ['Governorate', 'Count']
                st.bar_chart(gov_counts, x='Governorate', y='Count')
            
            with tab2:
                wil_counts = filtered_df['Wilayat'].value_counts().reset_index()
                wil_counts.columns = ['Wilayat', 'Count']
                st.bar_chart(wil_counts, x='Wilayat', y='Count')
            
            with tab3:
                ratings_df = filtered_df[filtered_df['Rating'].notna()]
                if not ratings_df.empty:
                    fig, ax = plt.subplots()
                    ax.hist(ratings_df['Rating'], bins=10, edgecolor='black')
                    ax.set_xlabel('Rating')
                    ax.set_ylabel('Count')
                    ax.set_title('Ratings Distribution')
                    st.pyplot(fig)
                else:
                    st.warning("No rating data available for visualization")
            
            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"oman_businesses_{timestamp}.xlsx"
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False)
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Results as Excel",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No results match your filters")

if __name__ == "__main__":
    main()
