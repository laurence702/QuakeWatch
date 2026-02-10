import asyncio

class EmailService:
    """
    A mock email service for sending alerts.
    
    In a real application, this class would be replaced with a service
    that sends emails using a provider like SendGrid or AWS SES.
    The `send_alert` method is async to simulate a non-blocking network call.
    """
    
    async def send_alert(self, email: str, earthquake_details: dict):
        """
        Simulates sending an earthquake alert email.
        """
        message = (
            f"--- MOCK EMAIL ---"
            f"\nTo: {email}"
            f"\nSubject: Earthquake Alert!"
            f"\n\nA significant earthquake has occurred near your subscribed location."
            f"\nDetails:"
            f"\n  Place: {earthquake_details.get('place')}"
            f"\n  Magnitude: {earthquake_details.get('magnitude')}"
            f"\n  Time: {earthquake_details.get('time')}"
            f"\n------------------"
        )
        print(message)
        # In a real I/O operation, we would have an `await` call here.
        # We add a small sleep to simulate a non-blocking network call.
        await asyncio.sleep(0.01)

async def send_bulk_alerts(alerts: list[tuple[str, dict]]):
    """
    Sends multiple alerts concurrently.
    
    Args:
        alerts: A list of tuples, where each tuple contains
                (email, earthquake_details_dict).
    """
    email_service = EmailService()
    tasks = [email_service.send_alert(email, details) for email, details in alerts]
    await asyncio.gather(*tasks)
