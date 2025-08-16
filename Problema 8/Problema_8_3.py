from celery.exceptions import Retry
from flask import current_app, render_template
from flask_mail import Message
from celery_app import celery
from extensions import mail

@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_jitter=True, max_retries=5)
def send_email_task(self, subject: str, recipient: str, template_name: str, context: dict):
    """
    Envía correo usando Flask-Mail. Usa plantillas Jinja2 para el cuerpo HTML.
    - autoretry_for: reintenta automáticamente ante excepciones (p. ej., fallo SMTP)
    - retry_backoff: backoff exponencial (5s, 10s, 20s, ...)
    """
    try:
        # current_app está disponible si la tarea se ejecuta con app_context
        html_body = render_template(template_name, **(context or {}))
        msg = Message(subject=subject, recipients=[recipient], html=html_body)
        mail.send(msg)
        return {"status": "ok"}
    except Exception as exc:
        raise Retry(exc=exc)