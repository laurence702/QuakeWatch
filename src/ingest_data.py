import requests
import json
from datetime import datetime
import os

def fetch_and_save_earthquake_data():
    """
    Fetches earthquake data from the USGS API and saves it to the bronze layer.
    """
    # The URL for the past day's earthquake data (all magnitudes)
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Create the bronze directory if it doesn't exist
        bronze_dir = "data/bronze"
        os.makedirs(bronze_dir, exist_ok=True)
        
        # Save the data to a file named with the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(bronze_dir, f"earthquake_data_{timestamp}.json")
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Successfully fetched and saved data to {file_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_and_save_earthquake_data()
