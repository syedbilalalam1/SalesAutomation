# SALES AUTOMATION

## First Look: CLI Interface
![CLI Screenshot](SALES AUTOMATION/img/demo.JPG)

<img src="SALES AUTOMATION/img/demo.JPG" alt="CLI Screenshot" width="500"/>

---

**This project is PURELY FOR EDUCATIONAL PURPOSES.**

---

## Overview
This project automates outreach and marketing tasks across multiple channels using Python. It is designed to handle as many Gmail accounts as you want. Emails are sent in batches, with built-in delays to avoid rate limits and prevent emails from going to spam. The system is modular, supporting Email Marketing, Facebook Marketplace, LinkedIn Outreach, and Twitter DMs.

**Emails sent using this system are designed to avoid spam filters.**

You can use as many Gmail accounts as you want. For each account, you must obtain your own Gmail API credentials (JSON file) from the Google Cloud Console. The first time you use an account, the system will create a token for authentication.

**Again, this project is for educational purposes only. Do not use it for unsolicited or commercial outreach.**

## Features
- Multi-account support (handles 12+ Gmail accounts)
- Automated email sending with randomized delays
- Modular design for different marketing channels
- Lead management via CSV files
- Logging of sent emails
- Customizable email templates
- Sorting system for leads (use your own or the provided one)

## Folder Structure
```
SALES AUTOMATION/
├── leads.csv                # List of leads for outreach
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
├── sent_emails_log.csv      # Log of sent emails
├── modules/
│   ├── email_marketing.py   # Email automation logic
│   ├── facebook_marketplace.py
│   ├── linkedin_outreach.py
│   ├── twitter_dms.py
│   └── __pycache__/
├── *.json                   # Gmail OAuth credentials (one per account)
├── email_template.txt       # Email template (customize as needed)
```

## Getting Started
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Gmail accounts:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project, and enable the Gmail API.
   - Create OAuth credentials and download the JSON file for each Gmail account you want to use.
   - Place your Gmail OAuth credential JSON files in the project root. Each file should be named after the account (e.g., `your_email@gmail.com.json`).
   - The first time you run the script with a new account, it will create a token for authentication.
4. **Prepare your leads:**
   - Add your leads to `leads.csv`.
5. **Customize your email template:**
   - Edit `email_template.txt` or create your own template file.
6. **Sorting system:**
   - You can use the provided sorting system for dividing leads among accounts, or implement your own.
7. **Run the automation:**
   ```bash
   python main.py
   ```

## Customization
- **Email Template:**
   - Create your own template or use the provided `email_template.txt`.
- **Lead Sorting:**
   - Use the built-in system to divide leads among accounts, or implement your own logic.

## License
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
