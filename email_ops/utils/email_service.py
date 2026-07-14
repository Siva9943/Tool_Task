import logging
import threading

from django.conf import settings
from core.tasks import deliver_email
from email_ops.utils.email_template import EMAIL_BUILDERS

logger = logging.getLogger("products")


def _deliver_in_background(email_type, context, to, cc, user_id):
    try:
        deliver_email(
            email_type=email_type,
            context=context,
            to=to,
            cc=cc,
            user_id=user_id,
        )
    except Exception:
        logger.exception(f"[{email_type}] email delivery failed")
    finally:
        from django.db import connection
        connection.close()


def send_email(email_type, to, context=None, cc=None, user_id=None):
    if email_type not in EMAIL_BUILDERS:
        raise ValueError(
            f"Unknown email_type '{email_type}'. Valid types: {list(EMAIL_BUILDERS.keys())}"
        )

    to = [to] if isinstance(to, str) else (to or [])
    cc = [cc] if isinstance(cc, str) else (cc or [])

    if settings.SERVER_TYPE == settings.PRODUCTION:
        final_to = list(to)
        final_cc = list(cc)
        logger.debug(f"Production email to: {final_to}")
    else:
        final_to = [settings.TEST_EMAIL]
        final_cc = []
        logger.debug(f"Development email to: {final_to}")

    threading.Thread(
        target=_deliver_in_background,
        args=(email_type, context or {}, final_to, final_cc, user_id),
        daemon=True,
    ).start()