import requests
import pandas as pd
import time

API_KEY = "AIzaSyBwaVRIyDN-rfYpFj7LxVDmzS-MYKO5BUw"

CITIES = [
    "Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri", "Barka", "Seeb", "Rustaq", "Ibra",
    "Al Buraimi", "Khasab", "Shinas", "Adam", "Bahla", "Duqm", "Haima", "Marmul", "Mutrah"
]

def get_places(query, location):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "location": location, "radius": 25000, "key": API_KEY}  
    
    businesses = []
    next_page_token = None

    while True:
        if next_page_token:
            params["pagetoken"] = next_page_token
            time.sleep(2)  

        response = requests.get(url, params=params)
        data = response.json()

        for place in data.get("results", []):
            place_id = place.get("place_id")
            details = get_place_details(place_id)
            
            business_info = {
                "Name": place.get("name"),
                "Address": place.get("formatted_address"),
                "Phone Number": details.get("formatted_phone_number", "Not Available"),
                "Website": details.get("website", "Not Available"),
                "Business Status": details.get("business_status", "Unknown"),
                "Rating": details.get("rating", "No Rating"),
                "Total Reviews": details.get("user_ratings_total", "No Reviews"),
                "Category": ", ".join(details.get("types", [])) 
            }
            businesses.append(business_info)

        next_page_token = data.get("next_page_token")

        if not next_page_token or len(businesses) >= 60:
            break 

    return businesses

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id, 
        "fields": "name,formatted_address,formatted_phone_number,website,business_status,rating,user_ratings_total,types",
        "key": API_KEY
    }
    
    response = requests.get(url, params=params)
    return response.json().get("result", {})

def get_city_location(city):
    """Get latitude & longitude for a given city using Google Geocoding API"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city + ", Oman", "key": API_KEY}
    
    response = requests.get(url, params=params).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return f"{location['lat']},{location['lng']}"
    return None

def remove_duplicates(data):
    """Removes duplicate businesses based on Name & Address"""
    df = pd.DataFrame(data)
    df.drop_duplicates(subset=["Name", "Address"], keep="first", inplace=True)
    return df.to_dict(orient="records")

def save_to_excel(data):
    cleaned_data = remove_duplicates(data)  
    df = pd.DataFrame(cleaned_data)
    df.to_excel("business_details_oman.xlsx", index=False)
    print(f"✅ Data saved to business_details_oman.xlsx ({len(cleaned_data)} unique entries)")

if __name__ == "__main__":
    query = input("Enter your search query (e.g., Cement Suppliers): ")
    
    all_results = []
    for city in CITIES:
        print(f"🔍 Searching in {city}...")
        location = get_city_location(city)
        
        if location:
            results = get_places(query, location)
            all_results.extend(results)
        
        if len(all_results) >= 1000:  
            break  

    if all_results:
        save_to_excel(all_results)
    else:
        print("❌ No business details found.")