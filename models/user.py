from utils.database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entra_id = db.Column(db.String(100), unique=True, nullable=True)  # Tornar nullable para usuários locais
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Para usuários locais
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_local = db.Column(db.Boolean, default=False, nullable=False)  # Indica se é usuário local
    mfa_secret = db.Column(db.String(32), nullable=True)  # Segredo para MFA
    mfa_enabled = db.Column(db.Boolean, default=False, nullable=False)  # Se MFA está habilitado
    
    def __repr__(self):
        return f'<User {self.username}>'