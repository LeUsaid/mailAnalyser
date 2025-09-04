from email_client import SimpleEmailClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_retrieval():
    """Test email retrieval functionality"""
    
    # Replace with your email credentials
    # For Gmail, use App Password: https://support.google.com/accounts/answer/185833
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'your_email@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
    
    if EMAIL_ADDRESS == 'your_email@gmail.com':
        print("⚠️  Please set your EMAIL_ADDRESS and EMAIL_PASSWORD in .env file")
        print("For Gmail: Use App Password instead of regular password")
        return
    
    # Create email client
    client = SimpleEmailClient(EMAIL_ADDRESS, EMAIL_PASSWORD)
    
    # Search for support emails
    print("🔍 Searching for support emails...")
    support_emails = client.search_support_emails(limit=5)
    
    if support_emails:
        print(f"\n📧 Found {len(support_emails)} support emails:")
        print("-" * 80)
        
        for i, email_data in enumerate(support_emails, 1):
            print(f"{i}. Subject: {email_data['subject']}")
            print(f"   From: {email_data['sender']}")
            print(f"   Date: {email_data['date']}")
            print(f"   Body preview: {email_data['body'][:100]}...")
            print("-" * 80)
    else:
        print("📭 No support emails found")
    
    # Clean up
    client.disconnect()

if __name__ == "__main__":
    test_email_retrieval()
