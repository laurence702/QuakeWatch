import pandas as pd
import os
import json
import smtplib
from email.mime.text import MIMEText

def load_env():
    """
    Loads environment variables from .env file if it exists.
    """
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def load_email_config():
    """
    Loads email configuration from config.json and environment variables.
    """
    load_env()
    config_path = 'config.json'
    
    if not os.path.exists(config_path):
        return None
        
    with open(config_path, 'r') as f:
        config = json.load(f)

    email_config = config.get('email')
    
    if email_config:
        email_config['sender_email'] = os.getenv('MAILTRAP_USERNAME')
        email_config['sender_password'] = os.getenv('MAILTRAP_PASSWORD')
        
    return email_config

def send_email_alert(config, earthquake_details):
    """
    Sends an email alert for a significant earthquake.
    """
    if not config or not config.get('sender_email') or not config.get('sender_password'):
        print("Email configuration is incomplete. Skipping email alert.")
        return

    subject = f"Significant Earthquake Alert: Magnitude {earthquake_details['magnitude']:.2f} near {earthquake_details['place']}"
    body = f"""
    A significant earthquake has been detected:

    Magnitude: {earthquake_details['magnitude']:.2f}
    Location: {earthquake_details['place']}
    Time: {earthquake_details['time']}
    URL: {earthquake_details['url']}
    Tsunami: {'Yes' if earthquake_details['tsunami'] == 1 else 'No'}
    """
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config['sender_email']
    msg['To'] = ", ".join(config['recipient_emails'])

    try:
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.sendmail(config['sender_email'], config['recipient_emails'], msg.as_string())
        print(f"Email alert sent for earthquake {earthquake_details['id']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def analyze_and_alert():
    """
    Analyzes silver data, creates gold data, and sends alerts for significant earthquakes.
    """
    silver_dir = "data/silver"
    gold_dir = "data/gold"
    alerted_log_file = os.path.join(gold_dir, "alerted_earthquakes.log")

    os.makedirs(gold_dir, exist_ok=True)

    email_config = load_email_config()

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
                send_email_alert(email_config, alert)
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
