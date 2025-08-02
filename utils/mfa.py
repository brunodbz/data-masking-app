import pyotp
import qrcode
import io
import base64
from flask import current_app

def generate_mfa_secret():
    return pyotp.random_base32()

def get_mfa_qr_code(secret, username):
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(username, issuer_name="Data Masking App")
    
    img = qrcode.make(provisioning_uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"

def verify_mfa_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Permite uma janela de validação