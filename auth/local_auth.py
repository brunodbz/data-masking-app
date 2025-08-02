from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils.database import db
from models.user import User
from utils.auth import hash_password, verify_password
from utils.mfa import generate_mfa_secret, get_mfa_qr_code, verify_mfa_code
from utils.email_sender import send_password_reset_email
from utils.system_config import is_local_registration_allowed
import uuid
import secrets
from datetime import datetime, timedelta

local_auth = Blueprint('local_auth', __name__)

@local_auth.route('/register', methods=['GET', 'POST'])
def register():
    # Verificar se o registro local está permitido
    if not is_local_registration_allowed():
        flash('O registro de novas contas locais está temporariamente desativado.', 'warning')
        return redirect(url_for('local_auth.login'))
    
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
        
        # Verificar se é o primeiro usuário local
        is_first_user = User.query.filter_by(is_local=True).count() == 0
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_local=True,
            mfa_secret=generate_mfa_secret(),
            is_admin=is_first_user,  # O primeiro usuário é administrador
            is_approved=is_first_user  # O primeiro usuário já é aprovado
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Armazenar ID do usuário na sessão para configuração do MFA
        session['mfa_setup_user_id'] = str(user.id)
        
        # Se for o primeiro usuário, informar que ele é administrador
        if is_first_user:
            flash('Você é o primeiro usuário local e foi definido como administrador!', 'success')
        
        return redirect(url_for('local_auth.setup_mfa'))
    
    return render_template('register.html')

# O resto do arquivo permanece igual...
    
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
            
            flash('MFA configurado com sucesso!', 'success')
            
            # Se o usuário já estiver aprovado, redirecionar para o login
            if user.is_approved:
                return redirect(url_for('local_auth.login'))
            else:
                flash('Sua conta foi criada, mas precisa ser aprovada por um administrador.', 'info')
                return redirect(url_for('local_auth.login'))
        else:
            flash('Código inválido. Tente novamente.', 'error')
    
    # Gerar QR Code para o MFA
    qr_code = get_mfa_qr_code(user.mfa_secret, user.username)
    
    return render_template('setup_mfa.html', qr_code=qr_code, username=user.username, mfa_secret=user.mfa_secret)

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
        
        if not user.is_approved:
            flash('Sua conta ainda não foi aprovada por um administrador.', 'warning')
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

@local_auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('E-mail é obrigatório', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email, is_local=True).first()
        
        if not user:
            flash('Se não existir uma conta com este e-mail, você não receberá um e-mail.', 'info')
            return render_template('forgot_password.html')
        
        # Gerar token de recuperação de senha
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token válido por 1 hora
        
        db.session.commit()
        
        # Enviar e-mail de recuperação
        success, message = send_password_reset_email(user, token)
        
        if success:
            flash('Um e-mail de recuperação foi enviado para o seu endereço de e-mail.', 'success')
        else:
            flash(f'Erro ao enviar e-mail de recuperação: {message}', 'error')
        
        return redirect(url_for('local_auth.login'))
    
    return render_template('forgot_password.html')

@local_auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or user.password_reset_expires < datetime.utcnow():
        flash('Token de recuperação inválido ou expirado.', 'error')
        return redirect(url_for('local_auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('reset_password.html', token=token)
        
        # Atualizar senha
        user.password_hash = hash_password(password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        db.session.commit()
        
        flash('Senha redefinida com sucesso! Você já pode fazer login.', 'success')
        return redirect(url_for('local_auth.login'))
    
    return render_template('reset_password.html', token=token)