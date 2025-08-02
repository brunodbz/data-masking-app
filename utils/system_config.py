from models.system_config import SystemConfig

def get_system_config():
    config = SystemConfig.query.first()
    if not config:
        # Criar configuração padrão se não existir
        config = SystemConfig(allow_local_registration=True)
        from utils.database import db
        db.session.add(config)
        db.session.commit()
    return config

def is_local_registration_allowed():
    config = get_system_config()
    return config.allow_local_registration

def set_local_registration_allowed(allowed):
    config = get_system_config()
    config.allow_local_registration = allowed
    from utils.database import db
    db.session.commit()
    return config