import os
import uuid
from flask import Flask, request, jsonify, send_file, redirect, url_for, session, render_template, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.database import db
from models import User, DocumentHistory, Session as SessionModel
from auth.entra_id import get_auth_url, get_token_from_code, get_user_info, login_required, get_mfa_auth_url
from auth.local_auth import local_auth
from utils.file_processor import allowed_file, process_docx, process_xlsx, process_pdf
from utils.cleanup import start_cleanup_scheduler
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db.init_app(app)

# Registrar blueprint de autenticação local
app.register_blueprint(local_auth)

# Criar diretório de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Criar as tabelas do banco de dados
with app.app_context():
    db.create_all()

# Iniciar o scheduler de limpeza
scheduler = start_cleanup_scheduler(app.config['UPLOAD_FOLDER'])

# Rotas de autenticação
@app.route('/login')
def login():
    # Verificar se o usuário já está autenticado
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('login_choice.html')

@app.route('/auth/entra-id/callback')
def entra_id_callback():
    auth_code = request.args.get('code')
    if not auth_code:
        flash('Erro: código de autorização não encontrado', 'error')
        return redirect(url_for('index'))
    
    token_result = get_token_from_code(auth_code)
    if 'error' in token_result:
        error_description = token_result.get('error_description', 'Erro desconhecido')
        
        # Verificar se o erro é relacionado a MFA
        if 'MFA' in error_description or 'strong authentication' in error_description:
            session['mfa_required'] = True
            flash('Autenticação de múltiplos fatores necessária. Por favor, tente novamente.', 'warning')
            return redirect(url_for('login'))
        
        flash(f'Erro ao obter token: {error_description}', 'error')
        return redirect(url_for('index'))
    
    user_info = get_user_info(token_result['access_token'])
    if 'error' in user_info:
        error_description = user_info.get('error_description', 'Erro desconhecido')
        flash(f'Erro ao obter informações do usuário: {error_description}', 'error')
        return redirect(url_for('index'))
    
    # Verificar se o usuário existe no banco de dados
    user = User.query.filter_by(entra_id=user_info['id']).first()
    if not user:
        # Criar novo usuário
        user = User(
            entra_id=user_info['id'],
            username=user_info.get('displayName', ''),
            email=user_info.get('mail', ''),
            is_local=False
        )
        db.session.add(user)
        db.session.commit()
    
    # Armazenar usuário na sessão
    session['user'] = {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_local': user.is_local
    }
    
    # Resetar flag de MFA
    session.pop('mfa_required', None)
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('mfa_required', None)
    session.pop('mfa_verify_user_id', None)
    session.pop('mfa_setup_user_id', None)
    flash('Você foi desconectado com sucesso', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login_choice.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if session['user']['is_admin']:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    # Buscar os últimos 10 documentos do usuário
    user_id = session['user']['id']
    history = DocumentHistory.query.filter_by(user_id=user_id)\
                                  .order_by(DocumentHistory.timestamp.desc())\
                                  .limit(10)\
                                  .all()
    
    return render_template('user_dashboard.html', history=history)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Verificar se é administrador
    if not session['user']['is_admin']:
        return redirect(url_for('user_dashboard'))
    
    # Buscar todos os usuários
    users = User.query.all()
    
    # Buscar todos os documentos (apenas metadados)
    history = DocumentHistory.query.order_by(DocumentHistory.timestamp.desc()).all()
    
    return render_template('admin_dashboard.html', users=users, history=history)

# Rotas da API
@app.route('/mask', methods=['POST'])
@login_required
def mask_data():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    mask_words = request.form.get('mask_words', '').split(',')
    mask_words = [word.strip() for word in mask_words if word.strip()]
    
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Formato de arquivo não suportado"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    session_id = str(uuid.uuid4())
    session_data = {}
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'docx':
            processed_file = process_docx(file_path, mask_words, session_data, is_masking=True)
        elif file_ext == 'xlsx':
            processed_file = process_xlsx(file_path, mask_words, session_data, is_masking=True)
        elif file_ext == 'pdf':
            processed_file = process_pdf(file_path, mask_words, session_data, is_masking=True)
        
        # Salvar sessão no banco de dados
        user_id = session['user']['id']
        db_session = SessionModel(
            session_id=session_id,
            user_id=user_id,
            original_filename=filename,
            file_format=file_ext,
            mappings=session_data
        )
        db.session.add(db_session)
        
        # Registrar no histórico
        history_record = DocumentHistory(
            user_id=user_id,
            filename=filename,
            file_format=file_ext,
            operation='mask',
            session_id=session_id  # Adicionando o ID da sessão ao histórico
        )
        db.session.add(history_record)
        db.session.commit()
        
        # Retornar arquivo processado e o ID da sessão
        response = send_file(
            processed_file,
            as_attachment=True,
            download_name=f"masked_{filename}",
            mimetype='application/octet-stream'
        )
        
        # Adicionar cabeçalho com o ID da sessão
        response.headers['X-Session-ID'] = session_id
        
        return response
    
    except Exception as e:
        return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500

@app.route('/unmask', methods=['POST'])
@login_required
def unmask_data():
    if 'file' not in request.files or 'session_id' not in request.form:
        return jsonify({"error": "Arquivo ou ID de sessão não fornecidos"}), 400
    
    file = request.files['file']
    session_id = request.form['session_id']
    
    # Buscar sessão no banco de dados
    db_session = SessionModel.query.filter_by(session_id=session_id).first()
    if not db_session:
        return jsonify({"error": "Sessão inválida ou expirada"}), 400
    
    # Verificar se o usuário tem permissão para acessar esta sessão
    if str(db_session.user_id) != session['user']['id'] and not session['user']['is_admin']:
        return jsonify({"error": "Acesso negado"}), 403
    
    session_data = db_session.mappings
    original_filename = db_session.original_filename
    file_format = db_session.file_format
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        if file_format == 'docx':
            restored_file = process_docx(file_path, [], session_data, is_masking=False)
        elif file_format == 'xlsx':
            restored_file = process_xlsx(file_path, [], session_data, is_masking=False)
        elif file_format == 'pdf':
            restored_file = process_pdf(file_path, [], session_data, is_masking=False)
        
        # Registrar no histórico
        history_record = DocumentHistory(
            user_id=db_session.user_id,
            filename=original_filename,
            file_format=file_format,
            operation='unmask',
            session_id=session_id  # Adicionando o ID da sessão ao histórico
        )
        db.session.add(history_record)
        
        # Remover sessão do banco de dados
        db.session.delete(db_session)
        db.session.commit()
        
        # Retornar arquivo restaurado
        return send_file(
            restored_file,
            as_attachment=True,
            download_name=f"restored_{original_filename}",
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        return jsonify({"error": f"Erro ao restaurar arquivo: {str(e)}"}), 500

# Rotas de administração
@app.route('/admin/promote/<user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    # Verificar se é administrador
    if not session['user']['is_admin']:
        return jsonify({"error": "Acesso negado"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    user.is_admin = True
    db.session.commit()
    
    flash(f"Usuário {user.username} promovido a administrador", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/demote/<user_id>', methods=['POST'])
@login_required
def demote_user(user_id):
    # Verificar se é administrador
    if not session['user']['is_admin']:
        return jsonify({"error": "Acesso negado"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    user.is_admin = False
    db.session.commit()
    
    flash(f"Usuário {user.username} rebaixado a usuário comum", "success")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)