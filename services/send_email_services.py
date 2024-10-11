import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from config.settings import SMTP_USERNAME, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT
from database.database import VerificationCode
from sqlalchemy.orm import Session

def verification_code_generator():
    first_digit = random.randint(1, 9)
    remaining_digits = [str(random.randint(0, 9)) for _ in range(5)]
    return str(first_digit) + "".join(remaining_digits)


def account_verification_email_body(db: Session):
    verification_code = verification_code_generator()

    db_verification_code = VerificationCode(code=verification_code)
    db.add(db_verification_code)
    db.commit()

    return (
        f"Hello Dear User!\n\n"
        f"Your verification code is: {verification_code}.\n"
        f"Please use it to complete your registration on the TaraLibrary Mobile Application.\n"
        f"Best Regards, TaraLibrary Team"
    )

def account_password_reset_email_body(db: Session, email: str) -> str:
    verification_code = verification_code_generator()
    db_verification_code = VerificationCode(code=verification_code)
    db.add(db_verification_code)
    db.commit()
    return (
        f"Hello Dear User!\n\n"
        f"Your password reset verification code is: {verification_code} for account {email}.\n"
        f"Please use it to complete your password reset on the TaraLibrary Mobile Application.\n"
        f"Best Regards, TaraLibrary Team"
    )


def send_email(receiver_email: str, subject: str, body: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, receiver_email, msg.as_string())
            return True
    except Exception as e:
        return False
