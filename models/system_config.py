from utils.database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    allow_local_registration = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<SystemConfig allow_local_registration={self.allow_local_registration}>'