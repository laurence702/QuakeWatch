import pandas as pd
import os

def analyze_and_alert():
    """
    Analyzes silver data, creates gold data, and sends alerts for significant earthquakes.
    """
    silver_dir = "data/silver"
    gold_dir = "data/gold"
    alerted_log_file = os.path.join(gold_dir, "alerted_earthquakes.log")

    os.makedirs(gold_dir, exist_ok=True)

    # --- Load already alerted earthquakes ---
    alerted_ids = set()
    if os.path.exists(alerted_log_file):
        with open(alerted_log_file, 'r') as f:
            alerted_ids = set(f.read().splitlines())

    # --- Process Silver Data ---
    silver_files = [f for f in os.listdir(silver_dir) if f.endswith('.parquet')]
    if not silver_files:
        print("No new data in the silver layer to process.")
        return

    latest_silver_file = max(silver_files, key=lambda f: os.path.getmtime(os.path.join(silver_dir, f)))
    file_path = os.path.join(silver_dir, latest_silver_file)
    
    df = pd.read_parquet(file_path)

    # --- Create Gold Data (Significant Earthquakes) ---
    significant_earthquakes = df[df['magnitude'] >= 5.0].copy()
    
    if not significant_earthquakes.empty:
        gold_file_path = os.path.join(gold_dir, latest_silver_file)
        significant_earthquakes.to_parquet(gold_file_path, index=False)
        print(f"Saved significant earthquakes to {gold_file_path}")

        # --- Alerting ---
        new_alerts = []
        for index, row in significant_earthquakes.iterrows():
            if row['id'] not in alerted_ids:
                new_alerts.append(row)
                alerted_ids.add(row['id'])

        if new_alerts:
            print("\n--- 🚨 New Significant Earthquake Alerts! ---")
            for alert in new_alerts:
                print(f"  -> Magnitude {alert['magnitude']:.2f} earthquake near {alert['place']}")
                print(f"     Time: {alert['time']}")
                print(f"     Details: {alert['url']}")
            print("--------------------------------------------\n")

            # --- Update alerted log ---
            with open(alerted_log_file, 'a') as f:
                for alert in new_alerts:
                    f.write(f"{alert['id']}\n")
        else:
            print("No new significant earthquakes to report.")

    else:
        print("No significant earthquakes (>= 5.0 magnitude) found in the latest data.")


if __name__ == "__main__":
    analyze_and_alert()
