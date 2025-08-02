from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils.database import db, User
from utils.auth import hash_password, verify_password
from utils.mfa import generate_mfa_secret, get_mfa_qr_code, verify_mfa_code
import uuid

local_auth = Blueprint('local_auth', __name__)

@local_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validação básica
        if not username or not email or not password:
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('register.html')
        
        # Verificar se o usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('E-mail já está em uso', 'error')
            return render_template('register.html')
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_local=True,
            mfa_secret=generate_mfa_secret()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Armazenar ID do usuário na sessão para configuração do MFA
        session['mfa_setup_user_id'] = str(user.id)
        
        return redirect(url_for('local_auth.setup_mfa'))
    
    return render_template('register.html')

@local_auth.route('/setup-mfa', methods=['GET', 'POST'])
def setup_mfa():
    user_id = session.get('mfa_setup_user_id')
    if not user_id:
        return redirect(url_for('local_auth.register'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('local_auth.register'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        
        if verify_mfa_code(user.mfa_secret, code):
            user.mfa_enabled = True
            db.session.commit()
            
            # Limpar sessão temporária
            session.pop('mfa_setup_user_id', None)
            
            flash('MFA configurado com sucesso! Você já pode fazer login.', 'success')
            return redirect(url_for('local_auth.login'))
        else:
            flash('Código inválido. Tente novamente.', 'error')
    
    # Gerar QR Code para o MFA
    qr_code = get_mfa_qr_code(user.mfa_secret, user.username)
    
    return render_template('setup_mfa.html', qr_code=qr_code, username=user.username)

@local_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Nome de usuário e senha são obrigatórios', 'error')
            return render_template('local_login.html')
        
        user = User.query.filter_by(username=username, is_local=True).first()
        
        if not user or not verify_password(user.password_hash, password):
            flash('Nome de usuário ou senha inválidos', 'error')
            return render_template('local_login.html')
        
        if not user.mfa_enabled:
            flash('MFA não está habilitado para este usuário', 'error')
            return render_template('local_login.html')
        
        # Armazenar ID do usuário na sessão para verificação do MFA
        session['mfa_verify_user_id'] = str(user.id)
        
        return redirect(url_for('local_auth.verify_mfa'))
    
    return render_template('local_login.html')

@local_auth.route('/verify-mfa', methods=['GET', 'POST'])
def verify_mfa():
    user_id = session.get('mfa_verify_user_id')
    if not user_id:
        return redirect(url_for('local_auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('local_auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        
        if verify_mfa_code(user.mfa_secret, code):
            # Armazenar usuário na sessão
            session['user'] = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_local': user.is_local
            }
            
            # Limpar sessão temporária
            session.pop('mfa_verify_user_id', None)
            
            return redirect(url_for('dashboard'))
        else:
            flash('Código inválido. Tente novamente.', 'error')
    
    return render_template('verify_mfa.html', username=user.username)