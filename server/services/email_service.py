import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ENV переменные
SMTP_USER = os.getenv("SMTP_USER", "ats.sidoryk@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

# Базовая проверка конфигурации
if not all([SMTP_USER, SMTP_PASS]):
    raise ValueError("❌ SMTP credentials are not properly configured")

def send_email_notification(to: str, subject: str, body: str):
    """Простое письмо в формате text/plain"""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            print(f"📨 Email sent to {to}: {subject}")
    except Exception as e:
        print(f"❌ Email error to {to}: {e}")

def send_signal_notification(to_email: str, ticker: str, action: str, price: float):
    subject = f"Trading Signal: {action.upper()} {ticker}"
    body = f"""\
A new trading signal has been generated:

Ticker: {ticker}
Action: {action.upper()}
Price: ${price:.2f}

You can review this signal in your trading dashboard.
"""
    send_email_notification(to_email, subject, body)

def send_order_filled_notification(to_email: str, ticker: str, price: float, quantity: int):
    subject = f"Order Filled: {ticker}"
    body = f"""\
Your order has been filled successfully:

Ticker: {ticker}
Quantity: {quantity}
Price: ${price:.2f}

You can review it in your dashboard.
"""
    send_email_notification(to_email, subject, body)

def send_error_notification(to_email: str, error_message: str):
    subject = "❌ Error during trade execution"
    body = f"""\
An error occurred during trading:

{error_message}

Please check your strategies or broker status.
"""
    send_email_notification(to_email, subject, body)