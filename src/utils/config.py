import os

def load_env():
    """
    Loads environment variables from .env file if it exists.
    This is useful for local development.
    """
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    # Use partition to handle values that might contain '='
                    key, _, value = line.strip().partition('=')
                    os.environ.setdefault(key, value)

def get_email_config():
    """
    Determines the environment (local vs. production) and returns the
    appropriate SMTP email configuration.
    """
    load_env()
    
    # Default to 'local' if ENVIRONMENT is not set
    environment = os.getenv('ENVIRONMENT', 'local')
    
    config = {
        'sender_email': os.getenv('SENDER_EMAIL'),
        'recipient_emails': [email.strip() for email in os.getenv('RECIPIENT_EMAILS', '').split(',')],
    }

    if environment == 'production':
        # Production uses Mailtrap/Mailgun credentials
        config.update({
            'smtp_host': os.getenv('PROD_SMTP_HOST'),
            'smtp_port': int(os.getenv('PROD_SMTP_PORT', 587)),
            'smtp_username': os.getenv('PROD_SMTP_USERNAME'),
            'smtp_password': os.getenv('PROD_SMTP_PASSWORD'),
        })
    else:
        # Local development uses MailHog
        config.update({
            'smtp_host': os.getenv('LOCAL_SMTP_HOST', 'localhost'),
            'smtp_port': int(os.getenv('LOCAL_SMTP_PORT', 1025)),
            'smtp_username': None,
            'smtp_password': None,
        })
        
    return config
