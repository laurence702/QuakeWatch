import pandas as pd
import json
import os
from datetime import datetime

def process_bronze_to_silver():
    """
    Processes raw earthquake data from the bronze layer to the silver layer.
    """
    bronze_dir = "data/bronze"
    silver_dir = "data/silver"
    archive_dir = os.path.join(bronze_dir, "archive")

    os.makedirs(silver_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Get the list of files in the bronze directory
    bronze_files = [f for f in os.listdir(bronze_dir) if f.endswith('.json')]

    for file_name in bronze_files:
        file_path = os.path.join(bronze_dir, file_name)

        with open(file_path, 'r') as f:
            data = json.load(f)

        # The earthquake data is in the 'features' list
        features = data.get('features', [])
        
        earthquake_list = []
        for feature in features:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            earthquake_list.append({
                'id': feature.get('id'),
                'magnitude': properties.get('mag'),
                'place': properties.get('place'),
                'time': pd.to_datetime(properties.get('time'), unit='ms'),
                'url': properties.get('url'),
                'tsunami': properties.get('tsunami'),
                'longitude': geometry.get('coordinates', [None, None, None])[0],
                'latitude': geometry.get('coordinates', [None, None, None])[1],
                'depth': geometry.get('coordinates', [None, None, None])[2]
            })

        if earthquake_list:
            df = pd.DataFrame(earthquake_list)
            
            # Generate a silver file name based on the bronze file name
            silver_file_name = file_name.replace('.json', '.parquet')
            silver_file_path = os.path.join(silver_dir, silver_file_name)
            
            df.to_parquet(silver_file_path, index=False)
            print(f"Successfully processed {file_name} and saved to {silver_file_path}")

            # Move the processed file to the archive
            os.rename(file_path, os.path.join(archive_dir, file_name))
            print(f"Archived {file_name}")

if __name__ == "__main__":
    process_bronze_to_silver()
