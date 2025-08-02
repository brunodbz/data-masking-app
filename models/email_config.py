from utils.database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class EmailConfig(db.Model):
    __tablename__ = 'email_config'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password = db.Column(db.String(255), nullable=False)
    use_tls = db.Column(db.Boolean, default=True, nullable=False)
    from_email = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<EmailConfig {self.smtp_server}>'