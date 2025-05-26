import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = 'ats.sidoryk@gmail.com'
APP_PASSWORD = 'nipq smkg gfjr wmvo'

msg = EmailMessage()
msg['Subject'] = 'SMTP Test'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'alexeisidorik@gmail.com'
msg.set_content('Если ты это читаешь — значит SMTP работает!')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
    smtp.send_message(msg)

print("✅ Email отправлен!")