import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from src.utils.config import get_email_config

def send_email_alert(config, earthquake_details):
    """
    Sends an email alert for a significant earthquake using SMTP.
    """
    if not config:
        print("Email configuration is incomplete. Skipping email alert.")
        return
    
    # Check if critical SMTP details are missing
    if not all(k in config and config[k] for k in ['smtp_host', 'smtp_port', 'sender_email', 'recipient_emails']):
        print("SMTP host, port, sender, or recipient emails are missing from config. Skipping email alert.")
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
        with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
            server.starttls()
            # Only login if username and password are provided (e.g., not needed for local MailHog)
            if config.get('smtp_username') and config.get('smtp_password'):
                server.login(config['smtp_username'], config['smtp_password'])
            server.sendmail(config['sender_email'], config['recipient_emails'], msg.as_string())
        print(f"Email alert sent for earthquake {earthquake_details['id']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def analyze_and_alert(silver_dir="data/silver", gold_dir="data/gold"):
    """
    Analyzes silver data, creates gold data, and sends alerts for significant earthquakes.
    """
    alerted_log_file = os.path.join(gold_dir, "alerted_earthquakes.log")

    os.makedirs(gold_dir, exist_ok=True)

    email_config = get_email_config()

    alerted_ids = set()
    if os.path.exists(alerted_log_file):
        with open(alerted_log_file, 'r') as f:
            alerted_ids = set(f.read().splitlines())

    silver_files = [f for f in os.listdir(silver_dir) if f.endswith('.parquet')]
    if not silver_files:
        print("No new data in the silver layer to process.")
        return

    latest_silver_file = max(silver_files, key=lambda f: os.path.getmtime(os.path.join(silver_dir, f)))
    file_path = os.path.join(silver_dir, latest_silver_file)
    
    df = pd.read_parquet(file_path)

    significant_earthquakes = df[df['magnitude'] >= 5.0].copy()
    
    if not significant_earthquakes.empty:
        gold_file_path = os.path.join(gold_dir, latest_silver_file)
        significant_earthquakes.to_parquet(gold_file_path, index=False)
        print(f"Saved significant earthquakes to {gold_file_path}")

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

            with open(alerted_log_file, 'a') as f:
                for alert in new_alerts:
                    f.write(f"{alert['id']}\n")
        else:
            print("No new significant earthquakes to report.")

    else:
        print("No significant earthquakes (>= 5.0 magnitude) found in the latest data.")


if __name__ == "__main__":
    analyze_and_alert()
