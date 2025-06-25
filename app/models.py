from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmailLog(db.Model):
    """Model for tracking email sending status"""
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    recipient_name = db.Column(db.String(255))
    company = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False)  # 'sent', 'failed', 'pending'
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    excel_row_index = db.Column(db.Integer)
    batch_id = db.Column(db.String(36))  # UUID for grouping emails in batches

    def __repr__(self):
        return f'<EmailLog {self.recipient_email} - {self.status}>'

class SystemStats(db.Model):
    """Model for tracking system-wide statistics"""
    id = db.Column(db.Integer, primary_key=True)
    total_sent = db.Column(db.Integer, default=0)
    total_failed = db.Column(db.Integer, default=0)
    total_pending = db.Column(db.Integer, default=0)
    last_excel_sync = db.Column(db.DateTime)
    last_batch_start = db.Column(db.DateTime)
    current_batch_id = db.Column(db.String(36))
    
    def __repr__(self):
        return f'<SystemStats sent={self.total_sent} failed={self.total_failed}>'