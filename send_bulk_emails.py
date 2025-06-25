import pandas as pd
import smtplib
from email.message import EmailMessage
import ssl
import os

# Debug: Show current directory files
print("📄 Current directory files:", os.listdir())
print("🚀 Script started...")

# Configuration
YOUR_NAME = "Atharva Pudale"
YOUR_EMAIL = "hire.atharvapudale@gmail.com"
YOUR_APP_PASSWORD = "oqnq crlb krbm hlvk"  # Replace with your Gmail App Password
RESUME_PATH = r"Atharva-Pudale-7972533419.pdf"  # Make sure this path matches your actual resume filename

def create_email(to_email, hr_name, company):
    # Sanitize all header values (to avoid newline issues in SMTP headers)
    to_email = str(to_email).replace('\n', ' ').replace('\r', ' ').strip()
    hr_name = str(hr_name).replace('\n', ' ').replace('\r', ' ').strip() if hr_name else 'Recruiter'
    company = str(company).replace('\n', ' ').replace('\r', ' ').strip() if company else 'your organization'

    msg = EmailMessage()
    msg['Subject'] = f"Application for DevOps Engineer (Fresher) at {company}"
    msg['From'] = YOUR_EMAIL
    msg['To'] = to_email

    body = f"""
Dear {hr_name},

I hope this message finds you well.

I'm Atharva Pudale, a DevOps Engineer passionate about automating cloud infrastructure and streamlining CI/CD workflows. I recently completed my B.E. in Computer Engineering and bring hands-on experience in building production-ready systems using AWS, Terraform, Kubernetes, Jenkins, and ArgoCD.

During my internship at Autocal Systems, I developed reusable Terraform modules, automated multi-environment EKS deployments, and implemented full-stack observability using Prometheus and Grafana—leading to a 40% increase in infrastructure efficiency.

I'm currently looking for an opportunity to contribute to a team that values cloud-native solutions, infrastructure as code, and continuous delivery. I’ve attached my resume for your reference and would appreciate the chance to discuss how I can bring value to your organization.

Thank you for your time and consideration.

Warm regards,  
Atharva Pudale  
📞 +91 9767526391  
📧 hire.atharvapudale@gmail.com  
🔗 GitHub: https://github.com/atharva0608  
🔗 LinkedIn: https://linkedin.com/in/atharva608  
🌐 Portfolio: https://www.atharvapudaletech.xyz
"""
    msg.set_content(body)

    # Attach resume
    try:
        with open(RESUME_PATH, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='resume.pdf')
        print(f"📎 Attached resume from: {RESUME_PATH}")
    except FileNotFoundError:
        print(f"❌ Resume file not found at: {RESUME_PATH}")
    
    return msg

def send_emails():
    try:
        df = pd.read_excel("contacts1.xlsx")
        df.columns = df.columns.str.strip().str.title()  # Normalize column names like 'Email', 'Name', 'Company'
        print("✅ Excel loaded:", df.shape)
    except Exception as e:
        print(f"❌ Failed to read contacts1.xlsx: {e}")
        return

    # Ask user for start and end row range
    try:
        start = input("Enter the start row index (default = 0): ").strip()
        end = input("Enter the end row index (default = end of file): ").strip()

        start = int(start) if start else 0
        end = int(end) if end else len(df)

        df = df.iloc[start:end]
        print(f"📨 Sending emails from row {start} to {end - 1} ({len(df)} total).")
    except ValueError:
        print("❌ Invalid input. Sending to all emails.")
        df = df

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            print("🔐 Logged into SMTP server successfully.")

            for index, row in df.iterrows():
                to_email = row.get('Email') or row.get('EMAIL')
                hr_name = row.get('Name') or row.get('NAME')
                company = row.get('Company') or row.get('COMPANY')

                # Sanitize header fields
                to_email = str(to_email).replace('\n', ' ').replace('\r', ' ').strip()
                hr_name = str(hr_name).replace('\n', ' ').replace('\r', ' ').strip() if hr_name else ''
                company = str(company).replace('\n', ' ').replace('\r', ' ').strip() if company else ''

                print(f"📧 Preparing email for: {to_email}, Name: {hr_name}, Company: {company}")

                if not to_email:
                    print(f"⚠️ Skipping row {index} — missing email.")
                    continue

                msg = create_email(to_email, hr_name, company)
                try:
                    server.send_message(msg)
                    print(f"✅ Email sent to {to_email}")
                except Exception as e:
                    print(f"❌ Failed to send email to {to_email}: {e}")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")

if __name__ == "__main__":
    send_emails()
