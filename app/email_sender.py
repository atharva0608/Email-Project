import os
import time
import uuid
import random
from datetime import datetime
import pandas as pd
import smtplib
from email.message import EmailMessage
import ssl
from dotenv import load_dotenv
from models import db, EmailLog, SystemStats

# Load environment variables
load_dotenv()

class EmailSenderService:
    def __init__(self):
        self.email = os.getenv('SMTP_EMAIL')
        self.password = os.getenv('SMTP_PASSWORD')
        self.name = os.getenv('SENDER_NAME')
        self.resume_path = os.getenv('RESUME_PATH')
        self.min_delay = int(os.getenv('MIN_DELAY_SECONDS', 5))
        self.max_delay = int(os.getenv('MAX_DELAY_SECONDS', 10))
        self.batch_size = int(os.getenv('BATCH_SIZE', 100))
        self.batch_delay = int(os.getenv('BATCH_DELAY_SECONDS', 120))
        
    def create_email(self, to_email, hr_name, company):
        """Create personalized email message"""
        to_email = str(to_email).replace('\n', ' ').replace('\r', ' ').strip()
        hr_name = str(hr_name).replace('\n', ' ').replace('\r', ' ').strip() if hr_name else 'Recruiter'
        company = str(company).replace('\n', ' ').replace('\r', ' ').strip() if company else 'your organization'

        msg = EmailMessage()
        msg['Subject'] = f"Application for DevOps Engineer (Fresher) at {company}"
        msg['From'] = self.email
        msg['To'] = to_email

        body = f"""
        Dear {hr_name},

        I hope this message finds you well.

        I'm {self.name}, a DevOps Engineer passionate about automating cloud infrastructure and streamlining CI/CD workflows. 
        I recently completed my B.E. in Computer Engineering and bring hands-on experience in building production-ready 
        systems using AWS, Terraform, Kubernetes, Jenkins, and ArgoCD.

        During my internship at Autocal Systems, I developed reusable Terraform modules, automated multi-environment 
        EKS deployments, and implemented full-stack observability using Prometheus and Grafana—leading to a 40% increase 
        in infrastructure efficiency.

        I'm currently looking for an opportunity to contribute to a team that values cloud-native solutions, 
        infrastructure as code, and continuous delivery. I've attached my resume for your reference and would appreciate 
        the chance to discuss how I can bring value to your organization.

        Thank you for your time and consideration.

        Warm regards,
        {self.name}
        📞 +91 9767526391
        📧 {self.email}
        🔗 GitHub: https://github.com/atharva0608
        🔗 LinkedIn: https://linkedin.com/in/atharva608
        🌐 Portfolio: https://www.atharvapudaletech.xyz
        """
        msg.set_content(body)

        # Attach resume
        try:
            with open(self.resume_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='resume.pdf')
        except FileNotFoundError as e:
            raise Exception(f"Resume not found at {self.resume_path}: {str(e)}")
        
        return msg

    def process_contacts(self, excel_path):
        """Process contacts from Excel file with batch handling and delays"""
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            df.columns = df.columns.str.strip().str.title()

            # Get or create system stats
            stats = SystemStats.query.first()
            if not stats:
                stats = SystemStats()
                db.session.add(stats)

            # Generate new batch ID
            batch_id = str(uuid.uuid4())
            stats.current_batch_id = batch_id
            stats.last_batch_start = datetime.utcnow()
            db.session.commit()

            # Set up SMTP connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email, self.password)

                for index, row in df.iterrows():
                    to_email = row.get('Email') or row.get('EMAIL')
                    hr_name = row.get('Name') or row.get('NAME')
                    company = row.get('Company') or row.get('COMPANY')

                    # Skip if email already sent
                    if EmailLog.query.filter_by(recipient_email=to_email, status='sent').first():
                        continue

                    # Create log entry
                    log_entry = EmailLog(
                        recipient_email=to_email,
                        recipient_name=hr_name,
                        company=company,
                        status='pending',
                        excel_row_index=index,
                        batch_id=batch_id
                    )
                    db.session.add(log_entry)
                    db.session.commit()

                    try:
                        msg = self.create_email(to_email, hr_name, company)
                        server.send_message(msg)
                        
                        # Update log entry
                        log_entry.status = 'sent'
                        log_entry.sent_at = datetime.utcnow()
                        stats.total_sent += 1
                        
                    except Exception as e:
                        log_entry.status = 'failed'
                        log_entry.error_message = str(e)
                        stats.total_failed += 1

                    db.session.commit()

                    # Add random delay between emails
                    time.sleep(random.uniform(self.min_delay, self.max_delay))

                    # Add extra delay after batch_size emails
                    if index > 0 and index % self.batch_size == 0:
                        time.sleep(self.batch_delay)

            stats.last_excel_sync = datetime.utcnow()
            db.session.commit()
            return True

        except Exception as e:
            print(f"Error processing contacts: {str(e)}")
            return False