import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_sms(phone_numbers: list, message: str):
    """
    Send SMS via Africa's Talking SDK.
    phone_numbers: list of E.164 Uganda numbers, e.g. ['+256701234567']
    """
    try:
        import africastalking
        africastalking.initialize(
            username=settings.AT_USERNAME,
            api_key=settings.AT_API_KEY,
        )
        sms = africastalking.SMS
        response = sms.send(message, phone_numbers, sender_id=settings.AT_SENDER_ID)
        logger.info(f"SMS sent to {phone_numbers}: {response}")
        return response
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        return None


def send_templated_email(subject, template_name, context, recipient_list):
    """
    Send HTML + plain text email using Django templates.
    """
    try:
        html_content = render_to_string(f'email/{template_name}.html', context)
        text_content = render_to_string(f'email/{template_name}.txt', context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@medimatch.ug',
            to=recipient_list,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Email sent to {recipient_list}: {subject}")
    except Exception as e:
        logger.error(f"Email send failed: {e}")
