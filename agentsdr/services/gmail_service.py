"""
Gmail API service for fetching and processing emails
"""
import os
import base64
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import openai
from flask import current_app


class GmailService:
    def __init__(self):
        self.client_id = os.getenv('GMAIL_CLIENT_ID')
        self.client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def get_access_token(self, refresh_token: str) -> str:
        """Get a fresh access token using refresh token"""
        try:
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
            token_json = response.json()
            
            if 'error' in token_json:
                raise Exception(f"Token refresh failed: {token_json['error']}")
            
            return token_json['access_token']
            
        except Exception as e:
            current_app.logger.error(f"Error refreshing access token: {e}")
            raise
    
    def build_gmail_service(self, refresh_token: str):
        """Build Gmail API service with fresh credentials"""
        try:
            access_token = self.get_access_token(refresh_token)
            
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri='https://oauth2.googleapis.com/token'
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            return service
            
        except Exception as e:
            current_app.logger.error(f"Error building Gmail service: {e}")
            raise
    
    def get_query_for_criteria(self, criteria_type: str, count: int = 10) -> str:
        """Build Gmail search query based on criteria"""
        if criteria_type == 'last_24_hours':
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            return f'after:{yesterday}'
        elif criteria_type == 'last_7_days':
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
            return f'after:{week_ago}'
        elif criteria_type in ['latest_n', 'oldest_n']:
            return 'in:inbox'  # We'll handle sorting in the API call
        else:
            return 'in:inbox'
    
    def fetch_emails(self, refresh_token: str, criteria_type: str, count: int = 10) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail based on criteria"""
        try:
            service = self.build_gmail_service(refresh_token)
            query = self.get_query_for_criteria(criteria_type, count)
            
            # Get message IDs
            if criteria_type == 'oldest_n':
                # For oldest emails, we need to search differently
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=count
                ).execute()
            else:
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=count
                ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full message details
            emails = []
            for message in messages:
                try:
                    msg = service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self.parse_email(msg)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    current_app.logger.error(f"Error fetching message {message['id']}: {e}")
                    continue
            
            # Sort emails based on criteria
            if criteria_type == 'oldest_n':
                emails.sort(key=lambda x: x['timestamp'])
            else:
                emails.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return emails[:count]
            
        except Exception as e:
            current_app.logger.error(f"Error fetching emails: {e}")
            raise
    
    def parse_email(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured data"""
        try:
            headers = message['payload'].get('headers', [])
            
            # Extract headers
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse date
            timestamp = datetime.now()
            try:
                from email.utils import parsedate_to_datetime
                timestamp = parsedate_to_datetime(date_str)
            except:
                pass
            
            # Extract body
            body = self.extract_body(message['payload'])
            
            # Clean sender name (remove email part if present)
            sender_name = sender
            if '<' in sender and '>' in sender:
                sender_name = sender.split('<')[0].strip().strip('"')
            elif '@' in sender:
                sender_name = sender.split('@')[0]
            
            return {
                'id': message['id'],
                'sender': sender_name,
                'sender_email': sender,
                'subject': subject,
                'body': body,
                'timestamp': timestamp,
                'date': timestamp.strftime('%Y-%m-%d %H:%M')
            }
            
        except Exception as e:
            current_app.logger.error(f"Error parsing email: {e}")
            return None
    
    def extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        body = self.html_to_text(html_body)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload['mimeType'] == 'text/html':
                data = payload['body'].get('data', '')
                if data:
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                    body = self.html_to_text(html_body)
        
        return self.clean_email_body(body)
    
    def html_to_text(self, html: str) -> str:
        """Convert HTML to plain text"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except ImportError:
            # Fallback: simple regex-based HTML removal
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html)
    
    def clean_email_body(self, body: str) -> str:
        """Clean email body by removing signatures, footers, etc."""
        if not body:
            return ""
        
        # Remove common signature patterns
        signature_patterns = [
            r'\n--\s*\n.*',  # Standard signature delimiter
            r'\nBest regards.*',
            r'\nSincerely.*',
            r'\nThanks.*\n.*@.*',
            r'\nSent from my.*',
            r'\n\[.*\].*',  # Email client footers
        ]
        
        cleaned = body
        for pattern in signature_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        # Limit length for summarization
        if len(cleaned) > 2000:
            cleaned = cleaned[:2000] + "..."
        
        return cleaned
    
    def summarize_with_openai(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize emails using OpenAI API"""
        try:
            summaries = []
            
            # Group emails by topic/sender for better summarization
            grouped_emails = self.group_emails_by_topic(emails)
            
            for group in grouped_emails:
                try:
                    if len(group) == 1:
                        # Single email summary
                        email = group[0]
                        summary_text = self.summarize_single_email(email)
                    else:
                        # Multiple emails on same topic
                        summary_text = self.summarize_email_group(group)
                        email = group[0]  # Use first email for metadata
                    
                    summaries.append({
                        'id': email['id'],
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'date': email['date'],
                        'summary': summary_text,
                        'email_count': len(group)
                    })
                    
                except Exception as e:
                    current_app.logger.error(f"Error summarizing email group: {e}")
                    # Add fallback summary
                    email = group[0]
                    summaries.append({
                        'id': email['id'],
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'date': email['date'],
                        'summary': f"Email from {email['sender']} about {email['subject']}",
                        'email_count': len(group)
                    })
            
            return summaries
            
        except Exception as e:
            current_app.logger.error(f"Error in OpenAI summarization: {e}")
            raise
    
    def group_emails_by_topic(self, emails: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group emails by similar topics/senders"""
        # Simple grouping by sender and subject similarity
        groups = []
        processed = set()
        
        for i, email in enumerate(emails):
            if i in processed:
                continue
            
            group = [email]
            processed.add(i)
            
            # Look for similar emails
            for j, other_email in enumerate(emails[i+1:], i+1):
                if j in processed:
                    continue
                
                # Group by same sender or similar subject
                if (email['sender'] == other_email['sender'] or 
                    self.subjects_similar(email['subject'], other_email['subject'])):
                    group.append(other_email)
                    processed.add(j)
            
            groups.append(group)
        
        return groups
    
    def subjects_similar(self, subject1: str, subject2: str) -> bool:
        """Check if two subjects are similar (simple implementation)"""
        # Remove common prefixes
        clean1 = re.sub(r'^(re:|fwd?:)\s*', '', subject1.lower()).strip()
        clean2 = re.sub(r'^(re:|fwd?:)\s*', '', subject2.lower()).strip()
        
        return clean1 == clean2
    
    def summarize_single_email(self, email: Dict[str, Any]) -> str:
        """Summarize a single email using OpenAI"""
        try:
            prompt = f"""
            Please summarize this email in 1-3 concise sentences. Focus on the main purpose and any action items.

            From: {email['sender']}
            Subject: {email['subject']}

            Email content:
            {email['body']}

            Summary:
            """

            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes emails concisely and clearly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            current_app.logger.error(f"Error in single email summarization: {e}")
            return f"Email from {email['sender']} regarding {email['subject']}"
    
    def summarize_email_group(self, emails: List[Dict[str, Any]]) -> str:
        """Summarize a group of related emails"""
        try:
            email_contents = []
            for email in emails:
                email_contents.append(f"From: {email['sender']}\nSubject: {email['subject']}\nContent: {email['body'][:500]}...")

            combined_content = "\n\n---\n\n".join(email_contents)

            prompt = f"""
            Please summarize this email thread in 2-4 sentences. Focus on the main topic and key developments.

            Email thread:
            {combined_content}

            Summary:
            """

            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes email threads concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            if len(emails) > 1:
                summary += f" (Thread of {len(emails)} emails)"

            return summary

        except Exception as e:
            current_app.logger.error(f"Error in group email summarization: {e}")
            return f"Email thread with {len(emails)} messages about {emails[0]['subject']}"


def fetch_and_summarize_emails(refresh_token: str, criteria_type: str, count: int = 10) -> List[Dict[str, Any]]:
    """Main function to fetch and summarize emails"""
    try:
        gmail_service = GmailService()
        
        # Fetch emails
        emails = gmail_service.fetch_emails(refresh_token, criteria_type, count)
        
        if not emails:
            return []
        
        # Summarize emails
        summaries = gmail_service.summarize_with_openai(emails)
        
        return summaries
        
    except Exception as e:
        current_app.logger.error(f"Error in fetch_and_summarize_emails: {e}")
        raise
