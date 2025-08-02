import os
import sys
from flask import Flask
from utils.database import db
from sqlalchemy import text

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Criar uma aplicação Flask mínima para executar as migrações
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@"
    f"{os.environ.get('POSTGRES_HOST', 'db')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}/"
    f"{os.environ.get('POSTGRES_DB', 'masking_app')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def run_migrations():
    with app.app_context():
        # Verificar se as colunas já existem
        inspector = db.engine.dialect.inspector(db.engine)
        columns = [column['name'] for column in inspector.get_columns('users')]
        
        # Adicionar coluna is_approved se não existir
        if 'is_approved' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE'))
            print("Coluna 'is_approved' adicionada com sucesso!")
        
        # Adicionar coluna password_reset_token se não existir
        if 'password_reset_token' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255)'))
            print("Coluna 'password_reset_token' adicionada com sucesso!")
        
        # Adicionar coluna password_reset_expires se não existir
        if 'password_reset_expires' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN password_reset_expires TIMESTAMP'))
            print("Coluna 'password_reset_expires' adicionada com sucesso!")
        
        # Criar tabela email_config se não existir
        table_names = inspector.get_table_names()
        if 'email_config' not in table_names:
            db.session.execute(text('''
                CREATE TABLE email_config (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    smtp_server VARCHAR(255) NOT NULL,
                    smtp_port INTEGER NOT NULL,
                    smtp_username VARCHAR(255) NOT NULL,
                    smtp_password VARCHAR(255) NOT NULL,
                    use_tls BOOLEAN DEFAULT TRUE,
                    from_email VARCHAR(255) NOT NULL
                )
            '''))
            print("Tabela 'email_config' criada com sucesso!")
        
        # Criar tabela system_config se não existir
        if 'system_config' not in table_names:
            db.session.execute(text('''
                CREATE TABLE system_config (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    allow_local_registration BOOLEAN DEFAULT TRUE NOT NULL
                )
            '''))
            # Inserir configuração padrão
            db.session.execute(text('''
                INSERT INTO system_config (id, allow_local_registration)
                VALUES (gen_random_uuid(), TRUE)
            '''))
            print("Tabela 'system_config' criada com sucesso!")
        
        db.session.commit()
        print("Migrações concluídas com sucesso!")

if __name__ == '__main__':
    run_migrations()