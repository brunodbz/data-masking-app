import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models.email_config import EmailConfig

def get_email_config():
    config = EmailConfig.query.first()
    if not config:
        return None
    return {
        'smtp_server': config.smtp_server,
        'smtp_port': config.smtp_port,
        'smtp_username': config.smtp_username,
        'smtp_password': config.smtp_password,
        'use_tls': config.use_tls,
        'from_email': config.from_email
    }

def send_email(to, subject, body, html_body=None):
    config = get_email_config()
    if not config:
        return False, "Configuração de e-mail não encontrada"
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = config['from_email']
        msg['To'] = to
        msg['Subject'] = subject
        
        # Adicionar corpo em texto plano
        msg.attach(MIMEText(body, 'plain'))
        
        # Adicionar corpo em HTML, se fornecido
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Conectar ao servidor SMTP e enviar o e-mail
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        
        if config['use_tls']:
            server.starttls()
        
        server.login(config['smtp_username'], config['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return True, "E-mail enviado com sucesso"
    except Exception as e:
        return False, f"Erro ao enviar e-mail: {str(e)}"

def send_password_reset_email(user, token):
    reset_url = f"http://localhost:5000/reset-password/{token}"
    
    subject = "Recuperação de Senha - Data Masking App"
    body = f"""
    Olá {user.username},
    
    Você solicitou a recuperação de senha para sua conta no Data Masking App.
    
    Para redefinir sua senha, clique no link abaixo:
    {reset_url}
    
    Se você não solicitou esta recuperação, ignore este e-mail.
    
    Atenciosamente,
    Equipe Data Masking App
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Recuperação de Senha - Data Masking App</h2>
        <p>Olá {user.username},</p>
        <p>Você solicitou a recuperação de senha para sua conta no Data Masking App.</p>
        <p>Para redefinir sua senha, clique no link abaixo:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Se você não solicitou esta recuperação, ignore este e-mail.</p>
        <p>Atenciosamente,<br>Equipe Data Masking App</p>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, body, html_body)

def send_document_email(user, filename, operation, session_id):
    subject = f"Documento {operation} - Data Masking App"
    body = f"""
    Olá {user.username},
    
    Um documento foi {operation} com sucesso no Data Masking App.
    
    Detalhes:
    - Nome do documento: {filename}
    - Operação: {operation}
    - ID da sessão: {session_id}
    
    Atenciosamente,
    Equipe Data Masking App
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Documento {operation} - Data Masking App</h2>
        <p>Olá {user.username},</p>
        <p>Um documento foi {operation} com sucesso no Data Masking App.</p>
        <h3>Detalhes:</h3>
        <ul>
            <li><strong>Nome do documento:</strong> {filename}</li>
            <li><strong>Operação:</strong> {operation}</li>
            <li><strong>ID da sessão:</strong> {session_id}</li>
        </ul>
        <p>Atenciosamente,<br>Equipe Data Masking App</p>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, body, html_body)