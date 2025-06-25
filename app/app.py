import os
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, EmailLog, SystemStats
from email_sender import EmailSenderService
from dotenv import load_dotenv
import git

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///emails.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    # Initialize SystemStats if not exists
    if not SystemStats.query.first():
        db.session.add(SystemStats())
        db.session.commit()

def pull_from_github():
    """Pull latest changes from GitHub repository"""
    try:
        repo_path = os.getenv('GITHUB_REPO_PATH')
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()
        return True
    except Exception as e:
        print(f"Error pulling from GitHub: {str(e)}")
        return False

def process_new_contacts():
    """Background job to process contacts"""
    with app.app_context():
        # Pull latest changes from GitHub
        if pull_from_github():
            # Process contacts
            excel_path = os.path.join(os.getenv('GITHUB_REPO_PATH'), 'contacts1.xlsx')
            email_sender = EmailSenderService()
            email_sender.process_contacts(excel_path)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(process_new_contacts, 'interval', minutes=int(os.getenv('SYNC_INTERVAL_MINUTES', 30)))
scheduler.start()

@app.route('/')
def dashboard():
    """Render main dashboard"""
    stats = SystemStats.query.first()
    recent_logs = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html',
                          stats=stats,
                          recent_logs=recent_logs)

@app.route('/api/stats')
def get_stats():
    """API endpoint for dashboard statistics"""
    stats = SystemStats.query.first()
    recent_logs = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(10)
    
    return jsonify({
        'total_sent': stats.total_sent,
        'total_failed': stats.total_failed,
        'total_pending': stats.total_pending,
        'last_sync': stats.last_excel_sync.isoformat() if stats.last_excel_sync else None,
        'recent_logs': [{
            'email': log.recipient_email,
            'status': log.status,
            'timestamp': log.sent_at.isoformat() if log.sent_at else log.created_at.isoformat(),
            'company': log.company
        } for log in recent_logs]
    })

@app.route('/api/batch/<batch_id>')
def get_batch_status(batch_id):
    """API endpoint for batch progress"""
    logs = EmailLog.query.filter_by(batch_id=batch_id).all()
    total = len(logs)
    sent = sum(1 for log in logs if log.status == 'sent')
    failed = sum(1 for log in logs if log.status == 'failed')
    pending = total - sent - failed
    
    return jsonify({
        'batch_id': batch_id,
        'total': total,
        'sent': sent,
        'failed': failed,
        'pending': pending,
        'progress': (sent + failed) / total * 100 if total > 0 else 0
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))