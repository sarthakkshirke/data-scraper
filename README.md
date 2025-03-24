# 📍 Google Places Business Scraper  
**Extract business details from Google Places API and save them to Excel.**  

## 🚀 Features  
- ✅ Extracts **business names, addresses, phone numbers, websites, ratings, and categories**  
- ✅ **Supports dynamic queries** (e.g., *Cement Suppliers in Oman*)  
- ✅ **Fetches up to 1000 businesses** per query using multiple cities  
- ✅ **Removes duplicate entries** before saving  
- ✅ **Saves data to an Excel file (`.xlsx`)**  

---

## 📦 Installation  
### 1️⃣ Clone the repository  
```bash
git clone https://github.com/sarthakkshirke/google-places-scraper.git
cd google-places-scraper
```

### 2️⃣ Create a virtual environment (optional but recommended)  
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3️⃣ Install dependencies  
```bash
pip install -r requirements.txt
```

---

## 🔑 Google Places API Setup  
### 1️⃣ Get API Key  
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).  
2. Create a new project & enable the **Places API** and **Geocoding API**.  
3. Generate an **API Key** under "Credentials".  
4. Replace `"YOUR_GOOGLE_PLACES_API_KEY"` in `app.py` with your actual API key.  

---

## 🏗️ Usage  
### Run the script  
```bash
python app.py
```
- 🔹 **Enter your search query** (e.g., *"Cement Suppliers in Oman"*)  
- 🔹 The script will automatically collect business data and save it to **`business_details_oman.xlsx`**  

---

## 📊 Sample Output (Excel)  
| Name                | Address          | Phone Number  | Website                 | Rating | Category          |  
|---------------------|-----------------|--------------|-------------------------|--------|------------------|  
| Oman Cement Co.    | Muscat, Oman     | +968 1234 5678 | www.omancement.com     | 4.5    | Hardware Store, Supplier |  
| Salalah Cement     | Salalah, Oman    | +968 9876 5432 | Not Available          | 4.3    | Building Materials |  

---

## ⚙️ Configuration  
### Modify Search Locations  
Edit the `CITIES` list in `app.py` to expand the search coverage:  
```python
CITIES = ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri"]
```

### Adjust Search Radius  
Change `radius=25000` (in meters) to **increase/decrease** the area per search:  
```python
params = {"query": query, "location": location, "radius": 25000, "key": API_KEY}
```

---

## 🛠️ Troubleshooting  
### ❌ `"REQUEST_DENIED"`  
- Ensure your **Google Places API Key** is correct and enabled for **Places API** and **Geocoding API**.  

### ❌ `"Over Query Limit"`  
- Google has a **daily free limit of 1000 requests**. Upgrade your API usage if needed.  

---

## 📝 License  
📜 **MIT License** – Feel free to modify and use this project.  

---

## ⭐ Contribute  
- Fork the repo & submit a pull request  
- Report issues & suggest improvements  

💡 **If this project helped you, don’t forget to ⭐ star the repository!**  

---

### 🎯 **Happy Scraping! 🚀**  

