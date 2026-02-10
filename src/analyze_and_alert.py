import pandas as pd
import os
import asyncio
from src.subscription_manager import get_all_subscribers
from src.utils.geo import haversine_distance
from src.utils.messaging import send_bulk_alerts

# Define the radius for which users will receive alerts
ALERT_RADIUS_KM = 300

async def analyze_and_alert(silver_dir="data/silver", gold_dir="data/gold"):
    """
    Analyzes silver data, creates gold data, and sends alerts to subscribed
    users for significant earthquakes within their notification radius.
    """
    alerted_log_file = os.path.join(gold_dir, "alerted_earthquakes.log")

    os.makedirs(gold_dir, exist_ok=True)

    # Load IDs of earthquakes we've already alerted on
    alerted_ids = set()
    if os.path.exists(alerted_log_file):
        with open(alerted_log_file, 'r') as f:
            alerted_ids = set(f.read().splitlines())

    # Find the latest processed data file
    silver_files = [f for f in os.listdir(silver_dir) if f.endswith('.parquet')]
    if not silver_files:
        print("No new data in the silver layer to process.")
        return

    latest_silver_file = max(silver_files, key=lambda f: os.path.getmtime(os.path.join(silver_dir, f)))
    file_path = os.path.join(silver_dir, latest_silver_file)
    
    df = pd.read_parquet(file_path)

    # Define "significant" earthquakes (e.g., magnitude >= 4.5)
    significant_earthquakes = df[df['magnitude'] >= 4.5].copy()
    
    if significant_earthquakes.empty:
        print("No significant earthquakes (>= 4.5 magnitude) found in the latest data.")
        return

    # Save significant earthquakes to the "gold" layer
    gold_file_path = os.path.join(gold_dir, latest_silver_file)
    significant_earthquakes.to_parquet(gold_file_path, index=False)
    print(f"Saved {len(significant_earthquakes)} significant earthquakes to {gold_file_path}")

    # Determine which significant earthquakes are new
    new_alerts_df = significant_earthquakes[~significant_earthquakes['id'].isin(alerted_ids)]

    if new_alerts_df.empty:
        print("No new significant earthquakes to report.")
        return

    # Get all subscribers from the database
    subscribers = get_all_subscribers()
    if not subscribers:
        print("No subscribers found in the database. Skipping alert notifications.")
        # Still log the new earthquakes as processed
        with open(alerted_log_file, 'a') as f:
            for alert_id in new_alerts_df['id'].unique():
                f.write(f"{alert_id}\n")
        return

    print(f"\n--- 🚨 Checking {len(new_alerts_df)} New Significant Earthquakes Against {len(subscribers)} Subscribers ---")
    
    notifications_to_send = []
    
    for _, alert_row in new_alerts_df.iterrows():
        print(f"  -> Analyzing: Mag {alert_row['magnitude']:.2f} near {alert_row['place']}")
        eq_lat = alert_row['latitude']
        eq_lon = alert_row['longitude']
        
        for subscriber in subscribers:
            dist = haversine_distance(eq_lat, eq_lon, subscriber['latitude'], subscriber['longitude'])
            if dist <= ALERT_RADIUS_KM:
                print(f"     ✅ Match found for {subscriber['email']} (Distance: {dist:.2f} km). Queueing alert.")
                notifications_to_send.append((subscriber['email'], alert_row.to_dict()))

    if notifications_to_send:
        print(f"\n--- Sending {len(notifications_to_send)} notifications... ---")
        await send_bulk_alerts(notifications_to_send)
        print("--------------------------------------------------\n")

    # Log the IDs of all new earthquakes we've processed, regardless of whether a notification was sent
    with open(alerted_log_file, 'a') as f:
        for alert_id in new_alerts_df['id'].unique():
            f.write(f"{alert_id}\n")
    
    if not notifications_to_send:
        print("No subscribers were within the alert radius of any new significant earthquake.")


if __name__ == "__main__":
    asyncio.run(analyze_and_alert())
