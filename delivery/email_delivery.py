# delivery/email_delivery.py

def send_report(to: str, filepath: str):
    # integrate with SMTP or SendGrid
    print(f"📧 Emailing {filepath} to {to}")
