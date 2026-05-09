from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from app.core.config import settings

templates = Jinja2Templates(directory="app/templates")


async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username or None,
        password=settings.mail_password.get_secret_value() or None,
        start_tls=settings.mail_use_tls,
        timeout=10,
    )

    # NOTE : debugging SMTP issues - uncomment if you need to troubleshoot email sending problems
    # try:
    #     print("📡 SMTP CONFIG:")
    #     print("HOST:", settings.mail_server)
    #     print("PORT:", settings.mail_port)
    #     print("USER:", settings.mail_username)
    #     print("TLS:", settings.mail_use_tls)

    #     response = await aiosmtplib.send(
    #         message,
    #         hostname=settings.mail_server,
    #         port=settings.mail_port,
    #         username=settings.mail_username or None,
    #         password=settings.mail_password.get_secret_value() if settings.mail_password else None,
    #         start_tls=settings.mail_use_tls,
    #     )

    #     print("✅ SMTP RESPONSE:", response)

    # except Exception as e:
    #     print("❌ SMTP ERROR:", e)


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

We received a request to reset your password for your account.

To proceed, please click the secure link below and follow the instructions:

{reset_url}

For your security, this link will expire in 30 minutes.

If you did not request a password reset, you can safely ignore this email—no changes will be made to your account.

Best regards,
Team BlogPost
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - Action Required",
        plain_text=plain_text,
        html_content=html_content,
    )
