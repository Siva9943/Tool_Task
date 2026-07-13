from django.conf import settings
from core.tasks import deliver_email
from email_ops.utils.email_template import EMAIL_BUILDERS


def send_email(email_type, to, context=None, cc=None, user_id=None):
    if email_type not in EMAIL_BUILDERS:
        raise ValueError(f"Unknown email_type '{email_type}'. Valid types: {list(EMAIL_BUILDERS)}")

    to = [to] if isinstance(to, str) else list(to or [])
    cc = [cc] if isinstance(cc, str) else list(cc or [])

    if settings.SERVER_TYPE == settings.PRODUCTION:
        print(to,"this is production email")
        final_to, final_cc = to, cc
    else:
        
        final_to, final_cc = [settings.TEST_EMAIL], []
        print(final_to,"this is development email")

    deliver_email(
        email_type=email_type,
        context=context or {},
        to=final_to,
        cc=final_cc,
        user_id=user_id,
    )