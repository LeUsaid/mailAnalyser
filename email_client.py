import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime
from typing import List, Dict

class SimpleEmailClient:
    def __init__(self, email_address: str, password: str, imap_server: str = "imap.gmail.com"):
        """
        Simple email client for retrieving emails
        
        For Gmail: Use App Password instead of regular password
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.connection = None
    
    def connect(self):
        """Connect to email server"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server)
            self.connection.login(self.email_address, self.password)
            self.connection.select('INBOX')
            print(f"✅ Connected to {self.email_address}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def search_support_emails(self, limit: int = 10) -> List[Dict]:
        """
        Search for support-related emails
        """
        if not self.connection:
            if not self.connect():
                return []
        
        # Search for emails with support keywords
        search_criteria = '(OR (OR (OR SUBJECT "support" SUBJECT "query") SUBJECT "request") SUBJECT "help")'
        
        try:
            # Search for emails
            status, message_ids = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                print("❌ Search failed")
                return []
            
            # Get email IDs (limit to recent emails)
            email_ids = message_ids[0].split()
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            print(f"📧 Found {len(recent_ids)} support emails")
            
            for email_id in recent_ids:
                email_data = self._fetch_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error searching emails: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes) -> Dict:
        """Fetch and parse individual email"""
        try:
            # Fetch email
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract basic info
            subject = self._decode_header(email_message['Subject'])
            sender = self._decode_header(email_message['From'])
            date = email_message['Date']
            
            # Parse date
            try:
                parsed_date = email.utils.parsedate_to_datetime(date)
            except:
                parsed_date = datetime.now()
            
            # Extract body
            body = self._extract_body(email_message)
            
            # Check if it's actually a support email
            if self._is_support_email(subject, body):
                return {
                    'id': email_id.decode('utf-8'),
                    'subject': subject,
                    'sender': sender,
                    'date': parsed_date,
                    'body': body[:500] + "..." if len(body) > 500 else body,
                    'full_body': body
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching email: {e}")
            return None
    
    def _decode_header(self, header):
        """Decode email header"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_header = ""
        
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                if charset:
                    decoded_header += part.decode(charset)
                else:
                    decoded_header += part.decode('utf-8', errors='ignore')
            else:
                decoded_header += part
        
        return decoded_header.strip()
    
    def _extract_body(self, email_message):
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
                    except:
                        continue
        else:
            if email_message.get_content_type() == "text/plain":
                try:
                    body = email_message.get_payload(decode=True).decode('utf-8')
                except:
                    body = str(email_message.get_payload())
        
        return body.strip()
    
    def _is_support_email(self, subject: str, body: str) -> bool:
        """Check if email is support-related using keywords"""
        support_keywords = [
            'support', 'help', 'query', 'request', 'issue', 'problem',
            'bug', 'error', 'assistance', 'question', 'inquiry',
            'urgent', 'critical', 'cannot access', 'not working'
        ]
        
        text_content = f"{subject} {body}".lower()
        
        # Must contain at least one support keyword
        return any(keyword in text_content for keyword in support_keywords)
    
    def disconnect(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection.logout()
            print("📪 Disconnected from email server")
