from utils.database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_format = db.Column(db.String(10), nullable=False)
    mappings = db.Column(db.JSON, nullable=False)
    
    def __repr__(self):
        return f'<Session {self.session_id}>'