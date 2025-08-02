from utils.database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class DocumentHistory(db.Model):
    __tablename__ = 'document_history'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_format = db.Column(db.String(10), nullable=False)
    operation = db.Column(db.String(10), nullable=False)  # 'mask' ou 'unmask'
    session_id = db.Column(db.String(100), nullable=True)  # Adicionado para armazenar o ID da sessão
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Adicionar a relação com o modelo User
    user = db.relationship('User', backref=db.backref('document_history', lazy=True))
    
    def __repr__(self):
        return f'<DocumentHistory {self.filename}>'