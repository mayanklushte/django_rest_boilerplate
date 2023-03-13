from .models import EmailService

def store_email_tokens(email, security_code, session_token):
    EmailService.objects.filter(email=email).delete()
    EmailService.objects.create(email=email, security_code=security_code, session_token=session_token)
