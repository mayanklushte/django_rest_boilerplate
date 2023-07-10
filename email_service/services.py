from __future__ import absolute_import
from .utils import EmailUtilities
import smtplib
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from requests.models import Response


class EmailService:
    def __init__(self, email):
        self.backend = EmailUtilities()

    def send_verification(self, email, email_template, user_name, session_token, security_code, email_subject):
        html_message, subject = self._generate_message(email, email_template, user_name, session_token, security_code, email_subject)
        try:
            send_mail(
                subject=subject,
                message="",
                from_email="Boilerplate <demo@gmail.com>",
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except smtplib.SMTPException as e:
            print("error", e)
            return Response({"status": "error", "errors": {"email": "Please check your email!"}})

    def _generate_message(self, email, email_template, user_name, session_token, security_code, email_subject):
        if email_subject == "Email Verification Link":
            verification_link = settings.FRONT_END_BASE + settings.FRONT_END_EMAIL_VERIFICATION_PATH + "?email=" + email + "&token=" + session_token
        elif email_subject == "Password Reset Link":
            verification_link = settings.FRONT_END_BASE + settings.FRONT_END_RESET_PASSWORD_PATH + "?type=email&token=" + session_token + "&value=" + email
        else:
            verification_link = None

        subject = email_subject
        params = {
            "verification_link": verification_link,
            "username": user_name,
            "verification_code": security_code,
            "frontend_base_url": settings.FRONT_END_BASE,
        }
        html_to_string = render_to_string(email_template, params)
        return html_to_string, subject


def send_email_and_generate_token(email, user_name=None, email_template=None, generate_security_code=True, email_subject=None):
    email_backend = EmailUtilities()
    security_code, session_token = email_backend.create_security_code_and_session_token(email, generate_security_code)
    service = EmailService(email)
    try:
        service.send_verification(email, email_template, user_name, session_token, security_code, email_subject)
    except Exception as exc:
        print("error", exc)
    return session_token
