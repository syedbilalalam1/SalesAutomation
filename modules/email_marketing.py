import csv
import os
import time
import random
from datetime import datetime
from colorama import Fore, Style
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.auth.transport.requests import Request
import re
from typing import List, Tuple
import json

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
]

def get_gmail_service(creds_filename, token_filename):
    creds = None
    
    # Check if paths are already absolute
    if os.path.isabs(creds_filename) and os.path.isabs(token_filename):
        creds_path = creds_filename
        token_path = token_filename
    else:
        # Fallback to relative path handling
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        token_path = os.path.join(root, token_filename)
        creds_path = os.path.join(root, creds_filename)
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def discover_accounts() -> List[Tuple[str, str, str]]:
    # First try in the project root
    root = _project_root()
    accounts: List[Tuple[str, str, str]] = []
    
    # Try to load accounts from both the project root and parent directory
    directories = [root]
    parent_dir = os.path.abspath(os.path.join(root, '..'))
    directories.append(parent_dir)
    
    for directory in directories:
        try:
            files = os.listdir(directory)
        except Exception:
            continue
            
        # Accept Gmail OAuth client files named either credentials_<label>.json or <email>.json
        # Exclude token_*.json and non-OAuth JSONs
        json_files = [f for f in files if f.endswith('.json') and not f.startswith('token_')]
        
        for fname in sorted(json_files):
            base = fname[:-len('.json')]
            if fname.startswith('credentials_') or ('@' in base):
                # Validate it looks like an OAuth client file
                try:
                    with open(os.path.join(directory, fname), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if not isinstance(data, dict) or ('installed' not in data and 'web' not in data):
                        continue
                except Exception:
                    continue
                label = base[len('credentials_'):] if base.startswith('credentials_') else base
                token_fname = f"token_{label}.json"
                display = label
                # Store the full path to the file
                accounts.append((os.path.join(directory, fname), os.path.join(directory, token_fname), display))
    return accounts

def partition_leads(leads_list: List[dict], num_parts: int) -> List[List[dict]]:
    if num_parts <= 0:
        return []
    base, remainder = divmod(len(leads_list), num_parts)
    parts: List[List[dict]] = []
    start = 0
    for i in range(num_parts):
        extra = 1 if i < remainder else 0
        end = start + base + extra
        parts.append(leads_list[start:end])
        start = end
    return parts

def parse_templates():
    # Look for the template file in the project root first
    template_path = os.path.join(_project_root(), 'email_template.txt')
    # If not found, try the parent directory
    if not os.path.exists(template_path):
        parent_dir = os.path.abspath(os.path.join(_project_root(), '..'))
        template_path = os.path.join(parent_dir, 'email_template.txt')
    
    with open(template_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    # Since we only have thumbnail templates now
    thumb_section = re.search(r'===THUMBNAIL===(.*)', content, re.DOTALL)
    thumb_text = thumb_section.group(1).strip() if thumb_section else ''
    def extract_templates(section_text):
        # Split by 'Subject:' but keep the delimiter
        parts = re.split(r'(?=Subject:)', section_text)
        templates = []
        for part in parts:
            lines = part.strip().splitlines()
            if not lines:
                continue
            subject = ''
            body_lines = []
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line[len('Subject:'):].strip()
                    body_lines = lines[i+1:]
                    break
            body = '\n'.join(body_lines).strip()
            if subject and body:
                templates.append((subject, body))
        return templates
    thumb_templates = extract_templates(thumb_text)
    return thumb_templates, thumb_templates  # Return the same templates for both to maintain compatibility

def run():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.LIGHTMAGENTA_EX}--- Email Marketing ---{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}Choose sending mode:")
    print(f"{Fore.LIGHTGREEN_EX}1. ALL EMAILS ROTATION (default, recommended)")
    print(f"{Fore.LIGHTGREEN_EX}2. MANUAL ACCOUNT SELECTION (send all leads with one account)")
    mode = input(f"{Fore.LIGHTYELLOW_EX}Select mode (1 or 2): ").strip()
    
    # First try in the project root directory
    leads_file = os.path.join(_project_root(), 'leads.csv')
    log_file = os.path.join(_project_root(), 'sent_emails_log.csv')
    
    # If not found, try the parent directory
    if not os.path.exists(leads_file):
        parent_dir = os.path.abspath(os.path.join(_project_root(), '..'))
        leads_file = os.path.join(parent_dir, 'leads.csv')
        log_file = os.path.join(parent_dir, 'sent_emails_log.csv')
    if not os.path.exists(leads_file):
        print(f"{Fore.RED}leads.csv not found! Please add your leads.csv in the project root.")
        input(f"{Fore.YELLOW}Press Enter to return to main menu...")
        return
    leads = []
    with open(leads_file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            normalized_row = {k.replace('\ufeff', '').replace('"', '').strip(): v for k, v in row.items() if k}
            leads.append(normalized_row)
    if not leads:
        print(f"{Fore.RED}No leads found in leads.csv!")
        input(f"{Fore.YELLOW}Press Enter to return to main menu...")
        return
    print(f"{Fore.CYAN}Loaded {len(leads)} leads.")
    thumb_templates, video_templates = parse_templates()
    if mode == '2':
        # Manual account selection
        print(f"{Fore.LIGHTCYAN_EX}Select account to use:")
        accounts = discover_accounts()
        if not accounts:
            print(f"{Fore.RED}No credentials found. Place your Google OAuth client file(s) named like credentials_<label>.json in the project root: {_project_root()}")
            input(f"{Fore.YELLOW}Press Enter to return to main menu...")
            return
        for i, (_, _, acc_name) in enumerate(accounts):
            print(f"{Fore.LIGHTGREEN_EX}{i+1}. {acc_name}")
        acc_choice = input(f"{Fore.LIGHTYELLOW_EX}Select account (1-{len(accounts)}): ").strip()
        try:
            acc_idx = int(acc_choice) - 1
            creds_file, token_file, account_name = accounts[acc_idx]
        except Exception:
            print(f"{Fore.RED}Invalid selection.")
            input(f"{Fore.YELLOW}Press Enter to return to main menu...")
            return
        print(f"{Fore.LIGHTBLUE_EX}--- Handling {len(leads)} leads with account: {account_name} ---")
        try:
            service = get_gmail_service(creds_file, token_file)
            sender_email = service.users().getProfile(userId='me').execute()['emailAddress']
        except Exception as e:
            print(f"{Fore.RED}Failed to authenticate {creds_file}: {e}")
            input(f"{Fore.YELLOW}Press Enter to return to main menu...")
            return
        
        # Use all leads for thumbnails since we don't have video editing anymore
        thumb_leads = leads
        print(f"{Fore.LIGHTCYAN_EX}Account {account_name}: {len(thumb_leads)} leads for THUMBNAIL")
        log_exists = os.path.exists(log_file)
        sent_count = 0
        with open(log_file, 'a', newline='', encoding='utf-8') as logfile:
            logwriter = csv.writer(logfile)
            if not log_exists:
                logwriter.writerow(['timestamp', 'account', 'recipient_email', 'subject', 'channel_name', 'template_type', 'lead_index', 'account_batch_index'])
            print(f"{Fore.LIGHTMAGENTA_EX}Now sending THUMBNAIL emails for account: {account_name}")
            for idx, lead in enumerate(thumb_leads):
                template_idx = idx % len(thumb_templates)
                subject, body = thumb_templates[template_idx]
                print(f"{Fore.LIGHTYELLOW_EX}[{account_name}] Sending THUMBNAIL email {idx+1}/{len(thumb_leads)} using template {template_idx+1}")
                try:
                    personalized_subject = subject.format(**lead)
                    personalized_body = body.format(**lead)
                except KeyError as e:
                    print(f"{Fore.YELLOW}Missing field {e} for lead: {lead}. Skipping.")
                    continue
                to_email = lead.get('Email') or lead.get('email')
                channel_name = lead.get('Channel_name', to_email)
                if not to_email:
                    print(f"{Fore.YELLOW}Skipping lead with missing email: {lead}")
                    continue
                message = MIMEText(personalized_body, 'html')
                message['to'] = to_email
                message['from'] = sender_email
                message['subject'] = personalized_subject
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                try:
                    service.users().messages().send(userId='me', body={'raw': raw}).execute()
                    print(f"{Fore.GREEN}Sent to {channel_name} <{to_email}> from {sender_email}")
                    logwriter.writerow([
                        datetime.now().isoformat(),
                        sender_email,
                        to_email,
                        personalized_subject,
                        channel_name,
                        'THUMBNAIL',
                        idx+1,
                        1
                    ])
                    sent_count += 1
                    wait_time = random.randint(30, 90)
                    print(f"{Fore.LIGHTYELLOW_EX}⏳ Waiting {wait_time} seconds before sending the next email...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"{Fore.RED}Failed to send to {channel_name} <{to_email}> from {sender_email}: {e}")
        print(f"{Fore.LIGHTMAGENTA_EX}\nAll emails processed.")
        input(f"{Fore.YELLOW}Press Enter to return to main menu...")
        return
    # Default: ALL EMAILS ROTATION (generalized)
    print(f"{Fore.LIGHTMAGENTA_EX}\nAuthenticating with Gmail accounts...\n")
    accounts = discover_accounts()
    if not accounts:
        print(f"{Fore.RED}No credentials found. Place your Google OAuth client file(s) named like credentials_<label>.json in the project root: {_project_root()}")
        input(f"{Fore.YELLOW}Press Enter to return to main menu...")
        return
    lead_chunks = partition_leads(leads, len(accounts))
    account_batches = []
    for i, ((creds_file, token_file, account_name)) in enumerate(accounts):
        batch_leads = lead_chunks[i] if i < len(lead_chunks) else []
        account_batches.append((batch_leads, creds_file, token_file, account_name))
    counts_str = ' | '.join([f"{acc[2]}: {len(lead_chunks[idx])} leads" for idx, acc in enumerate(accounts)])
    print(f"{Fore.LIGHTCYAN_EX}Total leads: {len(leads)} | {counts_str}")
    sent_count = 0
    log_exists = os.path.exists(log_file)
    with open(log_file, 'a', newline='', encoding='utf-8') as logfile:
        logwriter = csv.writer(logfile)
        if not log_exists:
            logwriter.writerow(['timestamp', 'account', 'recipient_email', 'subject', 'channel_name', 'template_type', 'lead_index', 'account_batch_index'])
        for batch_idx, (batch_leads, creds_file, token_file, account_name) in enumerate(account_batches):
            if not batch_leads:
                continue
            print(f"{Fore.LIGHTBLUE_EX}--- Handling {len(batch_leads)} leads with account: {account_name} ---")
            try:
                service = get_gmail_service(creds_file, token_file)
                sender_email = service.users().getProfile(userId='me').execute()['emailAddress']
            except Exception as e:
                print(f"{Fore.RED}Failed to authenticate {creds_file}: {e}")
                continue
            
            # All leads are for thumbnails
            thumb_leads = batch_leads
            print(f"{Fore.LIGHTCYAN_EX}Account {account_name}: {len(thumb_leads)} leads for THUMBNAIL")
            
            # Rotate through templates for each batch
            print(f"{Fore.LIGHTMAGENTA_EX}Now sending THUMBNAIL emails for account: {account_name}")
            for idx, lead in enumerate(thumb_leads):
                template_idx = idx % len(thumb_templates)
                subject, body = thumb_templates[template_idx]
                print(f"{Fore.LIGHTYELLOW_EX}[{account_name}] Sending THUMBNAIL email {idx+1}/{len(thumb_leads)} using template {template_idx+1}")
                try:
                    personalized_subject = subject.format(**lead)
                    personalized_body = body.format(**lead)
                except KeyError as e:
                    print(f"{Fore.YELLOW}Missing field {e} for lead: {lead}. Skipping.")
                    continue
                to_email = lead.get('Email') or lead.get('email')
                channel_name = lead.get('Channel_name', to_email)
                if not to_email:
                    print(f"{Fore.YELLOW}Skipping lead with missing email: {lead}")
                    continue
                message = MIMEText(personalized_body, 'html')
                message['to'] = to_email
                message['from'] = sender_email
                message['subject'] = personalized_subject
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                try:
                    service.users().messages().send(userId='me', body={'raw': raw}).execute()
                    print(f"{Fore.GREEN}Sent to {channel_name} <{to_email}> from {sender_email}")
                    logwriter.writerow([
                        datetime.now().isoformat(),
                        sender_email,
                        to_email,
                        personalized_subject,
                        channel_name,
                        'THUMBNAIL',
                        idx+1,
                        batch_idx+1
                    ])
                    sent_count += 1
                    wait_time = random.randint(60, 180)
                    print(f"{Fore.LIGHTYELLOW_EX}⏳ Waiting {wait_time} seconds before sending the next email...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"{Fore.RED}Failed to send to {channel_name} <{to_email}> from {sender_email}: {e}")
    print(f"{Fore.LIGHTMAGENTA_EX}\nAll emails processed.")
    input(f"{Fore.YELLOW}Press Enter to return to main menu...") 